require("dotenv").config({ path: "../.env" });

const URL = "wss://mainnet.infura.io/ws/v3/cf3f5c7c8d5f45a48940d926bab3c403";
const Web3 = require("web3");
const appConfig = require("./utils/app_config");
const db = require("./db");

db.query("SELECT * FROM pairs", (err, res) => {
  if (err) {
    console.log(err);
  } else {
    console.log(res.rows);
  }
});

console.log(appConfig.getExploerUrl(1));
console.log(appConfig.getChain(1));
console.log(appConfig.getProvider(1));
console.log(appConfig.getCoinGeckoId(1));

const utils = require("./utils/utils");
const UniswapV2Pair = require("./IUniswapV2Pair.json");
const wss = new Web3(URL);
const pairs = {
  "USDC-ETH": "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
  "USDT-ETH": "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
};

const swap = (pair, data) => {
  const amount0In = data.returnValues.amount0In;
  const amount1In = data.returnValues.amount1In;
  const amount0Out = data.returnValues.amount0Out;
  const amount1Out = data.returnValues.amount1Out;
  const to = data.returnValues.to;

  console.log(
    `Swap* Pair ${pair},  Paid(USDC) ${Web3.utils.fromWei(
      amount0In,
      "picoether"
    )},  Got(ETH) ${Web3.utils.fromWei(amount1Out, "ether")}, To ${to}`
  );

  //   else it's a sell
};

const subscriptions = {};

// connects and subscribes to infura services via web sockets (wss) for updates on reserves
const subscribe = async (pair, contract) => {
  const subscription = contract.events.Swap({});
  subscriptions[pair] = subscription;

  subscription.on("data", (data) => swap(pair, data));
};

// main function, iterates through all contracts in pairs
// (async function () {
//   for (const pair in pairs) {
//     const contract = new wss.eth.Contract(UniswapV2Pair.abi, pairs[pair]);
//     await subscribe(pair, contract);
//     console.log(`Monitoring Pair ${pair}, Address ${pairs[pair]}`);
//   }
//   console.log(subscriptions);

//   setTimeout(() => {
//     console.log("Unsubscribing from USDC-ETH");
//     subscriptions["USDC-ETH"].unsubscribe();
//   }, 10000);
// })();
