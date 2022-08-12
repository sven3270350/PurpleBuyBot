const selectTrackedToken = async (trackedToken, contract) => {
  const token0 = await getToken0(contract);
  const token1 = await getToken1(contract);

  if (trackedToken === token0) {
    return token1;
  } else {
    return token0;
  }
};

const getToken0 = async (contract) => {
  return contract.methods.token0().call();
};

const getToken1 = async (contract) => {
  return contract.methods.token1().call();
};

module.exports = {
  selectTrackedToken,
  getToken0,
  getToken1,
};
