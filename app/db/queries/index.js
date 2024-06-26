const db = require("../index");

const getTrackedTokensById = async (group_id) => {
  const query = `
    SELECT
    tk.group_id,  tk.token_name, tk.token_address,
    tk.token_symbol, tk.circulating_supply,
    CONCAT(tk.token_symbol, '/', sp.pair_name ) as pair_symbol,
    sc.chain_name, sc.chain_id,
    sp.pair_name, sp.pair_address,
    se.exchange_name, se.router_address
    FROM public.tracked_token tk
    JOIN public.token_chains tc
    ON tk.id = tc.token_id
    JOIN public.supported_chain sc
    ON sc.id = tc.chain_id
    JOIN public.token_pairs tp
    ON tk.id = tp.token_id
    JOIN public.supported_pairs sp
    ON sp.id = tp.pair_id
    JOIN public.token_dexs td
    ON tk.id = td.token_id
    JOIN public.supported_exchange se
    ON se.id = td.exchange_id
    WHERE tk.group_id = $1;
    `;
  const params = [group_id];
  const res = await db.query(query, params);
  return res.rows;
};

const getAllActivelyTrackedTokensNoActiveCampaign = async () => {
  const query = `
  SELECT
  DISTINCT 
  gp.buy_icon, gp.buy_media, tk.id, tk.group_id, tk.circulating_supply,  tk.token_name, tk.token_address,
  tk.token_symbol, tk.token_decimals, tk.pair_address as pair, tk.active_tracking, tk.min_usd_amount,
  sc.chain_name, sc.chain_id,
  sp.pair_name as paired_with_name, sp.pair_address as paired_with
  FROM public.tracked_token tk
  JOIN public.group gp
  ON tk.group_id = gp.group_id
  JOIN public.token_chains tc
  ON tk.id = tc.token_id
  JOIN public.supported_chain sc
  ON sc.id = tc.chain_id
  JOIN public.token_pairs tp
  ON tk.id = tp.token_id
  JOIN public.supported_pairs sp
  ON sp.id = tp.pair_id
  WHERE 
  (
      SELECT COUNT(*) 
       FROM public.campaigns 
      WHERE public.campaigns.start_time <= NOW() 
      AND  
      public.campaigns.end_time >= NOW() 
      AND tk.group_id =  public.campaigns.group_id
  ) < 1
  AND tk.active_tracking = true;
    `;
  const res = await db.query(query);
  return res.rows;
};

const getAllActivelyTrackedTokensWithActiveCampaign = async () => {
  const query = `
  SELECT
  tk.id, tk.group_id,  tk.token_name, tk.token_address, tk.circulating_supply, tk.min_usd_amount,
  tk.token_symbol, tk.token_decimals, tk.pair_address as pair,
  sc.chain_name, sc.chain_id,
  sp.pair_name as paired_with_name, sp.pair_address as paired_with,
  cp.id as campaign_id, cp.start_time, cp.end_time, cp.campaing_type, cp.min_amount, cp.prize 
  FROM public.tracked_token tk
  JOIN public.token_chains tc
  ON tk.id = tc.token_id
  JOIN public.supported_chain sc
  ON sc.id = tc.chain_id
  JOIN public.token_pairs tp
  ON tk.id = tp.token_id
  JOIN public.supported_pairs sp
  ON sp.id = tp.pair_id
  JOIN public.campaigns cp
  ON cp.group_id = tk.group_id
  WHERE cp.start_time <= NOW() AND cp.end_time >= NOW();
    `;
  const res = await db.query(query);
  return res.rows;
};

const getActiveSubscriptionByGroupId = async (group_id) => {
  const query = `
        SELECT 
        st.subscription_type,
        ss.start_date, ss.end_date,
        ss.number_of_countable_subscriptions AS total,
        ss.is_life_time_subscription AS for_life,
        CASE 
            WHEN ss.end_date >= NOW() THEN 'active'
            ELSE 'inactive'
        END AS status
        FROM PUBLIC.subscription ss
        JOIN public.subscription_type st
        ON st.id = ss.subscription_type_id
        WHERE ss.group_id = $1 AND ss.end_date >= NOW();
        `;
  const params = [group_id];
  const res = await db.query(query, params);
  return res.rows;
};

