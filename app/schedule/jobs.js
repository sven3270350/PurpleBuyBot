const schedule = require("node-schedule");
const CoingeckoService = require("../services/coingecko");

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

module.exports = {
  CoingeckoCacheJob,
};
