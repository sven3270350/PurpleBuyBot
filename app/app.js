require("dotenv").config({ path: "../.env" });

const throng = require("throng");
const allBuysListener = require("./listeners/allBuys");
const countdownListener = require("./listeners/countdown");
const campaignBuyListener = require("./listeners/campaingBuys");
const winnerAnnouncer = require("./listeners/winnerAnnouncer");
const utils = require("./utils");

const WORKERS = 1;
// main function, iterates through all contracts in pairs
async function start() {
  await utils.cachePrices();
  await allBuysListener.main();
  await countdownListener.main();
  await campaignBuyListener.main();
  await winnerAnnouncer.main();
}

throng({
  workers: WORKERS,
  lifetime: Infinity,
  start: start,
});
