const config = require("config");

const getExploerUrl = (chainId) => {
  const explorers = {
    1: "etherscan",
    56: "bscscan",
    25: "cronoscan",
    42161: "arbiscan",
    3: "ropsten",
    97: "bscTestnet",
    338: "croTest",
  };

  const key = explorers[chainId];
  return config.get(`EXPLORERS.${key}`);
};

const getDexChartUrl = (chainId) => {
  const dexChart = {
    1: "ethdex",
    56: "bscdex",
    25: "crodex",
    42161: "arbdex",
  };
  const key = dexChart[chainId];
  return config.get(`DEX_EXPLORERS.${key}`);
};

const getChain = (chainId) => {
  const chain_name = {
    1: "ETH",
    56: "BSC",
    25: "CRO",
    42161: "Arbitrum",
    3: "Ropsten",
    97: "BSCTestnet",
    338: "CROTestnet",
  };
  return chain_name[chainId];
};

const getProvider = (chainId) => {
  const providers = {
    1: "ethProvider",
    56: "bscProvider",
    25: "croProvider",
    42161: "arbProvider",
    3: "testnetEthProvider",
    97: "testnetBscProvider",
    338: "testnetCroProvider",
  };
  const key = providers[chainId];
  return config.get(`WEB3_PROVIDER.${key}`);
};

const getCoinGeckoId = (chainId) => {
  const chains = {
    1: "ethid",
    56: "bscid",
    25: "croid",
    42161: "ethid",
    3: "ethid",
    97: "bscid",
    338: "croid",
  };
  const key = chains[chainId];
  return config.get(`COINGECKO_IDS.${key}`);
};

const getAllCoingeckoIds = () => {
  return config.get(`COINGECKO_IDS`);
};

const trending_group_id = "-1001778462627";

module.exports = {
  getExploerUrl,
  getChain,
  getProvider,
  getCoinGeckoId,
  getAllCoingeckoIds,
  getDexChartUrl,
  trending_group_id,
};
