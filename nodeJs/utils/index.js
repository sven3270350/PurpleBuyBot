const queries = require("../db/queries");
const appConfig = require("./app_config");
const UniswapV2Pair = require("./IUniswapV2Pair.json");
const ERC20 = require("./erc20abi.json");
const Web3 = require("web3");
const CoinGecko = require("coingecko-api");
const CoinGeckoClient = new CoinGecko();
const TelegramBot = require("node-telegram-bot-api");

const bot = new TelegramBot(process.env.PUBLIC_BOT_API_KEY);

const wss = (provider) => new Web3(provider);

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

const swapHanlder = async (contract, trackedToken, data, callback) => {
  const tx_hash = data.transactionHash;
  const token_address = trackedToken.token_address.toLowerCase();
  const decimals = trackedToken.token_decimals;
  const chainId = trackedToken.chain_id;
  const explorer = appConfig.getExploerUrl(chainId);
  const tx_link = `${explorer}tx/${tx_hash}`;

  try {
    const selectedTrackedToken = await selectTrackedToken(
      token_address,
      contract
    );

    let amountIn = 0;
    let amountOut = 0;

    if (selectedTrackedToken.token === 1) {
      const token1Decimals = await getTokenDecimals(
        trackedToken.paired_with,
        chainId
      );

      amountOut = Web3.utils.fromWei(
        data.returnValues.amount1In,
        decimalsToUnit(token1Decimals)
      );

      amountIn = Web3.utils.fromWei(
        data.returnValues.amount0Out,
        decimalsToUnit(decimals)
      );
    } else {
      const token0Decimals = await getTokenDecimals(
        trackedToken.paired_with,
        chainId
      );

      amountOut = Web3.utils.fromWei(
        data.returnValues.amount0Out,
        decimalsToUnit(decimals)
      );

      amountIn = Web3.utils.fromWei(
        data.returnValues.amount1In,
        decimalsToUnit(token0Decimals)
      );
    }

    const to = data.returnValues.to;

    if (amountIn > 0 || amountOut > 0) {
      callback(trackedToken, amountIn, amountOut, to, tx_link);
    }
  } catch (error) {
    console.log("[Utils::swapHanlder]", error);
  }
};

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

    const price = cachedPrices[pairs[id]].usd;
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
  // send max 29 messages per second per group
  setTimeout(() => {
    bot
      .sendMessage(groupId, messageTemplate, {
        parse_mode: "HTML",
        disable_web_page_preview: true,
      })
      .catch((error) => {
        console.log("[Utils::sendHTMLMessage]", { ...error.toJSON(), groupId });
      });
  }, 2000);
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
};