const getAllActiveCampaigns = async () => {
  const query = `
  SELECT * FROM public.campaigns WHERE start_time <= NOW() AND end_time >= NOW()
  ;
    `;
  const res = await db.query(query);
  return res.rows;
};

const getAllUpcomingCampaigns = async () => {
  const query = `
    SELECT * FROM public.campaigns WHERE start_time > NOW();
    `;
  const res = await db.query(query);
  return res.rows;
};

const getGroupActiveCampaign = async (group_id) => {
  const query = `
  SELECT * 
    FROM public.campaigns 
    WHERE public.campaigns.start_time <= NOW() 
    AND  
    public.campaigns.end_time >= NOW() 
    AND public.campaigns.group_id = $1;
    `;
  const params = [group_id];
  const res = await db.query(query, params);

  return res.rows[0];
};

const getActiveAd = async () => {
  const query = `
  SELECT advert FROM public.advertisement WHERE "isActive" = true;
    `;
  const res = await db.query(query);
  return res.rows;
};

const writeAllBuysToDB = async (buys) => {
  const query = `
  INSERT INTO public.all_transactions (
    buyer_address,
    buyer_amount,
    transaction_link,
    transaction_chain,
    group_id,
    token_name
    )
  VALUES ($1, $2, $3, $4, $5, $6);
  `;
  const params = [
    buys.buyer_address,
    buys.buyer_amount,
    buys.transaction_link,
    buys.transaction_chain,
    buys.group_id,
    buys.token_name,
  ];
  const res = await db.query(query, params);
  return res.rows[0];
};

const writeBuysToDB = async (buys) => {
  const query = `
  INSERT INTO public.transactions (
    group_id,
    campaign_id,
    buyer_address,
    buyer_amount,
    transaction_link,
    transaction_chain,
    campaing_type
  )
  VALUES ($1, $2, $3, $4, $5, $6, $7)
  RETURNING *;
  `;
  const params = [
    buys.group_id,
    buys.campaign_id,
    buys.buyer_address,
    buys.buyer_amount,
    buys.transaction_link,
    buys.transaction_chain,
    buys.campaing_type,
  ];
  const res = await db.query(query, params);
  return res.rows[0];
};

const getTop5Buys = async (campaign_id) => {
  const query = `
  SELECT
  *,
    RANK() OVER (ORDER BY t.amount DESC) AS campaignRank
  FROM (
    SELECT
      group_id,
      buyer_address,
      SUM(buyer_amount) AS amount
    FROM public.transactions
    WHERE campaign_id = $1
    GROUP BY group_id, buyer_address
  ) AS t
  ORDER BY campaignRank LIMIT 5;
    `;
  const params = [campaign_id];
  const res = await db.query(query, params);
  return res.rows;
};

const deleteNonTop5Buys = async (campaign_id) => {
  const query = `
  DELETE FROM public.transactions
  WHERE campaign_id = $1
  AND buyer_address NOT IN (
    SELECT buyer_address
    FROM (
      SELECT
        group_id,
        buyer_address,
        SUM(buyer_amount) AS amount
      FROM public.transactions
      WHERE campaign_id = $1
      GROUP BY group_id, buyer_address
    ) AS t
    ORDER BY amount DESC LIMIT 5
  );
    `;
  const params = [campaign_id];
  const res = await db.query(query, params);
  return res.rows;
};

const getTrendingGroups = async () => {
  const query = `
  SELECT
    group_id,
    count(*) as transactions,
    sum(buyer_amount) as volume,
	RANK() OVER (ORDER BY  count(*) DESC) AS "rank"
  FROM public.all_transactions
  WHERE
    all_transactions.buy_date > (NOW() - INTERVAL '4 HOUR')
  GROUP BY group_id
  ORDER BY
    transactions DESC,
    volume DESC
  LIMIT 10;
  `;
  const res = await db.query(query);
  return res.rows;
};

