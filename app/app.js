const cluster = require("cluster");
const semver = require("semver");
const { startMainJobs, startChildJobs } = require("./schedule");

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
    const isPrimaryCluster = () => {
      if (semver.gte(process.version, "v16.0.0")) {
        return cluster.isPrimary;
      }
      return cluster.isMaster;
    };

    if (isPrimaryCluster()) {
      // start main jobs
      startMainJobs();

      await allBuysListener.main();
      await campaignBuyListener.main();
      await countdownListener.main();
      await winnerAnnouncer.main();

      // manage child processes
      let childProcessId;
      cluster.on("exit", (worker, code, signal) => {
        // refork
        if (worker.process.id == childProcessId) {
          console.log(
            `[app::main] child process ${childProcessId} died, reforking...`
          );
          cluster.fork();
        }
      });
      cluster.on("fork", (worker) => {
        childProcessId = worker.process.pid;
      });
      cluster.fork();
    } else {
      // start child jobs in child process
      startChildJobs();
    }
  } catch (error) {
    console.log("[_app::main]", error);
  }
};

main();
