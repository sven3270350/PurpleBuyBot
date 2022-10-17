const queries = require("../db/queries");
const utils = require("../utils");
const { countdowToStartTemplate } = require("../utils/templates");

const countdowns = {};

const countdownHandler = async (activeCampaign) => {
  const startDate = new Date(activeCampaign.start_time);
  const endDate = new Date(activeCampaign.end_time);

  const startCountdownString = utils.getCountdownString(startDate);
  const endCountDownString = utils.getCountdownString(endDate);

  try {
    const ad = await utils.getAd(activeCampaign.group_id);
    const groupLink = await utils.getGroupInviteLink(activeCampaign.group_id);

    const startCountdownToUse =
      new Date() > startDate ? "Started" : startCountdownString;

    const templates = countdowToStartTemplate(
      startCountdownToUse,
      endCountDownString,
      groupLink,
      ad
    );

    // send message to group
    utils.sendHTMLMessage(activeCampaign.group_id, templates);
  } catch (error) {
    console.log("[countdown::countdownHandler]", error);
  }
};

const main = async (interval = 1000 * 30) => {
  // get all tracked tokens
  const maxDelayValue = 2147483647;

  try {
    setInterval(
      async () => {
        const activeCampaigns = await queries.getAllUpcomingCampaigns();

        // if no active campaigns, and countdowns, then stop all countdowns
        if (
          activeCampaigns.length === 0 &&
          Object.keys(countdowns).length > 0
        ) {
          Object.keys(countdowns).forEach((id) => {
            clearInterval(countdowns[id]);
            delete countdowns[id];
          });
        }

        // stop countdowns that are no longer active
        Object.keys(countdowns).forEach((id) => {
          const campaign = activeCampaigns.find(
            (c) => Number(c.id) === Number(id)
          );
          if (!campaign) {
            clearInterval(countdowns[id]);
            delete countdowns[id];
          }
        });

        // for each active campaign, create a countdown
        activeCampaigns.forEach(async (activeCampaign) => {
          const countdownInterval =
            1000 * 60 * (activeCampaign.count_down ?? 10);

          // check if it's is not in countdowns
          if (!utils.keyInObject(activeCampaign.id, countdowns)) {
            // create a countdown
            const countdown = setInterval(async () => {
              // send reminder message to group
              await countdownHandler(activeCampaign);
            }, countdownInterval);

            // add to countdowns
            countdowns[activeCampaign.id] = countdown;
          }
        });
      },
      interval > maxDelayValue ? maxDelayValue : interval
    );
  } catch (error) {
    console.log("[countdown::main]", error);
  }
};

module.exports = {
  main,
};
