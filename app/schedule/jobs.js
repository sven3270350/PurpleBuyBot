const schedule = require("node-schedule");
const CoingeckoService = require("../services/coingecko");
const AllBuysService = require("../services/all_buys");
const ContestBuysService = require("../services/contest_buys");
const CountDownService = require("../services/countdown");
const AnnounceWinnerService = require("../services/announce_winner");
const { cleanDB, deleteBlacklisted } = require("../services/maintenance");
class Job {
  rule;
  callback;
  jobName;

  /**
   * @param rule
   * @param callback
   * @param jobName
   */
  constructor(rule, callback, jobName) {
    this.rule = rule;
    this.callback = callback;
    this.jobName = jobName;
  }

  schedule() {
    return schedule.scheduleJob(this.rule, async () => {
      try {
        this.callback && (await this.callback());
      } catch (error) {
        let message = `MJob.schedule error: ${error}, rule: ${this.rule}`;
        if (this.jobName) {
          message += `, jobName: ${this.jobName}`;
        }
        console.error(message);
      }
    });
  }
}

// Pessimism Lock Job
class JobPessimism extends Job {
  schedule() {
    let pessimismLock = false;

    const _callback = this.callback;

    this.callback = async () => {
      if (pessimismLock) {
        return;
      }
      pessimismLock = true;

      try {
        _callback && (await _callback());
      } catch (error) {
        throw error;
      } finally {
        // Always release lock
        pessimismLock = false;
      }
    };

    return super.schedule();
  }
}

function CoingeckoCacheJob() {
  const cb = async () => {
    await new CoingeckoService().cachePrices();
  };

  new JobPessimism("*/59 * * * * *", cb, CoingeckoCacheJob.name).schedule();
}

function AllBuysJob() {
  const cb = async () => {
    await new AllBuysService().main();
  };

  new JobPessimism("*/30 * * * * *", cb, AllBuysJob.name).schedule();
}

function ContestBuysJob() {
  const cb = async () => {
    await new ContestBuysService().main();
  };

  new JobPessimism("*/30 * * * * *", cb, ContestBuysJob.name).schedule();
}

function CountDownJob() {
  const cb = async () => {
    await new CountDownService().main();
  };

  new JobPessimism("*/30 * * * * *", cb, CountDownJob.name).schedule();
}

function AnnounceWinnerJob() {
  const cb = async () => {
    await new AnnounceWinnerService().main();
  };

  new JobPessimism("*/30 * * * * *", cb, AnnounceWinnerJob.name).schedule();
}

function CleanDBJob() {
  const cb = async () => {
    await cleanDB();
    await deleteBlacklisted();
  };

  new JobPessimism("0 0 0 */25 * *", cb, CleanDBJob.name).schedule();
}

module.exports = {
  CoingeckoCacheJob,
  AllBuysJob,
  ContestBuysJob,
  CountDownJob,
  AnnounceWinnerJob,
  CleanDBJob,
};
