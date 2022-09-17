const queries = require("../db/queries");
const utils = require("../utils");
const {
  winnerBiggestBuysTemplate,
  winnerRaffleBuysTemplate,
} = require("../utils/templates");

const announcers = {};

const announcerHandler = async (activeCampaign) => {
  try {
    const ad = await utils.getAd(activeCampaign.group_id);

    let templates;

    if (activeCampaign.campaing_type) {
      let winner, winnerAddress;

      switch (activeCampaign.campaing_type) {
        case "Biggest Buy":
          // anounce biggest buy campaign winner
          winner = await queries.getTop5Buys(activeCampaign.id);
          winnerAddress = winner[0].buyer_address;
          templates = winnerBiggestBuysTemplate(winner, activeCampaign, ad);
          await queries.deleteNonTop5Buys(activeCampaign.id);

          // write winner to campaign
          await queries.writeWinnerToCampaign(winnerAddress, activeCampaign.id);
          break;
        case "Raffle":
          // anounce raffle campaign winner
          winner = await queries.getRandomWinner(activeCampaign.id);
          winnerAddress = winner.buyer_address;
          templates = winnerRaffleBuysTemplate(winner, activeCampaign, ad);

          // write winner to campaign
          await queries.writeWinnerToCampaign(winnerAddress, activeCampaign.id);

          await queries.deleteNonRandomWinner(activeCampaign.id);
          break;
        case "Last Buy":
          // anounce last buy campaign winner
          winner = await queries.getLastBuy(activeCampaign.id);
          winnerAddress = winner.buyer_address;

          templates = winnerRaffleBuysTemplate(winner, activeCampaign, ad);

          // write winner to campaign
          await queries.writeWinnerToCampaign(winnerAddress, activeCampaign.id);

          await queries.deleteNonLastBuy(activeCampaign.id);
          break;
        default:
          break;
      }

      // send message to group
      utils.sendHTMLMessage(activeCampaign.group_id, templates);
    }
  } catch (error) {
    console.log("[announcer::announcerHandler]", error);
  }
};

const main = async (interval = 1000 * 30) => {
  // get all tracked tokens
  const maxDelayValue = 2147483647;
  try {
    setInterval(
      async () => {
        const activeCampaigns = await queries.getAllActiveCampaigns();

        // for each active campaign, create a announcer
        activeCampaigns.forEach(async (activeCampaign) => {
          const timeDiff = new Date(activeCampaign.end_time) - new Date();
          // check if it's is not in announcers
          if (!utils.keyInObject(activeCampaign.id, announcers)) {
            // create a announcer
            const announcer = setTimeout(
              async () => {
                // send reminder message to group
                await announcerHandler(activeCampaign);
                // delete announcer
                clearTimeout(announcers[activeCampaign.id]);
                delete announcers[activeCampaign.id];
                if (timeDiff > maxDelayValue) {
                  await queries.stopCampaingByGroup(activeCampaign.id);
                }
              },
              timeDiff > maxDelayValue ? maxDelayValue : timeDiff
            );

            // add to announcers
            if (!announcers[activeCampaign.id]) {
              announcers[activeCampaign.id] = announcer;
            }
          }
        });
      },
      interval > maxDelayValue ? maxDelayValue : interval
    );
  } catch (error) {
    console.log("[announcer::main]", error);
  }
};

module.exports = {
  main,
};
