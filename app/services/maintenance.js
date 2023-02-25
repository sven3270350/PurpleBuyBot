const { cleanDatabase, deleteBlacklistedTokens } = require("../db/queries");

class MaintenanceService {
  async cleanDB() {
    await cleanDatabase();
  }

  async deleteBlacklisted() {
    await deleteBlacklistedTokens();
  }
}

module.exports = new MaintenanceService();
