const queries = require("../db/queries");
const appConfig = require("./app_config");
const UniswapV2Pair = require("./IUniswapV2Pair.json");
const ERC20 = require("./erc20abi.json");
const Web3 = require("web3");
const Web3WsProvider = require("web3-providers-ws");
const TelegramBot = require("node-telegram-bot-api");
const TrendingQueue = require("./trending_queue");
const CoingeckoService = require("../services/coingecko");

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

const getGroupInviteLink = async (groupId) => {
  const groupInfo = await bot.getChat(groupId);
  // groupInfo.permissions.can_pin_messages
  // bot.pinChatMessage(groupInfo.id, nessageId);
  // bot.editMessageText(text, {
  //   chat_id: groupInfo.id,
  //   message_id: messageId,
  //   parse_mode: "HTML",
  // });
  const { group_link } = await queries.getGroupInviteLink(groupId);
  const invite_link = groupInfo.invite_link;
  const user_name = groupInfo.username;

  return group_link
    ? group_link
    : invite_link
    ? invite_link
    : user_name
    ? `https://t.me/${user_name}`
    : "";
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
  const { min_usd_amount } = await queries.getMinUSDBuyAmount(
    trackedToken.group_id
  );
  const explorer = appConfig.getExploerUrl(chainId);
  const tx_link = `${explorer}tx/${tx_hash}`;
  const { circulating_supply } = await queries.getTokenCircSupply(
    trackedToken.id
  );

  try {
    if (!circulating_supply) {
      await setCirculatingSupply(trackedToken);
    }

    const selectedTrackedToken = await selectTrackedToken(
      token_address,
      contract
    );

    let amountIn = 2;
    let amountOut = 2;

    // const pairedTokenDecimals = await getTokenDecimals(
    //   trackedToken.paired_with,
    //   chainId
    // );

    // if (Number(data.returnValues.amount0In) > 0) {
    //   amountOut = convertFromWei(data.returnValues.amount1Out, decimals);
    //   amountIn = convertFromWei(data.returnValues.amount0In, pairedTokenDecimals);
    // } else {
    //   amountOut = convertFromWei(data.returnValues.amount0Out, decimals);
    //   amountIn = convertFromWei(data.returnValues.amount1In, pairedTokenDecimals);
    // }

    // if (selectedTrackedToken.token === 1) {
    //   console.log("---------step amount----------", selectedTrackedToken.token, data.returnValues)

    //   const token1Decimals = await getTokenDecimals(
    //     trackedToken.paired_with,
    //     chainId
    //   );
    //   console.log('before token 1 decimal')
    //   amountOut = convertFromWei(data.returnValues.amount1Out, decimals);
    //   amountIn = convertFromWei(data.returnValues.amount0In, token1Decimals);
    //   console.log("------token 1 Decimal-------", token1Decimals)
    // } else {
    //   console.log("---------step amount----------", selectedTrackedToken.token, data.returnValues)

    //   const token0Decimals = await getTokenDecimals(
    //     trackedToken.paired_with,
    //     chainId
    //   );

    //   console.log('before token 0 decimal')
    //   amountOut = convertFromWei(data.returnValues.amount0Out, decimals);
    //   amountIn = convertFromWei(data.returnValues.amount1In, token0Decimals);
    //   console.log("------token 0 Decimal-------", token0Decimals)
    // }

    const to = data.returnValues.to;
    // const price = await new CoingeckoService().getUsdPrice(
    //   amountIn,
    //   trackedToken.paired_with_name
    // );
    const price = { usdString: '$2.00', usdNumber: 1, actualPrice: 270.46 };
    console.info("(amountIn > 0 || amountOut > 0)",(amountIn > 0 || amountOut > 0))
    console.info("price.usdNumber >= (min_usd_amount ?? 1)",price.usdNumber >= (min_usd_amount ?? 1))

    if (
      (amountIn > 0 || amountOut > 0) &&
      price.usdNumber >= (min_usd_amount ?? 1)
    ) {
      let marketCap = 0;
      console.info("----step3----")
      if (circulating_supply) {
        const unitPrice = price.actualPrice / (amountOut / amountIn);
        marketCap = unitPrice * circulating_supply;
      }

      const { group_id, token_name, chain_name } = trackedToken;
      try {
        console.info("--------write to DB----------");
        await queries.writeAllBuysToDB({
          buyer_address: to,
          buyer_amount: price.usdNumber,
          token_name: token_name,
          transaction_link: tx_link,
          transaction_chain: chain_name,
          group_id: group_id,
        });
      } catch (error) {
        console.log(
          "[Utils::swapHanlder::SaveToDB]",
          {
            group_id,
            token_name,
            chain_name,
          },
          error
        );
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
    const circulatingSupply = totalSupply
      ? convertFromWei(totalSupply, token_decimals)
      : 0;
    if (circulatingSupply)
      await queries.updateTrackedTokenCircSupply(
        group_id,
        id,
        circulatingSupply
      );
  } catch (error) {
    console.log("[Utils::setCirculatingSupply]", error);
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
      // send to trending channel
      trendingQueue.add({
        type: "animation",
        file_id: buy_media.file_id,
        messageTemplate,
      });
    } else if (buy_media?.type === "photo") {
      await sendPhotoWithCaption(groupId, buy_media.file_id, messageTemplate);
      // send to trending channel
      trendingQueue.add({
        type: "photo",
        file_id: buy_media.file_id,
        messageTemplate,
      });
    } else {
      bot
        .sendMessage(groupId, messageTemplate, {
          parse_mode: "HTML",
          disable_web_page_preview: true,
        })
        .catch((error) => {
          handleSendError(error, groupId);
        });
      // send to trending channel
      trendingQueue.add({
        type: "",
        file_id: "",
        messageTemplate,
      });
    }
  }, 2000);
};

