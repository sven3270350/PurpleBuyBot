// 20 messages per minute per group

// config: { interval, max}

const TrendingQueue = (callback, config) => {
  const queue = [];
  const max = config.max || 300;
  let tracker;

  const add = (item) => {
    if (!tracker || tracker?._destroyed) {
      start();
    }

    if (queue.length >= max) {
      dequeue();
    }
    queue.push(item);
  };

  const get = () => queue;

  const dequeue = () => {
    return queue.shift();
  };

  const clear = () => {
    queue.length = 0;
  };

  const start = () => {
    tracker = setInterval(async () => {
      if (queue.length > 0) {
        await callback(dequeue());
      }
    }, config.interval || 1000);
  };

  return {
    add,
    get,
    clear,
    start,
  };
};

module.exports = TrendingQueue;
