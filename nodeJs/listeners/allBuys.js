const queries = require("../db/queries");
const utils = require("../utils");
const { generalBuyTemplate } = require("../utils/templates");

const subscriptions = {};

const allBuysHandler = async (trackedToken, amountIn, amountOut, to) => {
  const usdPrice = await utils.getUsdPrice(amountIn, trackedToken.chain_id);
  const templates = generalBuyTemplate(
    trackedToken.token_name,
    amountIn,
    usdPrice,
    amountOut,
    trackedToken.chain_name,
    to
  );

  // send message to group
  utils.sendHTMLMessage(trackedToken.group_id, templates);
};

const subscribe = async (trackedToken, contract) => {
  const subscription = contract.events.Swap({});
  subscriptions[trackedToken.token_address.toLowerCase()] = subscription;

  // subscribe to event
  subscription.on("data", (data) =>
    utils.swapHanlder(contract, trackedToken, data, allBuysHandler)
  );

  subscription.on("error", (error) => console.log(error));
};

const main = async (interval = 1000 * 30) => {
  // get all tracked tokens

  setInterval(async () => {
    const trackedTokens = await queries.getAllActivelyTrackedTokens();

    // if no tracked tokens, and subssciptions, unsubscribe from all
    if (trackedTokens.length === 0 && Object.keys(subscriptions).length > 0) {
      Object.keys(subscriptions).forEach((address) => {
        subscriptions[address].unsubscribe();
        delete subscriptions[address];
      });
    }

    // for each tracked token, subscribe to the event
    trackedTokens.forEach(async (trackedToken) => {
      const provider = utils.getProvider(trackedToken.chain_id);
      const wss = utils.wss(provider);

      // check if event is not in subscriptions
      if (
        !utils.addressInSubscription(
          trackedToken.token_address.toLowerCase(),
          subscriptions
        ) &&
        trackedToken.active_tracking
      ) {
        // get event from contract
        const contract = new wss.eth.Contract(
          utils.UniswapV2Pair.abi,
          trackedToken.pair
        );

        await subscribe(trackedToken, contract);
      }

      // if event is in subscriptions, but not active, unsubscribe
      if (
        utils.addressInSubscription(
          trackedToken.token_address.toLowerCase(),
          subscriptions
        ) &&
        !trackedToken.active_tracking
      ) {
        subscriptions[trackedToken.token_address.toLowerCase()].unsubscribe();
        delete subscriptions[trackedToken.token_address.toLowerCase()];
      }
    });
  }, interval);
};

module.exports = {
  main,
};