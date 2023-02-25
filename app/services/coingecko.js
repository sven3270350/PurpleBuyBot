const CoinGecko = require("coingecko-api");
const appConfig = require("../utils/app_config");

class CoingeckoService {
  static prices = undefined;
  static numberToUsd = (amount) => {
    return Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  async cachePrices() {
    const CoinGeckoClient = new CoinGecko();
    const ids = appConfig.getAllCoingeckoIds();
    const { data } = await CoinGeckoClient.simple.price({
      ids: Object.values(ids),
      vs_currencies: "usd",
    });

    if (data) {
      CoingeckoService.prices = data;
      console.log("[CoingeckoService::cachePrices] prices cached");
    }
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

    return CoingeckoService.prices[pairs[id]]?.usd;
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