const getRandomWinner = async (campaign_id) => {
  const query = `
  SELECT * FROM public.transactions WHERE campaign_id = $1 ORDER BY RANDOM() LIMIT 1;
    `;
  const params = [campaign_id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const getLastBuy = async (campaign_id) => {
  const query = `
  SELECT * FROM public.transactions WHERE campaign_id = $1 ORDER BY id DESC LIMIT 1;
    `;
  const params = [campaign_id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const deleteNonRandomWinner = async (campaign_id) => {
  const query = `
  DELETE FROM public.transactions
  WHERE campaign_id = $1
  AND buyer_address != (
    SELECT campaign_winner
    FROM public.campaigns
    WHERE id = $1
  );
    `;
  const params = [campaign_id];
  const res = await db.query(query, params);
  return res.rows;
};

const getOdds = async (campaign_id) => {
  const query = `
  SELECT COUNT(*) FROM public.transactions WHERE campaign_id = $1;
    `;
  const params = [campaign_id];
  const res = await db.query(query, params);
  return `1 in ${res.rows[0].count}`;
};

const writeWinnerToCampaign = async (address, id) => {
  const query = `
  UPDATE public.campaigns
  SET campaign_winner = $1
  WHERE id = $2;
    `;
  const params = [address, id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const setWinnerAndEndContest = async (address, id) => {
  const query = `
  UPDATE public.campaigns
  SET campaign_winner = $1, end_time = NOW()
  WHERE id = $2;
    `;
  const params = [address, id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const deleteTrackedToken = async (group_id) => {
  const client = await db.pool.connect();
  try {
    await client.query("BEGIN");
    const deleteTokenChain = `
    DELETE FROM public.token_chains 
    WHERE token_chains.token_id
    IN (
      SELECT id 
        FROM public.tracked_token 
        WHERE tracked_token.group_id = $1)
    `;
    const deleteTokenDex = `
    DELETE FROM public.token_dexs
    WHERE token_dexs.token_id
    IN (
      SELECT id 
        FROM public.tracked_token 
        WHERE tracked_token.group_id = $1)
    `;
    const deleteTokenPair = `
    DELETE FROM public.token_pairs
    WHERE token_pairs.token_id
    IN (
      SELECT id 
        FROM public.tracked_token 
        WHERE tracked_token.group_id = $1
    )
    `;

    await Promise.all([
      client.query(deleteTokenChain, [group_id]),
      client.query(deleteTokenDex, [group_id]),
      client.query(deleteTokenPair, [group_id]),
    ]);

    const deleteToken = `
    DELETE FROM public.tracked_token
    WHERE tracked_token.group_id = $1
    `;
    await client.query(deleteToken, [group_id]);

    await client.query("COMMIT");
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
  }
};

const stopGroupActiveCampaign = async (group_id) => {
  const query = `
  UPDATE public.campaigns SET end_time = NOW() WHERE group_id = $1 AND end_time >= NOW();
  `;
  const params = [group_id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const stopCampaingByGroup = async (campaign_id) => {
  const query = `
  UPDATE public.campaigns SET end_time = NOW() WHERE id = $1;
  `;
  const params = [campaign_id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const getGroupIconAndMedia = async (group_id) => {
  const query = `
  SELECT
  buy_icon, buy_media
  FROM public.group
  WHERE group_id = $1;
    `;
  const params = [group_id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const getGroupInviteLink = async (group_id) => {
  const query = `
  SELECT
  group_link
  FROM public.group
  WHERE group_id = $1;
    `;
  const params = [group_id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const updateTrackedTokenCircSupply = async (
  group_id,
  tracked_token_id,
  circ_supply
) => {
  const query = `
  UPDATE public.tracked_token
  SET circulating_supply = $3
  WHERE group_id = $1 AND id = $2;
    `;
  const params = [group_id, tracked_token_id, circ_supply];
  const res = await db.query(query, params);
  return res.rows[0];
};

const getTokenCircSupply = async (tracked_token_id) => {
  const query = `
  SELECT circulating_supply FROM public.tracked_token WHERE id = $1 ORDER BY id DESC LIMIT 1;
    `;
  const params = [tracked_token_id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const getMinUSDBuyAmount = async (group_id) => {
  const query = `
  SELECT
  min_usd_amount as min_usd_amount
  FROM public.tracked_token
  WHERE group_id = $1 ORDER BY id DESC LIMIT 1;
    `;
  const params = [group_id];
  const res = await db.query(query, params);
  return res.rows[0];
};

const cleanDatabase = async () => {
  const client = await db.pool.connect();
  try {
    await client.query("BEGIN");
    const deleteAllTxnsOlderThan2Days = `
    DELETE FROM public.all_transactions WHERE buy_date < NOW() - INTERVAL '2 days'
    `;
    const deleteCampainTxnsOlderThan1Month = `
    DELETE FROM public.transactions 
    WHERE transactions.campaign_id IN (SELECT id FROM public.campaigns WHERE campaigns.end_time < (NOW() - INTERVAL '1 MONTH'));
  `;
    const deleteCampaignsOlderThan1Month = `DELETE FROM public.campaigns WHERE campaigns.end_time < (NOW() - INTERVAL '1 MONTH')`;

    await Promise.all([
      client.query(deleteAllTxnsOlderThan2Days),
      client.query(deleteCampainTxnsOlderThan1Month),
      client.query(deleteCampaignsOlderThan1Month),
    ]);
    await client.query("COMMIT");
    console.log("[DB] Cleaned database");
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  }
};

const deleteBlacklistedTokens = async () => {
  const client = await db.pool.connect();
  try {
    await client.query("BEGIN");
    const deleteTokenChain = `
    DELETE FROM
        public.token_chains
    WHERE
        token_chains.token_id IN (
            SELECT id
            FROM
                public.tracked_token
            WHERE
                tracked_token.token_address IN (
                    SELECT
                        address
                    from
                        public.blacklist
                )
        );`;

    const deleteTokenDex = `   
    DELETE FROM public.token_dexs
    WHERE token_dexs.token_id IN (
            SELECT id
            FROM
                public.tracked_token
            WHERE
                tracked_token.token_address IN (
                    SELECT
                        address
                    from
                        public.blacklist
                )
        )`;

    const deleteTokenPairs = `
    DELETE FROM public.token_pairs
    WHERE token_pairs.token_id IN (
            SELECT id
            FROM
                public.tracked_token
            WHERE
                tracked_token.token_address IN (
                    SELECT
                        address
                    from
                        public.blacklist
                )
        )`;

    const deleteToken = `
    DELETE FROM
        public.tracked_token
    WHERE
        tracked_token.token_address IN (
            SELECT address
            from
                public.blacklist
        )`;

    await Promise.all([
      client.query(deleteTokenChain),
      client.query(deleteTokenDex),
      client.query(deleteTokenPairs),
      client.query(deleteToken),
    ]);

    await client.query("COMMIT");
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  }
};

module.exports = {
  getTrackedTokensById,
  getActiveSubscriptionByGroupId,
  getAllActivelyTrackedTokensNoActiveCampaign,
  getActiveAd,
  getAllActiveCampaigns,
  getAllUpcomingCampaigns,
  getAllActivelyTrackedTokensWithActiveCampaign,
  getGroupActiveCampaign,
  writeAllBuysToDB,
  writeBuysToDB,
  getTrendingGroups,
  getTop5Buys,
  getRandomWinner,
  getOdds,
  writeWinnerToCampaign,
  deleteTrackedToken,
  getGroupIconAndMedia,
  deleteNonTop5Buys,
  deleteNonRandomWinner,
  stopGroupActiveCampaign,
  stopCampaingByGroup,
  updateTrackedTokenCircSupply,
  getTokenCircSupply,
  setWinnerAndEndContest,
  getLastBuy,
  getGroupInviteLink,
  getMinUSDBuyAmount,
  cleanDatabase,
  deleteBlacklistedTokens,
};
