const generalBuyTemplate = (
  tokenName,
  tokenSymbol,
  amountIn,
  usdPrice,
  amountOut,
  chainName,
  buyer,
  ad = ""
) => {
  return `
🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢

New <b>${tokenName} </b> Buy!

<b>Paid</b>: <i>${amountIn} (${usdPrice})</i>
<b>For</b>: <i>${amountOut} ${tokenSymbol}</i>

<b>On</b>: <i>${chainName}</i>

Buyer: <i>${buyer}</i>

${ad}
`;
};

module.exports = {
  generalBuyTemplate,
};
