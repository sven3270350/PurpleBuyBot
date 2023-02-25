const queries = require("../db/queries");
const utils = require("../utils");
const { countdowToStartTemplate } = require("../utils/templates");

class CountDownService {
  countdowns = {};

  async countdownHandler(activeCampaign) {
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
        activeCampaign.campaing_type,
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
  }

  async main() {
    // get all tracked tokens
    try {
      const activeCampaigns = await queries.getAllUpcomingCampaigns();

      // if no active campaigns, and countdowns, then stop all countdowns
      if (
        activeCampaigns.length === 0 &&
        Object.keys(this.countdowns).length > 0
      ) {
        Object.keys(this.countdowns).forEach((id) => {
          clearInterval(this.countdowns[id]);
          delete this.countdowns[id];
        });
      }

      // stop countdowns that are no longer active
      Object.keys(this.countdowns).forEach((id) => {
        const campaign = activeCampaigns.find(
          (c) => Number(c.id) === Number(id)
        );
        if (!campaign) {
          clearInterval(this.countdowns[id]);
          delete this.countdowns[id];
        }
      });

      // for each active campaign, create a countdown
      activeCampaigns.forEach(async (activeCampaign) => {
        const countdownInterval = 1000 * 60 * (activeCampaign.count_down ?? 10);

        // check if it's is not in countdowns
        if (!utils.keyInObject(activeCampaign.id, this.countdowns)) {
          // create a countdown
          const countdown = setInterval(async () => {
            // send reminder message to group
            await this.countdownHandler(activeCampaign);
          }, countdownInterval);

          // add to countdowns
          this.countdowns[activeCampaign.id] = countdown;
        }
      });
    } catch (error) {
      console.log("[countdown::main]", error);
    }
  }
}

module.exports = CountDownService;
