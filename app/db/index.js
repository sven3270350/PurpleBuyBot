const { Pool } = require("pg");
console.log("Database env var test:", process.env.DATABASE_URL);
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 3,
  ssl: {
    rejectUnauthorized: false, //this has to be set true in production -s
  },
});

pool.on('connect', (client) => {
  console.log('!!Database connection successful!!');
});

pool.on('error', (err) => {
  console.error('!!Error establishing the DB connection!!', err)
  process.exit(-1)
})

module.exports = {
  query: (text, params) => {
    return pool.query(text, params)
      .catch(err => {
        console.error('Error executing query', err);
        throw err;
      });
  },
  pool: pool,
};
