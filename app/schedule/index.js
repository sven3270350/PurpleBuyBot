const jobs = require("./jobs");

const startMainJobs = async () => {
  jobs.CoingeckoCacheJob();
};

const startChildJobs = async () => {};

module.exports = {
  startMainJobs,
  startChildJobs,
};
