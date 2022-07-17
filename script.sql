SELECT 
tk.id, tk.token_name, tk.token_address, 
tk.token_symbol, tk.group_id, 
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
ON se.id = td.exchange_id;



-- DROP TABLE active_competition, alembic_version, biggest_buy_campaign, biggest_buy_transaction, Public."group", raffle_campaign, raffle_transaction, Public."subscription", supported_chain, supported_exchange, supported_pairs, token_chains, tracked_token, wallet;

-- INSERT INTO PUBLIC.supported_chain (chain_name, chain_id)
-- VALUES ('Ethereum', 1), ('Binance Smart Chain', 56), ('Cronos', 25);


-- INSERT INTO PUBLIC.supported_exchange 
-- (exchange_name, router_address, chain_id, factory_address)
-- VALUES 
-- ('UniSwap V2', '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', 1, '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'), 
-- ('SushiSwap', '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F', 1, '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'),
-- ('PancakeSwap', '0x10ED43C718714eb63d5aA57B78B54704E256024E', 56, '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'), 
-- ('VVS', '0x145863Eb42Cf62847A6Ca784e6416C1682b1b2Ae', 25, '0x3B44B2a187a7b3824131F8db5a74194D0a42Fc15'),
-- ('MMF', '0x145677FC4d9b8F19B5D56d1820c48e0443049a30', 25, '0xd590cC180601AEcD6eeADD9B7f2B7611519544f4');

-- INSERT INTO PUBLIC.supported_pairs
-- (pair_name, pair_address, chain_id)
-- VALUES
-- ('WETH', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 1),
-- ('USDT', '0xdAC17F958D2ee523a2206206994597C13D831ec7', 1), 
-- ('USDC', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 1),
-- ('WBNB', '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', 56),
-- ('BUSD', '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56', 56),
-- ('USDC', '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d', 56),
-- ('WCRO', '0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23', 25),
-- ('USDT', '0x66e428c3f67a68878562e79A0234c1F83c208770', 25),
-- ('USDC', '0xc21223249CA28397B4B6541dfFaEcC539BfF0c59', 25);

-- select(
--     [TrackedToken.id.label('tracked_token_id'), TrackedToken.token_name, TrackedToken.token_address, TrackedToken.token_symbol, TrackedToken.group_id, SupportedChain.chain_name]).select_from(
--         SupportedChain.__tablename__.outerjoin(TrackedToken, SupportedChain.chain_id==TrackedToken.chain.chain_id)
--     )
