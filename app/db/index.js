const { Pool } = require("pg");
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 3,
  ssl: {
    rejectUnauthorized: false,
  },
});


module.exports = {
  query: (text, params) => pool.query(text, params),
  pool: pool,
};
