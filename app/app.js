const { startMainJobs, startChildJobs } = require("./schedule");
// scheduler issue (discarded commit)
const allBuysListener = require("./listeners/allBuys");
const countdownListener = require("./listeners/countdown");
const campaignBuyListener = require("./listeners/campaingBuys");
const winnerAnnouncer = require("./listeners/winnerAnnouncer");

const https = require("https");
const http = require("http");

https.globalAgent.maxSockets = 100;
http.globalAgent.maxSockets = 100;

const main = async () => {
  try {
    // start main jobs
    startMainJobs();

    await Promise.all([
      allBuysListener.main(),
      campaignBuyListener.main(),
      countdownListener.main(),
      winnerAnnouncer.main(),
    ]).catch((err) => console.log("[All::PromiseError] : ", err));

    // start child jobs
    startChildJobs();
  } catch (error) {
    console.log("[_app::main]", error);
  }
};

main();
