const Moralis = require("moralis").default;
const appConfig = require("../utils/app_config");
const moralis_key =
  "yh7eNtVqRRVf6s8ftrT4RY10k2FBG9YeghrsJuhkyx7unp6PDK7y3IDAZQvCsQpg";
let isStarted = true;

const start = async () => {
  await Moralis.start({
    apiKey: moralis_key,
  });
  isStarted = false;
};

class CoingeckoService {
  static prices = undefined;
  static numberToUsd = (amount) => {
    return Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  async cachePrices() {
    try {
      isStarted && (await start());
      const ids = appConfig.getAllMoralisIds();
      const response = await Promise.all(
        Object.values(ids).map(async (value) => {
          return await Moralis.EvmApi.token.getTokenPrice({
            chain: value.chain,
            exchange: value.exchange,
            address: value.address,
          });
        })
      );
      const data = {};
      response.map(
        (value, index) =>
          (data[ids[index].name] = value.ResponseAdapter.jsonResponse.usdPrice)
      );

      CoingeckoService.prices = data;
      console.log("[CoingeckoService::cachePrices] prices cached");
    } catch (e) {
      console.error(e);
    }
    // const CoinGeckoClient = new CoinGecko();
    // const ids = appConfig.getAllCoingeckoIds();
    // const { data } = await CoinGeckoClient.simple.price({
    //   ids: Object.values(ids),
    //   vs_currencies: "usd",
    // });

    // if (data) {
    //   CoingeckoService.prices = data;
    //   console.log("[CoingeckoService::cachePrices] prices cached");
    // }
  }

  async getPairPrice(paired_with) {
    const id = paired_with.toLowerCase();
    const pairs = {
      eth: "ethereum",
      bnb: "binancecoin",
      cro: "crypto-com-chain",
      usdt: "tether",
      busd: "binance-usd",
      usdc: "usd-coin",
    };

    if (!CoingeckoService.prices) {
      await this.cachePrices();
    }

    return CoingeckoService.prices[pairs[id]];
  }

  async getUsdPrice(amount, paired_with) {
    const price = await this.getPairPrice(paired_with);
    return {
      usdString: CoingeckoService.numberToUsd(Number(amount) * price),
      usdNumber: Number(amount) * price,
      actualPrice: price,
    };
  }
}

module.exports = CoingeckoService;
