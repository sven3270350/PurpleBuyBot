const queries = require("../db/queries");
const utils = require("../utils");
const { campaignBiggestBuysTemplate } = require("../utils/templates");

const subscriptions = {};

const campaignBuysHandler = async (
  trackedToken,
  amountIn,
  amountOut,
  to,
  tx_link
) => {
  try {
    const usdPrice = await utils.getUsdPrice(amountIn, trackedToken.chain_id);
    const ad = await utils.getAd(trackedToken.group_id);
    const activeCampaign = await queries.getGroupActiveCampaign(
      trackedToken.group_id
    );
    const endDate = new Date(activeCampaign.end_time);

    const new_buyer = {
      amountIn,
      amountOut,
      usdPrice,
      tx_link,
      to: utils.ellipseAddress(to),
      chain_name: trackedToken.chain_name,
    };

    const times = {
      start_time: new Date(activeCampaign.start_time).toLocaleString(),
      count_down: utils.getCountdownString(endDate),
    };

    const leaderboard = {
      leading: {
        address: "",
        amount: 0,
      },
      others: [],
    };

    const campaign = {
      min_buy: activeCampaign.minimum_buy_amount,
      type: activeCampaign.campaing_type,
      prize: activeCampaign.prize,
    };

    const templates = campaignBiggestBuysTemplate(
      times,
      new_buyer,
      leaderboard,
      campaign,
      ad
    );

    // send message to group
    utils.sendHTMLMessage(trackedToken.group_id, templates);
  } catch (error) {
    console.log("[campaignBuys::allBuysHandler]", error);
  }
};

const subscribe = async (trackedToken, contract) => {
  const subscription = contract.events.Swap({});
  subscriptions[trackedToken.token_address.toLowerCase()] = subscription;

  // subscribe to event
  subscription.on("data", (data) =>
    utils.swapHanlder(contract, trackedToken, data, campaignBuysHandler)
  );

  subscription.on("error", (error) => console.log(error));
};

const main = async (interval = 1000 * 30) => {
  // get all tracked tokens

  try {
    setInterval(async () => {
      const trackedTokens =
        await queries.getAllActivelyTrackedTokensWithActiveCampaign();

      // if no tracked tokens, and subssciptions, unsubscribe from all
      if (trackedTokens.length === 0 && Object.keys(subscriptions).length > 0) {
        Object.keys(subscriptions).forEach((address) => {
          subscriptions[address].unsubscribe();
          delete subscriptions[address];
        });
      }

      // stop subcription if there is no active campaign
      Object.keys(subscriptions).forEach((address) => {
        if (
          !trackedTokens.find(
            (token) =>
              token.token_address.toLowerCase() === address.toLowerCase()
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
          )
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
    console.log("[campaignBuys::main]", error);
  }
};

module.exports = {
  main,
};
