const jobs = require("./jobs");

const startMainJobs = async () => {
  jobs.CoingeckoCacheJob();
  jobs.AllBuysJob();
  jobs.ContestBuysJob();
  jobs.CountDownJob();
  jobs.AnnounceWinnerJob();

  // maintenance jobs

  jobs.CleanDBJob();
};

const startChildJobs = async () => {};

module.exports = {
  startMainJobs,
  startChildJobs,
};
