const queries = require("../db/queries");
const appConfig = require("./app_config");
const UniswapV2Pair = require("./IUniswapV2Pair.json");
const ERC20 = require("./erc20abi.json");
const Web3 = require("web3");
const Web3WsProvider = require("web3-providers-ws");
const CoinGecko = require("coingecko-api");
const CoinGeckoClient = new CoinGecko();
const TelegramBot = require("node-telegram-bot-api");

const bot = new TelegramBot(process.env.PUBLIC_BOT_API_KEY);

const wss = (provider) => {
  const options = {
    timeout: 30000,

    clientConfig: {
      keepalive: true,
      keepaliveInterval: 60000,
    },

    reconnect: {
      auto: true,
      delay: 5000, // ms
      maxAttempts: 10,
      onTimeout: false,
    },
  };

  const ws = new Web3WsProvider(provider, options);

  return new Web3(ws);
};

const selectTrackedToken = async (trackedToken, contract) => {
  try {
    const token0 = await getToken0(contract);
    const token1 = await getToken1(contract);

    if (trackedToken.toLowerCase() === token0) {
      return { token: 0, address: token0 };
    } else {
      return { token: 1, address: token1 };
    }
  } catch (error) {
    console.log("[Utils::selectTrackedToken]", error);
  }
};

const getToken0 = async (contract) => {
  const token0 = await contract.methods.token0().call();
  return token0.toLowerCase();
};

const getToken1 = async (contract) => {
  const token1 = await contract.methods.token1().call();
  return token1.toLowerCase();
};

const hasActiveSubscription = async (groupId) => {
  try {
    const activeSubscription = await queries.getActiveSubscriptionByGroupId(
      groupId
    );
    return activeSubscription.length > 0;
  } catch (error) {
    console.log("[Utils::hasActiveSubscription]", error);
  }
};

const getTokenDecimals = async (address, chain) => {
  const web3 = wss(appConfig.getProvider(chain));
  const token = new web3.eth.Contract(ERC20, address);
  return token.methods.decimals().call();
};

const getTokenTotalSupply = async (tokenAddress, chainId) => {
  const web3 = wss(appConfig.getProvider(chainId));
  const token = new web3.eth.Contract(ERC20, tokenAddress);
  return token.methods.totalSupply().call();
};

const getBuyerLink = (address, chainId) => {
  const explorer = appConfig.getExploerUrl(chainId);
  return `${explorer}address/${address}`;
};

const getBuyerBalance = async (address, token, chainId) => {
  const web3 = wss(appConfig.getProvider(chainId));
  const tokenContract = new web3.eth.Contract(ERC20, token);
  return tokenContract.methods.balanceOf(address).call();
};

const isNewBuyer = async (address, token, decimals, amountOut, chainId) => {
  const balance = await getBuyerBalance(address, token, chainId);
  const readableBalance = convertFromWei(balance, decimals);
  return {
    newBuyer: readableBalance <= amountOut,
    percentageIncrease: getPercentageIncrease(
      readableBalance - amountOut,
      readableBalance
    ),
  };
};

const convertFromWei = (amount, decimals) => {
  return new Web3.utils.BN(amount) / 10 ** decimals;
};

const getPercentageIncrease = (oldValue, newValue) => {
  return ((newValue - oldValue) / oldValue) * 1;
};

const getChart = (chainId, pairAddress) => {
  const chart = appConfig.getDexChartUrl(chainId);
  return `${chart}${pairAddress}`;
};

const swapHanlder = async (contract, trackedToken, data, callback) => {
  const tx_hash = data.transactionHash;
  const token_address = trackedToken.token_address.toLowerCase();
  const decimals = trackedToken.token_decimals;
  const chainId = trackedToken.chain_id;
  const explorer = appConfig.getExploerUrl(chainId);
  const tx_link = `${explorer}tx/${tx_hash}`;

  try {
    if (!trackedToken.circulating_supply) {
      await setCirculatingSupply(trackedToken);
    }

    const selectedTrackedToken = await selectTrackedToken(
      token_address,
      contract
    );

    let amountIn = 0;
    let amountOut = 0;

    if (selectedTrackedToken.token === 1) {
      const { group_id, token_name, chain_name } = trackedToken;
      console.log(
        "UTILS::swapHanlder::token1",
        {
          group_id,
          token_name,
          chain_name,
        },
        data.returnValues
      );
      const token1Decimals = await getTokenDecimals(
        trackedToken.paired_with,
        chainId
      );

      amountOut = convertFromWei(data.returnValues.amount1Out, decimals);
      amountIn = convertFromWei(data.returnValues.amount0In, token1Decimals);
    } else {
      const token0Decimals = await getTokenDecimals(
        trackedToken.paired_with,
        chainId
      );

      amountOut = convertFromWei(data.returnValues.amount0Out, decimals);

      amountIn = convertFromWei(data.returnValues.amount1In, token0Decimals);
    }

    const to = data.returnValues.to;
    const price = await getUsdPrice(amountIn, trackedToken.paired_with_name);

    if ((amountIn > 0 || amountOut > 0) && price.usdNumber > 1) {
      let marketCap = 0;

      if (trackedToken.circulating_supply) {
        const unitPrice = amountOut / amountIn;
        marketCap = unitPrice * trackedToken.circulating_supply;
      }

      callback(
        trackedToken,
        amountIn,
        amountOut,
        marketCap,
        price,
        to,
        tx_link
      );
    }
  } catch (error) {
    const { group_id, token_name, chain_name } = trackedToken;
    console.log(
      "[Utils::swapHanlder]",
      {
        group_id,
        token_name,
        chain_name,
      },
      error
    );
  }
};

