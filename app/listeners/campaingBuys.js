const queries = require("../db/queries");
const utils = require("../utils");
const {
  campaignBiggestBuysTemplate,
  campaignRaffleBuysTemplate,
  campaignLastBuyTemplate,
  winnerRaffleBuysTemplate,
} = require("../utils/templates");
const { allBuysHandler } = require("./allBuys");

const subscriptions = {};
let lastBuy = {
  timeout: null,
  winner: {
    buyer_address: null,
    buyer_amount: null,
  },
  lastTimeSet: 0,
};

const campaignBuysHandler = async (
  trackedToken,
  amountIn,
  amountOut,
  mc,
  price,
  to,
  tx_link
) => {
  try {
    const { usdString: usdPrice, usdNumber } = price;

    if (usdNumber >= trackedToken.min_amount) {
      const activeCampaign = await queries.getGroupActiveCampaign(
        trackedToken.group_id
      );

      await queries.writeBuysToDB({
        group_id: trackedToken.group_id,
        campaign_id: trackedToken.campaign_id,
        buyer_address: to,
        buyer_amount: usdNumber,
        transaction_link: tx_link,
        transaction_chain: trackedToken.chain_id,
        campaign_type: trackedToken.campaing_type,
      });

      const ad = await utils.getAd(trackedToken.group_id);

      const endDate = new Date(activeCampaign?.end_time);
      const times = {
        start_time: new Date(activeCampaign?.start_time).toLocaleString(),
        count_down: utils.getCountdownString(endDate),
      };

      const new_buyer = {
        amountIn,
        amountOut,
        usdPrice,
        usdNumber,
        tx_link,
        mc,
        to: utils.ellipseAddress(to),
        chain_name: trackedToken?.chain_name,
      };

      const campaign = {
        min_buy: activeCampaign?.min_amount,
        type: activeCampaign?.campaing_type,
        prize: activeCampaign?.prize,
        trackedToken,
      };

      let templates;

      if (activeCampaign?.campaing_type) {
        const { buy_icon, buy_media } = await utils.getGroupMedia(
          trackedToken.group_id
        );

        const rank = await utils.trendingGroupRank(trackedToken.group_id);

        switch (activeCampaign?.campaing_type) {
          case "Biggest Buy":
            const ranking = await queries.getTop5Buys(trackedToken.campaign_id);
            const leaderboard = {
              leading: {
                address: ranking[0]?.buyer_address,
                amount: ranking[0]?.amount,
              },
              others: ranking,
            };

            templates = await campaignBiggestBuysTemplate(
              rank,
              times,
              new_buyer,
              buy_icon,
              !!buy_media,
              leaderboard,
              campaign,
              ad
            );
            break;
          case "Raffle":
            const odds = await queries.getOdds(trackedToken.campaign_id);
            templates = await campaignRaffleBuysTemplate(
              rank,
              times,
              new_buyer,
              buy_icon,
              !!buy_media,
              campaign,
              ad,
              odds
            );
            break;
          case "Last Buy":
            clearTimeout(lastBuy.timeout);
            const winner = {
              buyer_address: to,
              buyer_amount: new_buyer.usdPrice,
            };

            lastBuy.winner = winner;
            const resetAfter =
              lastBuy.lastTimeSet > 0
                ? Math.round((new Date() - lastBuy.lastTimeSet) / 1000)
                : 0;

            lastBuy.timeout = setTimeout(async () => {
              await queries.setWinnerAndEndContest(
                to,
                trackedToken.campaign_id
              );

              // announce winner
              let template = await winnerRaffleBuysTemplate(
                lastBuy.winner,
                activeCampaign,
                ad
              );
              await utils.sendHTMLMessage(trackedToken.group_id, template);
              await queries.deleteNonRandomWinner(trackedToken.campaign_id);
            }, activeCampaign.interval * 1000);

            const lastBuyCampaign = {
              ...campaign,
              interval: activeCampaign?.interval,
              resetAfter,
            };

            templates = await campaignLastBuyTemplate(
              rank,
              times,
              new_buyer,
              buy_icon,
              !!buy_media,
              lastBuyCampaign,
              ad
            );
            lastBuy.lastTimeSet = new Date();
            break;
          default:
            break;
        }
      }
      // send message to group
      utils.sendHTMLMessage(trackedToken.group_id, templates);
    } else {
      await allBuysHandler(
        trackedToken,
        amountIn,
        amountOut,
        mc,
        price,
        to,
        tx_link
      );
    }
  } catch (error) {
    const { group_id } = trackedToken;
    console.log("[campaignBuys::allBuysHandler]");
    utils.handleSendError(error, group_id);
  }
};

const subscribe = async (trackedToken, contract) => {
  const subscription = contract.events.Swap({});
  subscriptions[
    `${trackedToken.token_address.toLowerCase()}_${trackedToken.id}`
  ] = subscription;

  // subscribe to event
  subscription.on("data", (data) =>
    utils.swapHanlder(contract, trackedToken, data, campaignBuysHandler)
  );

  subscription.on("error", (error) => console.log(error));
};

const main = async (interval = 1000 * 60) => {
  // get all tracked tokens
  const maxDelayValue = 2147483647;

  try {
    setInterval(
      async () => {
        const trackedTokens =
          await queries.getAllActivelyTrackedTokensWithActiveCampaign();

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

        // stop subcription if there is no active campaign
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
        await Promise.all(
          trackedTokens.map(async (trackedToken) => {
            const provider = utils.getProvider(trackedToken.chain_id);
            const wss = utils.wss(provider);

            // check if event is not in subscriptions
            if (
              !utils.keyInObject(
                `${trackedToken.token_address.toLowerCase()}_${trackedToken.id}`,
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
          })
        ).catch((err) => console.log("[CampaignBuyPromiseAll:Error]", err));
      },
      interval > maxDelayValue ? maxDelayValue : interval
    );
  } catch (error) {
    console.log("[campaignBuys::main]", error);
  }
};

module.exports = {
  main,
};
