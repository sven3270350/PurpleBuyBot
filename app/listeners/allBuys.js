const queries = require("../db/queries");
const utils = require("../utils");
const { generalBuyTemplate } = require("../utils/templates");

const subscriptions = {};

const allBuysHandler = async (
  trackedToken,
  amountIn,
  amountOut,
  mc,
  price,
  to,
  tx_link
) => {
  try {
    const { usdString: usdPrice, usdNumber: multiplier } = price;
    const ad = await utils.getAd(trackedToken.group_id);
    const { buy_icon, buy_media } = await utils.getGroupMedia(
      trackedToken.group_id
    );
    const activeContest = await queries.getGroupActiveCampaign(
      trackedToken.group_id
    );

    const contest = {
      count_down: utils.getCountdownString(new Date(activeContest?.end_time)),
      name: activeContest?.campaing_type,
      prize: activeContest?.prize,
    };

    const amounts = {
      amountIn,
      amountOut,
      usdPrice,
      multiplier,
      mc,
      buyer: to,
    };

    const buyer = {
      address: utils.ellipseAddress(to),
      tx_link,
    };

    const templates = await generalBuyTemplate(
      trackedToken,
      amounts,
      buyer,
      buy_icon,
      !!buy_media,
      contest,
      ad
    );

    // send message to group
    utils.sendHTMLMessage(trackedToken.group_id, templates);
  } catch (error) {
    const { group_id, token_name, chain_name } = trackedToken;
    console.log(
      "[allBuys::allBuysHandler]",
      {
        group_id,
        token_name,
        chain_name,
      },
      error
    );
  }
};

const subscribe = async (trackedToken, contract) => {
  const subscription = contract.events.Swap({});
  subscriptions[
    `${trackedToken.token_address.toLowerCase()}_${trackedToken.id}`
  ] = subscription;

  // subscribe to event
  subscription.on("data", (data) => {
    utils.swapHanlder(contract, trackedToken, data, allBuysHandler);
  });

  subscription.on("error", (error) => console.log(error));
};

const main = async (interval = 1000 * 30) => {
  // get all tracked tokens
  const maxDelayValue = 2147483647;

  try {
    setInterval(
      async () => {
        const trackedTokens =
          await queries.getAllActivelyTrackedTokensNoActiveCampaign();

        // if no tracked tokens, and subssciptions, unsubscribe from all
        if (
          trackedTokens.length === 0 &&
          Object.keys(subscriptions).length > 0
        ) {
          Object.keys(subscriptions).forEach((id) => {
            subscriptions[id].unsubscribe();
            delete subscriptions[id];
          });
        }

        // if stop subscription if not actively tracked
        Object.keys(subscriptions).forEach((id) => {
          if (
            !trackedTokens.find(
              (token) =>
                `${token.token_address.toLowerCase()}_${token.id}` === id
            )
          ) {
            subscriptions[id].unsubscribe();
            delete subscriptions[id];
          }
        });

        // for each tracked token, subscribe to the event
        trackedTokens.forEach(async (trackedToken) => {
          const provider = utils.getProvider(trackedToken.chain_id);
          const wss = utils.wss(provider);

          // check if event is not in subscriptions
          if (
            !utils.keyInObject(
              `${trackedToken.token_address.toLowerCase()}_${trackedToken.id}`,
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
      },
      interval > maxDelayValue ? maxDelayValue : interval
    );
  } catch (error) {
    console.log("[allBuys::main]", error);
  }
};

module.exports = {
  main,
  allBuysHandler,
};
