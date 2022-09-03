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

    if (activeCampaign.campaing_type === "Biggest Buy") {
      // anounce biggest buy campaign winner
      const winner = await queries.getTop5Buys(activeCampaign.id);
      const winnerAddress = winner[0].buyer_address;
      templates = winnerBiggestBuysTemplate(winner, activeCampaign, ad);
      await queries.deleteNonTop5Buys(activeCampaign.id);

      // write winner to campaign
      await queries.writeWinnerToCampaign(winnerAddress, activeCampaign.id);
    } else {
      // anounce raffle campaign winner
      const winner = await queries.getRandomWinner(activeCampaign.id);
      const winnerAddress = winner.buyer_address;
      templates = winnerRaffleBuysTemplate(winner, activeCampaign, ad);

      // write winner to campaign
      await queries.writeWinnerToCampaign(winnerAddress, activeCampaign.id);

      await queries.deleteNonRandomWinner(activeCampaign.id);
    }

    // send message to group
    utils.sendHTMLMessage(activeCampaign.group_id, templates);
  } catch (error) {
    console.log("[announcer::announcerHandler]", error);
  }
};

const main = async (interval = 1000 * 30) => {
  // get all tracked tokens

  try {
    setInterval(async () => {
      const activeCampaigns = await queries.getAllActiveCampaigns();

      // for each active campaign, create a announcer
      activeCampaigns.forEach(async (activeCampaign) => {
        const timeDiff = new Date(activeCampaign.end_time) - new Date();
        // check if it's is not in announcers
        if (!utils.keyInObject(activeCampaign.id, announcers)) {
          // create a announcer
          const announcer = setTimeout(async () => {
            // send reminder message to group
            await announcerHandler(activeCampaign);
            // delete announcer
            delete announcers[activeCampaign.id];
          }, timeDiff);

          // add to announcers
          if (!announcers[activeCampaign.id]) {
            announcers[activeCampaign.id] = announcer;
          }
        }
      });
    }, interval);
  } catch (error) {
    console.log("[announcer::main]", error);
  }
};

module.exports = {
  main,
};
