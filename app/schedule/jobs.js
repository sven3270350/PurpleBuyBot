const schedule = require("node-schedule");
const CoingeckoService = require("../services/coingecko");
const AllBuysService = require("../services/all_buys");
const ContestBuysService = require("../services/contest_buys");

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

  new JobPessimism("*/20 * * * * *", cb, CoingeckoCacheJob.name).schedule();
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

module.exports = {
  CoingeckoCacheJob,
  AllBuysJob,
};
