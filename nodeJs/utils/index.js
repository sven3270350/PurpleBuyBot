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
  const token0 = await getToken0(contract);
  const token1 = await getToken1(contract);

  if (trackedToken === token0) {
    return { token: 0, address: token0 };
  } else {
    return { token: 1, address: token1 };
  }
};

const getToken0 = async (contract) => {
  return contract.methods.token0().call();
};

const getToken1 = async (contract) => {
  return contract.methods.token1().call();
};

const hasActiveSubscription = async (groupId) => {
  const activeSubscription = await queries.getActiveSubscriptionByGroupId(
    groupId
  );
  return activeSubscription.length > 0;
};

const getTokenDecimals = async (address, chain) => {
  const web3 = wss(appConfig.getProvider(chain));
  const token = new web3.eth.Contract(ERC20, address);
  return token.methods.decimals().call();
};

const swapHanlder = async (contract, trackedToken, data, callback) => {
  const token_address = trackedToken.token_address.toLowerCase();
  const decimals = trackedToken.token_decimals;
  const chainId = trackedToken.chain_id;

  const selectedTrackedToken = await selectTrackedToken(
    token_address,
    contract
  );

  let amountIn = 0;
  let amountOut = 0;

  if (selectedTrackedToken.token === 1) {
    const token1Decimals = await getTokenDecimals(
      selectedTrackedToken.address,
      chainId
    );

    amountIn = Web3.utils.fromWei(
      data.returnValues.amount1In,
      decimalsToUnit(token1Decimals)
    );

    amountOut = Web3.utils.fromWei(
      data.returnValues.amount0Out,
      decimalsToUnit(decimals)
    );
  } else {
    const token0Decimals = await getTokenDecimals(
      selectedTrackedToken.address,
      chainId
    );

    amountIn = Web3.utils.fromWei(
      data.returnValues.amount0In,
      decimalsToUnit(token0Decimals)
    );

    amountOut = Web3.utils.fromWei(
      data.returnValues.amount1Out,
      decimalsToUnit(decimals)
    );
  }

  const to = data.returnValues.to;

  if (amountIn > 0 || amountOut > 0) {
    callback(trackedToken, amountIn, amountOut, to);
  }
};

const addressInSubscription = (address, subscription) => {
  const length = Object.keys(subscription).length;
  if (length === 0) return false;
  return !!subscription.hasOwnProperty(address);
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
  return units[decimals];
};

const getUsdPrice = async (amount, chainId) => {
  const id = appConfig.getCoinGeckoId(chainId);
  const { data } = await CoinGeckoClient.simple.price({
    ids: id,
    vs_currencies: "usd",
  });
  const price = data[id].usd;

  return Intl.NumberFormat("en-US").format(Number(amount) * price);
};

const sendHTMLMessage = async (groupId, messageTemplate) => {
  bot.sendMessage(groupId, messageTemplate, { parse_mode: "HTML" });
};

module.exports = {
  ...appConfig,
  selectTrackedToken,
  getToken0,
  getToken1,
  hasActiveSubscription,
  addressInSubscription,
  swapHanlder,
  UniswapV2Pair,
  wss,
  fromWei: Web3.utils.fromWei,
  decimalsToUnit,
  getUsdPrice,
  sendHTMLMessage,
};
