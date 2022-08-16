require("dotenv").config({ path: "../.env" });

const allBuysListener = require("./listeners/allBuys");
const countdownListener = require("./listeners/countdown");

// main function, iterates through all contracts in pairs
(async function () {
  await allBuysListener.main();
  await countdownListener.main();
})();