const sendAnimationWithCaption = async (groupId, animation, caption) => {
  return bot
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
  return bot
    .sendPhoto(groupId, photo, {
      parse_mode: "HTML",
      disable_web_page_preview: true,
      caption: caption,
    })
    .catch((error) => {
      handleSendError(error, groupId);
    });
};

const sendToTrendingChannel = async (config) => {
  const trendingChannelId = appConfig.trending_group_id;
  if (config?.type === "animation") {
    await sendAnimationWithCaption(
      trendingChannelId,
      config.file_id,
      config.messageTemplate
    );
  } else if (config?.type === "photo") {
    await sendPhotoWithCaption(
      trendingChannelId,
      config.file_id,
      config.messageTemplate
    );
  } else {
    bot
      .sendMessage(trendingChannelId, config?.messageTemplate, {
        parse_mode: "HTML",
        disable_web_page_preview: true,
      })
      .catch((error) => {
        handleSendError(error, trendingChannelId);
      });
  }
};

const trendingQueue = TrendingQueue(sendToTrendingChannel, {
  interval: 3100,
  max: 1000,
});

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
  const rankNumber = Number(rank);
  switch (rankNumber) {
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
      return "🔥";
  }
};

const genFormatter3dec = new Intl.NumberFormat("en-US", {
  notation: "standard",
  maximumFractionDigits: 3,
});

const genFormatter = new Intl.NumberFormat("en-US", {
  notation: "standard",
  maximumFractionDigits: 0,
});

const compactFormatter = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 2,
});

const amountFormater = (value) => {
  const parsedValue = Number.parseFloat(value);
  if (parsedValue > 0.001 && parsedValue <= 999999999) {
    return genFormatter3dec.format(value);
  } else if (Number.parseFloat(value) > 999999999) {
    return compactFormatter.format(value);
  } else {
    return Number.parseFloat(value).toExponential(2);
  }
};

const amountFormater2 = (value) => {
  const parsedValue = Number.parseFloat(value);
  if (parsedValue > 0.001 && parsedValue <= 999999999) {
    return genFormatter.format(value);
  } else if (Number.parseFloat(value) > 999999999) {
    return compactFormatter.format(value);
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

const trendingGroupRank = async (groupId) => {
  const trending = await queries.getTrendingGroups(); // [{group_id: 123, rank: 1}]
  if (trending.some((group) => group.group_id === groupId)) {
    return trending.find((group) => group.group_id === groupId).rank;
  } else {
    return 0;
  }
};

const handleSendError = (error, groupId) => {
  const errorJson = error.toJSON();
  if (
    errorJson.message.includes("bot was blocked") ||
    errorJson.message.includes("bot was kicked") ||
    errorJson.message.includes("group chat was upgraded") ||
    errorJson.message.includes("not found") ||
    errorJson.message.includes("no rights to send a message")
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
  getGroupInviteLink,
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
  sendHTMLMessage,
  getCountdown,
  getCountdownString,
  getAd,
  ellipseAddress,
  rankIcon,
  amountFormater,
  getBuyerLink,
  isNewBuyer,
  getBuyerBalance,
  getChart,
  convertFromWei,
  getGroupMedia,
  amountFormater2,
  percentageFormatter,
  handleSendError,
  trendingGroupRank,
};
