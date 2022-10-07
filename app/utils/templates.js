const {
  ellipseAddress,
  numberToUsd,
  rankIcon,
  amountFormater,
  amountFormater2,
  getBuyerLink,
  isNewBuyer,
  getChart,
  getGroupInviteLink,
  percentageFormatter,
} = require(".");

const generalBuyTemplate = async (
  trackedToken,
  amounts,
  buyer,
  tx_link,
  group_icon,
  has_media,
  contest,
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

  const group_link = await getGroupInviteLink(trackedToken.group_id);
  const buy_icon = group_icon || "🟢";

  const percent =
    percentageIncrease <= 10000
      ? percentageFormatter.format(percentageIncrease)
      : "10000%+";

  const maxIcons = has_media ? 300 : 3667;

  return `
 <b>${
   group_link
     ? "<a href='" + group_link + "'>" + trackedToken.token_name + "</a> "
     : trackedToken.token_name
 } Buy!</b>
${buy_icon.repeat((multiplier > maxIcons ? maxIcons : multiplier) | 1)}

💸 ${amountFormater(amounts.amountIn)} ${trackedToken.paired_with_name} (${
    amounts.usdPrice
  })
🚀 ${amountFormater(amounts.amountOut)} ${trackedToken.token_symbol}
👤 <b>Buyer</b> <a href='${getBuyerLink(
    amounts.buyer,
    trackedToken.chain_id
  )}'>${buyer}</a> | <a href='${tx_link}'>Txn</a>
${!newBuyer ? "⏫ <b>Position:</b> " + percent : "🔥 <b>New Holder</b>"}
${!!amounts.mc ? "🏪 <b>Market Cap</b>: $" + amountFormater2(amounts.mc) : ""}

${
  contest?.count_down
    ? "⏳ " + contest?.name + " Ends in: <b>" + contest?.count_down + "</b>"
    : ""
}

${constest?.prize ? "🏆 Prize: <b>" + contest?.prize + "</b>" : ""}

📊 <a href='${getChart(trackedToken.chain_id, trackedToken.pair)}'>Chart</a> 
📈 <a href="https://t.me/PurpleBuyBotTrending">Trending</a> | 👨‍💻 <a href="https://t.me/PurpleBuyBotSupport">Support</a>
${ad ? "\n\n——\n\n" + ad : ""}
`;
};

const countdowToStartTemplate = (startCountdown, EndCountdown, ad) => {
  return `
🕐🕐🕐🕐🕐🕐🕐🕐🕐🕐🕐

<b>Countdown to buy contest</b>

<b>Starts: <i>${startCountdown}</i></b>
<b>Ends: <i>${EndCountdown}</i></b>
${ad ? "\n\n——\n\n" + ad : ""}
`;
};

const campaignBiggestBuysTemplate = (
  times,
  new_buyer,
  group_icon,
  has_media,
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

  const multiplier = Math.round(new_buyer.usdNumber / 10);
  const buy_icon = group_icon || "🟢";
  const maxIcons = has_media ? 300 : 3667;

  return `
<b>🎉 ${campaign.type} Competition Entry</b>
${buy_icon.repeat((multiplier > maxIcons ? maxIcons : multiplier) | 1)}

⏱ Started at: <b>${times.start_time}</b>
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
${
  !!new_buyer.mc
    ? "🏪 <b>Market Cap :</b> <i>$" + amountFormater2(new_buyer.mc) + "</i>"
    : ""
}
${ad ? "\n\n——\n\n" + ad : ""}
`;
};

const campaignRaffleBuysTemplate = (
  times,
  new_buyer,
  group_icon,
  has_media,
  campaign,
  ad,
  odds
) => {
  const multiplier = Math.round(new_buyer.usdNumber / 10);
  const buy_icon = group_icon || "🟢";

  const maxIcons = has_media ? 300 : 3667;

  return `
<b>🎉 ${campaign.type} Competition Entry</b>
${buy_icon.repeat((multiplier > maxIcons ? maxIcons : multiplier) | 1)}

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
${
  !!new_buyer.mc
    ? "🏪 <b>Market Cap :</b> <i>$" + amountFormater2(new_buyer.mc) + "</i>"
    : ""
}
${ad ? "\n\n——\n\n" + ad : ""}
`;
};

const campaignLastBuyTemplate = (
  times,
  new_buyer,
  group_icon,
  has_media,
  campaign,
  ad
) => {
  const multiplier = Math.round(new_buyer.usdNumber / 10);
  const buy_icon = group_icon || "🟢";

  const maxIcons = has_media ? 300 : 3667;

  return `
  <b>🎉 ${campaign.type} Competition Entry</b>
  ${buy_icon.repeat((multiplier > maxIcons ? maxIcons : multiplier) | 1)}

  <b><i>Countdown Started (${campaign.resetAfter}s after previous start)</i></b>

🕓 Started at: <b>${times.start_time}</b>
⏳ Ends in: <b>${times.count_down}</b>
⬇️ Minimum Buy: <b>${Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(campaign.min_buy)}</b>
🏆 Prize: <b>${campaign.prize}</b>
🕓 Countdown Interval: <b>${campaign.interval}s</b>

🆕 <b>Last Buyer:</b>

<i> Wins the prize if no one buys in the next ${campaign.interval} seconds</i>

😎 <b>Buyer :</b> <i><a href='${new_buyer.tx_link}'>${ellipseAddress(
    new_buyer.to
  )}</a></i>
🤑 <b>Amount :</b> <i>${amountFormater(new_buyer.amountOut)} (~${
    new_buyer.usdPrice
  })</i>
${
  !!new_buyer.mc
    ? "🏪 <b>Market Cap :</b> <i>$" + amountFormater2(new_buyer.mc) + "</i>"
    : ""
}
${ad ? "\n\n——\n\n" + ad : ""}
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
${ad ? "\n\n——\n\n" + ad : ""}
`;
};

const winnerRaffleBuysTemplate = (winner, campaign, ad) => {
  return `
<b>${campaign?.campaing_type} Competition Completed</b>

🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉
<b>Winner</b>
<code>${winner.buyer_address} ➖ ${numberToUsd(winner.buyer_amount)}</code>


🏆 Prize: <b>${campaign?.prize}</b>
${ad ? "\n\n——\n\n" + ad : ""}
`;
};

module.exports = {
  generalBuyTemplate,
  countdowToStartTemplate,
  campaignBiggestBuysTemplate,
  campaignRaffleBuysTemplate,
  campaignLastBuyTemplate,
  winnerBiggestBuysTemplate,
  winnerRaffleBuysTemplate,
};
