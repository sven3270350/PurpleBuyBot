require("dotenv").config({ path: "../.env" });

const allBuysListener = require("./listeners/allBuys");

// main function, iterates through all contracts in pairs
(async function () {
  await allBuysListener.main();
})();

