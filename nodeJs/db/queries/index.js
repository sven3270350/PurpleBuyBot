const db = require("../index");

const getTrackedTokensById = async (group_id) => {
  const query = `
    SELECT
    tk.group_id,  tk.token_name, tk.token_address,
    tk.token_symbol,
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
  tk.id, tk.group_id,  tk.token_name, tk.token_address,
  tk.token_symbol, tk.token_decimals, tk.pair_address as pair, tk.active_tracking,
  sc.chain_name, sc.chain_id,
  sp.pair_name as paired_with_name, sp.pair_address as paired_with
  FROM public.tracked_token tk
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
  tk.group_id,  tk.token_name, tk.token_address,
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
  SELECT * FROM public.campaigns WHERE end_time >= NOW();
    `;
  const res = await db.query(query);
  return res.rows;
};

const getAllUpcomingCampaigns = async () => {
  const query = `
    SELECT * FROM public.campaigns WHERE start_time >= NOW();
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

const writeBuysToDB = async (buys) => {
  const query = `
  INSERT INTO public.transactions (
    group_id,
    campaign_id,
    buyer_address,
    buyer_amount,
    transaction_link,
    transaction_chain,
    cmapaign_type
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
    buys.campaign_type,
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

const getRandomWinner = async (campaign_id) => {
  const query = `
  SELECT * FROM public.transactions WHERE campaign_id = $1 ORDER BY RANDOM() LIMIT 1;
    `;
  const params = [campaign_id];
  const res = await db.query(query, params);
  return res.rows[0];
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

const deleteTrackedToken = async (group_id) => {
  const query = `
  UPDATE public.tracked_token SET active_tracking=false WHERE group_id = $1;
    `;
  const params = [group_id];
  const res = await db.query(query, params);
  return res.rows[0];
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
  writeBuysToDB,
  getTop5Buys,
  getRandomWinner,
  getOdds,
  writeWinnerToCampaign,
  deleteTrackedToken,
};
