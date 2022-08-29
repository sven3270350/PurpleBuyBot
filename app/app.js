require("dotenv").config({ path: "../.env" });

const allBuysListener = require("./listeners/allBuys");
const countdownListener = require("./listeners/countdown");
const campaignBuyListener = require("./listeners/campaingBuys");
const winnerAnnouncer = require("./listeners/winnerAnnouncer");
const utils = require("./utils");
// main function, iterates through all contracts in pairs
(async function () {
  await utils.cachePrices();
  await allBuysListener.main();
  await countdownListener.main();
  await campaignBuyListener.main();
  await winnerAnnouncer.main();
})().catch((err) => console.log(err));
