const jobs = require("./jobs");

const startMainJobs = async () => {
  jobs.CoingeckoCacheJob();
  jobs.AllBuysJob();
  jobs.ContestBuysJob();
  jobs.CountDownJob();
  jobs.AnnounceWinnerJob();
};

const startChildJobs = async () => {};

module.exports = {
  startMainJobs,
  startChildJobs,
};