const setCirculatingSupply = async (trackedToken) => {
  try {
    const { id, token_address, token_decimals, chain_id, group_id } =
      trackedToken;
    const totalSupply = await getTokenTotalSupply(token_address, chain_id);
    const circulatingSupply = convertFromWei(totalSupply, token_decimals);
    await queries.updateTrackedTokenCircSupply(group_id, id, circulatingSupply);
  } catch (error) {
    console.log("[Utils::setCirculatingSupply]", error);
  }
};

// const getUnitPrice = async (trackedToken) => {
//   const getAmountsOutAbi = [
//     {
//       inputs: [
//         { internalType: "uint256", name: "amountIn", type: "uint256" },
//         { internalType: "address[]", name: "path", type: "address[]" },
//       ],
//       name: "getAmountsOut",
//       outputs: [
//         { internalType: "uint256[]", name: "amounts", type: "uint256[]" },
//       ],
//       stateMutability: "view",
//       type: "function",
//     },
//   ];
//   try {
//     const {
//       token_address,
//       token_decimals,
//       chain_id,
//       router_address,
//       paired_with,
//     } = trackedToken;

//     const web3 = wss(appConfig.getProvider(chain_id));
//     const router = new web3.eth.Contract(
//       getAmountsOutAbi,
//       router_address.toLowerCase()
//     );

//     const amountIn = 1 * 10 ** token_decimals; // 1 token
//     const amountsOut = await router.methods
//       .getAmountsOut(amountIn, [
//         token_address.toLowerCase(),
//         paired_with.toLowerCase(),
//       ])
//       .call();
//     return amountsOut[1];
//   } catch (error) {
//     console.log("[Utils::getUnitPrice]", error);
//   }
// };

const keyInObject = (key, obj) => {
  const length = Object.keys(obj).length;
  if (length === 0) return false;
  return !!obj.hasOwnProperty(key);
};

const decimalsToUnit = (decimals) => {
  const units = {
    1: "wei",
    3: "kwei",
    6: "mwei",
    9: "gwei",
    12: "szabo",
    15: "finney",
    18: "ether",
    21: "kether",
    24: "mether",
    27: "gether",
    30: "tether",
  };
  return units[Number(decimals)];
};

