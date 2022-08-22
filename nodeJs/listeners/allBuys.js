const queries = require("../db/queries");
const utils = require("../utils");
const { generalBuyTemplate } = require("../utils/templates");

const subscriptions = {};

const allBuysHandler = async (
  trackedToken,
  amountIn,
  amountOut,
  to,
  tx_link
) => {
  try {
    const { usdString: usdPrice, usdNumber } = await utils.getUsdPrice(
      amountIn,
      trackedToken.chain_id
    );
    const ad = await utils.getAd(trackedToken.group_id);
    const amounts = {
      amountIn,
      amountOut,
      usdPrice,
    };

    const templates = generalBuyTemplate(
      trackedToken,
      amounts,
      utils.ellipseAddress(to),
      tx_link,
      ad
    );

    // send message to group
    utils.sendHTMLMessage(trackedToken.group_id, templates);
  } catch (error) {
    console.log("[allBuys::allBuysHandler]", error);
  }
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

  try {
    setInterval(async () => {
      const trackedTokens =
        await queries.getAllActivelyTrackedTokensNoActiveCampaign();

      // if no tracked tokens, and subssciptions, unsubscribe from all
      if (trackedTokens.length === 0 && Object.keys(subscriptions).length > 0) {
        Object.keys(subscriptions).forEach((address) => {
          subscriptions[address].unsubscribe();
          delete subscriptions[address];
        });
      }

      // if stop subscription if not actively tracked
      Object.keys(subscriptions).forEach((address) => {
        if (
          !trackedTokens.find(
            (token) =>
              token.token_address.toLowerCase() === address.toLocaleLowerCase()
          )
        ) {
          subscriptions[address].unsubscribe();
          delete subscriptions[address];
        }
      });

      // for each tracked token, subscribe to the event
      trackedTokens.forEach(async (trackedToken) => {
        const provider = utils.getProvider(trackedToken.chain_id);
        const wss = utils.wss(provider);

        // check if event is not in subscriptions
        if (
          !utils.keyInObject(
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
      });
    }, interval);
  } catch (error) {
    console.log("[allBuys::main]", error);
  }
};

module.exports = {
  main,
  allBuysHandler,
};
