const generalBuyTemplate = (trackedToken, amounts, buyer, ad = "") => {
  return `
🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢

New <b>${trackedToken.token_name} </b> Buy!

<b>Paid</b>: <i>${amounts.amountIn} (${amounts.usdPrice})</i>
<b>For</b>: <i>${amounts.amountOut} ${trackedToken.token_symbol}</i>

<b>On</b>: <i>${trackedToken.chain_name}</i>

Buyer: <i>${buyer}</i>

<i>${ad}</i>
`;
};

const countdowToStartTemplate = (startCountdown, EndCountdown, ad) => {
  return `
🕐🕐🕐🕐🕐🕐🕐🕐🕐🕐🕐

<b>Countdown to Buys Competition</b>

<b>Starts: <i>${startCountdown}</i></b>
<b>Ends: <i>${EndCountdown}</i></b>

${ad}
`;
};

module.exports = {
  generalBuyTemplate,
  countdowToStartTemplate,
};
