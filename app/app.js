const cluster = require("cluster");
const semver = require("semver");
const { startMainJobs, startChildJobs } = require("./schedule");

var https = require('https');
var http = require('http');

https.globalAgent.maxSockets = 5;
http.globalAgent.maxSockets = 5;

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