const ellipseAddress = (address) => {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

const getUsdPrice = async (amount, paired_with) => {
  const price = await getUsdPriceFromCache(paired_with);
  return {
    usdString: numberToUsd(Number(amount) * price),
    usdNumber: Number(amount) * price,
  };
};

const getUSDPrices = async () => {
  const ids = appConfig.getAllCoingeckoIds();
  try {
    const { data } = await CoinGeckoClient.simple.price({
      ids: Object.values(ids),
      vs_currencies: "usd",
    });
    return data;
  } catch (error) {
    console.log("[Utils::getUsdPrices]", error);
    return {};
  }
};

let prices = {};
const cachePrices = async (interval = 1000 * 15) => {
  return (async () => {
    if (Object.keys(prices).length === 0) {
      try {
        prices = await getUSDPrices();
        setInterval(async () => {
          prices = await getUSDPrices();
        }, interval);
      } catch (error) {
        console.log("[allBuys::cachePrices]", error);
      }
    }
    return prices;
  })();
};

const getUsdPriceFromCache = async (paired_with) => {
  const id = paired_with.toLowerCase();
  const pairs = {
    eth: "ethereum",
    bnb: "binancecoin",
    cro: "crypto-com-chain",
    usdt: "tether",
    busd: "binance-usd",
    usdc: "usd-coin",
  };

  try {
    const cachedPrices = await cachePrices();
    // console.log("UTILS::getUsdPriceFromCache::cachedPrices", cachedPrices);

    const price = cachedPrices[pairs[id]]?.usd;
    return price;
  } catch (error) {
    console.log("[Utils::getUsdPriceFromCache]", error);
    return 0;
  }
};

const numberToUsd = (amount) => {
  return Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

const sendHTMLMessage = async (groupId, messageTemplate) => {
  const { buy_media } = await getGroupMedia(groupId);
  // send max 29 messages per second per group
  setTimeout(async () => {
    if (buy_media?.type === "animation") {
      await sendAnimationWithCaption(
        groupId,
        buy_media.file_id,
        messageTemplate
      );
    } else if (buy_media?.type === "photo") {
      await sendPhotoWithCaption(groupId, buy_media.file_id, messageTemplate);
    } else {
      bot
        .sendMessage(groupId, messageTemplate, {
          parse_mode: "HTML",
          disable_web_page_preview: true,
        })
        .catch((error) => {
          handleSendError(error, groupId);
        });
    }
  }, 2000);
};

const sendAnimationWithCaption = async (groupId, animation, caption) => {
  bot
    .sendAnimation(groupId, animation, {
      parse_mode: "HTML",
      disable_web_page_preview: true,
      caption: caption,
    })
    .catch((error) => {
      handleSendError(error, groupId);
    });
};

const sendPhotoWithCaption = async (groupId, photo, caption) => {
  bot
    .sendPhoto(groupId, photo, {
      parse_mode: "HTML",
      disable_web_page_preview: true,
      caption: caption,
    })
    .catch((error) => {
      handleSendError(error, groupId);
    });
};

const getCountdown = (date) => {
  const now = new Date();
  const diff = date.getTime() - now.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor(diff / (1000 * 60 * 60)) % 24;
  const minutes = Math.floor(diff / (1000 * 60)) % 60;
  const seconds = Math.floor(diff / 1000) % 60;
  return { days, hours, minutes, seconds };
};

const getCountdownString = (date) => {
  const { days, hours, minutes, seconds } = getCountdown(date);
  let countdownString = "";
  if (days > 0) {
    countdownString += `${days}d `;
  }
  if (hours > 0) {
    countdownString += `${hours}h `;
  }
  if (minutes > 0) {
    countdownString += `${minutes}m `;
  }
  if (seconds > 0) {
    countdownString += `${seconds}s `;
  }
  return countdownString;
};

const getAd = async (groupId) => {
  let ad = "";
  try {
    const isSubscriber = await hasActiveSubscription(groupId);

    if (!isSubscriber) {
      const ads = await queries.getActiveAd();
      ad = ads[0].advert;
    }
  } catch (error) {
    console.log("[Utils::getAd]", error);
  }
  return ad;
};

const rankIcon = (rank) => {
  switch (rank) {
    case 1:
      return "🥇";
    case 2:
      return "🥈";
    case 3:
      return "🥉";
    case 4:
      return "4️⃣";
    case 5:
      return "5️⃣";
    default:
      return "😎";
  }
};

const genFormatter3dec = new Intl.NumberFormat("en-US", {
  notation: "standard",
  maximumFractionDigits: 3,
});

const amountFormater = (value) => {
  if (Number.parseFloat(value) > 0.001) {
    return genFormatter3dec.format(value);
  } else {
    return Number.parseFloat(value).toExponential(2);
  }
};

const percentageFormatter = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 2,
});

const getGroupMedia = async (groupId) => {
  let { buy_icon, buy_media } = await queries.getGroupIconAndMedia(groupId);
  buy_media = buy_media ? JSON.parse(buy_media) : "";
  return { buy_icon, buy_media };
};

const handleSendError = (error, groupId) => {
  const errorJson = error.toJSON();
  if (
    errorJson.message.includes("bot was blocked") ||
    errorJson.message.includes("bot was kicked") ||
    errorJson.message.includes("group chat was upgraded")
  ) {
    queries
      .deleteTrackedToken(groupId)
      .then(() => console.log("[Utils::handleSendError]", "Tracking disabled"));

    queries
      .stopGroupActiveCampaign(groupId)
      .then(() => console.log("[Utils::handleSendError]", "Campaign stopped"));
  }

  console.log("[Utils::sendHTMLMessage]", {
    ...error.toJSON(),
    groupId,
  });
};

module.exports = {
  ...appConfig,
  selectTrackedToken,
  getToken0,
  getToken1,
  hasActiveSubscription,
  keyInObject,
  swapHanlder,
  UniswapV2Pair,
  wss,
  fromWei: Web3.utils.fromWei,
  decimalsToUnit,
  getUsdPrice,
  sendHTMLMessage,
  getCountdown,
  getCountdownString,
  getAd,
  ellipseAddress,
  numberToUsd,
  rankIcon,
  getUSDPrices,
  cachePrices,
  getUsdPriceFromCache,
  amountFormater,
  getBuyerLink,
  isNewBuyer,
  getBuyerBalance,
  getChart,
  convertFromWei,
  getGroupMedia,
  percentageFormatter,
};
