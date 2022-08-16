const generalBuyTemplate = (trackedToken, amounts, buyer, tx_link, ad = "") => {
  return `
🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢

New <b>${trackedToken.token_name} </b> Buy!

<b>Paid</b>: <i>${amounts.amountIn} (${amounts.usdPrice})</i>
<b>For</b>: <i>${amounts.amountOut} ${trackedToken.token_symbol}</i>

<b>On</b>: <i>${trackedToken.chain_name}</i>

Buyer: <a href='${tx_link}'><i>${buyer}</i></a>

——

<i>${ad}</i>
`;
};

const countdowToStartTemplate = (startCountdown, EndCountdown, ad) => {
  return `
🕐🕐🕐🕐🕐🕐🕐🕐🕐🕐🕐

<b>Countdown to buys contest</b>

<b>Starts: <i>${startCountdown}</i></b>
<b>Ends: <i>${EndCountdown}</i></b>

——

${ad}
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

  const templates = `
🥇 0x46b0…1974 ➖ 1.2 BNB
🥈 0xc351…4bf7 ➖ 0.75 BNB
🥉 0x7171…4ee6 ➖ 0.7 BNB
4️⃣ 0xdfd0…4815 ➖ 0.54 BNB
5️⃣ 0x3fa6…d50a ➖ 0.5 BNB
`;

  return `
<b>🎉 ${campaign.type} Competition Started</b>

🕓 Started at: <b>${times.start_time}</b>
⏳ Ends in: <b>${times.count_down}</b>
⬇️ Minimum Buy: <b>${Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(campaign.min_buy)}</b>
🏆 Prize: <b>${campaign.prize}</b>

<b>Top 5</b>
${templates}

🎖 Top buyer <b><i>${leading.address || "take this spot 😉?"}</i></b>  ${
    leading.amount || ""
  }

🆕 <b>New Entry:</b>

😎 <b>Buyer :</b> <i><a href='${new_buyer.tx_link}'>${new_buyer.to}</a></i>
🤑 <b>Amount :</b> <i>${new_buyer.amountOut} (~${new_buyer.usdPrice})</i>

⛓ <b>Bought On:</b> <i>${new_buyer.chain_name}</i>

——

<i>${ad || "Premium"}</i>
`;
};

module.exports = {
  generalBuyTemplate,
  countdowToStartTemplate,
  campaignBiggestBuysTemplate,
};
