const CoinGecko = require("coingecko-api");
const appConfig = require("../utils/app_config");

class CoingeckoService {
  static prices = undefined;

  async cachePrices() {
    const CoinGeckoClient = new CoinGecko();
    const ids = appConfig.getAllCoingeckoIds();
    const { data } = await CoinGeckoClient.simple.price({
      ids: Object.values(ids),
      vs_currencies: "usd",
    });

    if (data) {
      this.prices = data;
      console.log("[CoingeckoService::cachePrices] prices cached");
    }
  }

  async getUsdPrice(paired_with) {
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
}

module.exports = CoingeckoService;
