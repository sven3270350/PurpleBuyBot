const { Pool } = require("pg");
console.log("Database env var test:", process.env.DATABASE_URL);

let pool;
let isPoolCreated = false;

function createPool() {
  pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 3,
    ssl: {
      rejectUnauthorized: false, //this has to be set true in production -s
    },
  });

  pool.on('connect', (client) => {
    if (!isPoolCreated) {
      console.log('!!Database connection successful!!');
      isPoolCreated = true;
    }
  });

  pool.on('error', (err) => {
    console.error('!!Error establishing the DB connection!!', err)
    process.exit(-1)
  });

  return pool;
}

// Export a singleton instance of the connection pool
module.exports = {
  query: (text, params) => {
    if (!pool) {
      createPool();
    }
    return pool.connect()
      .then(client => {
        return client.query(text, params)
          .then(result => {
            client.release()
            return result
          })
          .catch(err => {
            client.release()
            console.error('Error executing query', err)
            throw err
          })
      })
      .catch(err => {
        console.error('Error acquiring client from pool', err)
        throw err
      })
  },
  pool: () => {
    if (!pool) {
      createPool();
    }
    return pool;
  },
};
