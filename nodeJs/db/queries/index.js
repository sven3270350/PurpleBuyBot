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

const getAllActivelyTrackedTokens = async () => {
  const query = `
    SELECT
    tk.group_id,  tk.token_name, tk.token_address,
    tk.token_symbol, tk.token_decimals, tk.pair_address as pair,
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
    WHERE tk.active_tracking = true;
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

module.exports = {
  getTrackedTokensById,
  getActiveSubscriptionByGroupId,
  getAllActivelyTrackedTokens,
};
