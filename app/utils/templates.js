const {
  ellipseAddress,
  numberToUsd,
  rankIcon,
  amountFormater,
  getBuyerLink,
  isNewBuyer,
  getChart,
  percentageFormatter,
} = require(".");

const generalBuyTemplate = async (
  trackedToken,
  amounts,
  buyer,
  tx_link,
  group_icon,
  has_media,
  ad = ""
) => {
  const multiplier = Math.round(amounts.multiplier / 10);
  const { newBuyer, percentageIncrease } = await isNewBuyer(
    amounts.buyer,
    trackedToken.token_address,
    trackedToken.token_decimals,
    amounts.amountOut,
    trackedToken.chain_id
  );

  const buy_icon = group_icon || "🟢";

  const percent =
    percentageIncrease <= 10000
      ? percentageFormatter.format(percentageIncrease)
      : "10000%+";

  const maxIcons = has_media ? 300 : 3667;

  return `
 <b>${trackedToken.token_name} Buy!</b>
${buy_icon.repeat((multiplier > maxIcons ? maxIcons : multiplier) | 1)}

💸 ${amountFormater(amounts.amountIn)} ${trackedToken.paired_with_name} (${
    amounts.usdPrice
  })
🚀 ${amountFormater(amounts.amountOut)} ${trackedToken.token_symbol}
👤 Buyer <a href='${getBuyerLink(
    amounts.buyer,
    trackedToken.chain_id
  )}'>${buyer}</a> | <a href='${tx_link}'>Txn</a>
${!newBuyer ? "⏫Position: " + percent : "🔥 New Holder"}

🕸 Chain:${trackedToken.chain_name}
📊 <a href='${getChart(
    trackedToken.chain_id,
    trackedToken.pair
  )}'>Chart</a> | 📈 <a href="https://t.me/PurpleBuyBotTrending">Trending</a> | 👨‍💻 <a href="https://t.me/PurpleBuyBotSupport">Support</a>

——

<i>${ad || "Premium"}</i>
`;
};

const countdowToStartTemplate = (startCountdown, EndCountdown, ad) => {
  return `
🕐🕐🕐🕐🕐🕐🕐🕐🕐🕐🕐

<b>Countdown to buy contest</b>

<b>Starts: <i>${startCountdown}</i></b>
<b>Ends: <i>${EndCountdown}</i></b>

——

<i>${ad || "Premium"}</i>
`;
};

const campaignBiggestBuysTemplate = (
  times,
  new_buyer,
  leaderboard,
  campaign,
  ad
) => {
  const top5 = leaderboard.others;
  const leading = leaderboard.leading;

  let templates = ``;

  for (let i = 0; i < top5.length; i++) {
    const { buyer_address, amount } = top5[i];
    templates += `
${rankIcon(i + 1)} ${ellipseAddress(buyer_address)} ➖${numberToUsd(amount)}
`;
  }

  return `
<b>🎉 ${campaign.type} Competition Entry</b>

🕓 Started at: <b>${times.start_time}</b>
⏳ Ends in: <b>${times.count_down}</b>
⬇️ Minimum Buy: <b>${Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(campaign.min_buy)}</b>
🏆 Prize: <b>${campaign.prize}</b>

<b>Top 5</b>
${templates}

🎖 Top buyer <b><i>${
    ellipseAddress(leading.address) || "take this spot 😉?"
  }</i></b>  ${numberToUsd(leading.amount) || ""}

<b>New Entry:</b>

😎 <b>Buyer :</b> <i><a href='${new_buyer.tx_link}'>${ellipseAddress(
    new_buyer.to
  )}</a></i>
🤑 <b>Amount :</b> <i>${amountFormater(new_buyer.amountOut)} (~${
    new_buyer.usdPrice
  })</i>

⛓ <b>Bought On:</b> <i>${new_buyer.chain_name}</i>

——

<i>${ad || "Premium"}</i>
`;
};

const campaignRaffleBuysTemplate = (times, new_buyer, campaign, ad, odds) => {
  return `
<b>🎉 ${campaign.type} Competition Entry</b>

🕓 Started at: <b>${times.start_time}</b>
⏳ Ends in: <b>${times.count_down}</b>
⬇️ Minimum Buy: <b>${Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(campaign.min_buy)}</b>
🏆 Prize: <b>${campaign.prize}</b>

<b>Winning Odds</b>
${odds}

🆕 <b>New Entry:</b>

😎 <b>Buyer :</b> <i><a href='${new_buyer.tx_link}'>${ellipseAddress(
    new_buyer.to
  )}</a></i>
🤑 <b>Amount :</b> <i>${amountFormater(new_buyer.amountOut)} (~${
    new_buyer.usdPrice
  })</i>

⛓ <b>Bought On:</b> <i>${new_buyer.chain_name}</i>

——

<i>${ad || "Premium"}</i>
`;
};

const winnerBiggestBuysTemplate = (leaderboard, campaign, ad) => {
  let templates = ``;

  for (let i = 0; i < leaderboard.length; i++) {
    const { buyer_address, amount } = leaderboard[i];
    templates += `
${rankIcon(i + 1)} ${ellipseAddress(buyer_address)} ➖${numberToUsd(amount)}
`;
  }

  return `
<b>${campaign.campaing_type} Competition Completed</b>

🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉
<b>Winner</b>
<code>${leaderboard[0].buyer_address} </code> 
<i> ➖ ${numberToUsd(leaderboard[0].amount)}</i>

<b>Top 5</b>
${templates}

🏆 Prize: <b>${campaign.prize}</b>

——

<i>${ad || "Premium"}</i>
`;
};

const winnerRaffleBuysTemplate = (winner, campaign, ad) => {
  return `
<b>${campaign.campaing_type} Competition Completed</b>

🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉
<b>Winner</b>
<code>${winner.buyer_address} ➖ ${numberToUsd(winner.buyer_amount)}</code>


🏆 Prize: <b>${campaign.prize}</b>

——

<i>${ad || "Premium"}</i>
`;
};

module.exports = {
  generalBuyTemplate,
  countdowToStartTemplate,
  campaignBiggestBuysTemplate,
  campaignRaffleBuysTemplate,
  winnerBiggestBuysTemplate,
  winnerRaffleBuysTemplate,
};
