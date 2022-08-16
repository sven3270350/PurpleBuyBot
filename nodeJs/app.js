require("dotenv").config({ path: "../.env" });

const allBuysListener = require("./listeners/allBuys");
const countdownListener = require("./listeners/countdown");
const campaignBuyListener = require("./listeners/campaingBuys");

// main function, iterates through all contracts in pairs
(async function () {
  await allBuysListener.main();
  await countdownListener.main();
  await campaignBuyListener.main();
})();
