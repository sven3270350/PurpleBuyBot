from services.web3_service import Web3Service
from models import db, Group, Wallet, SupportedChain, TrackedToken, SupportedExchange, SupportedPairs, token_chains, token_pairs, token_dexs
from telegram.ext import CallbackContext
from telegram import Update, ParseMode


class BotService:

    def create_new_bot_user(self, chat_id, chat_title, username) -> bool:

        try:
            group_instance = Group(chat_id, chat_title, username)
            (wallet_address, wallet_private_key) = Web3Service().create_wallet()
            group_instance.wallet = Wallet(wallet_address, wallet_private_key)
            db.session.add(group_instance)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error creating new bot user: {e}")
            return False

    def is_registered_group(self, chat_id):
        group = Group.query.filter_by(group_id=chat_id).first()
        if group:
            return True
        else:
            return False

    def is_chat_admin(self, context: CallbackContext,  chat_id, user_id):
        admins = [admin.user.id
                  for admin in context.bot.get_chat_administrators(chat_id)]
        return user_id in admins

    def get_supported_chains(self, chain_id=None):

        if chain_id is None:
            chains = SupportedChain.query.all()
            return chains
        else:
            chains = SupportedChain.query.filter_by(chain_id=chain_id).first()
            return chains

    def get_supported_dexes(self, chain_index):
        dex = SupportedExchange.query.filter_by(chain_id=chain_index).all()
        return dex

    def get_supported_dex_by_id(self, dex_id):
        dex = SupportedExchange.query.filter_by(id=dex_id).first()
        return dex

    def get_tracked_token_by_id(self, token_id):
        token = TrackedToken.query.filter_by(id=token_id).first()
        return token

    def get_supported_pairs(self, chain_index):
        pairs = SupportedPairs.query.filter_by(chain_id=chain_index).all()
        return pairs

    def get_supported_pair_by_id(self, pair_id):
        pair = SupportedPairs.query.filter_by(id=pair_id).first()
        return pair

    def get_tracked_tokens(self, group_id):
        tokens = TrackedToken.query.filter_by(group_id=str(group_id)).all()
        return tokens

    def is_token_set_for_chain(self, group_id, chain_id):
        tokens = TrackedToken.query.filter(TrackedToken.group_id == str(
            group_id), TrackedToken.chain.any(SupportedChain.chain_id == chain_id)).all()
        if tokens:
            return True
        else:
            return False

    def get_tracked_tokens_by_group_id(self, group_id):
        stmt = f'''
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
        WHERE tk.group_id = '{group_id}';
        '''
        return list(db.engine.execute(stmt))

    def get_tracked_tokens_for_removal(self, group_id):
        stmt = f'''
        SELECT
        tk.id, tk.token_name,
        sc.chain_name
        FROM public.tracked_token tk
        JOIN public.token_chains tc
        ON tk.id = tc.token_id
        JOIN public.supported_chain sc
        ON sc.id = tc.chain_id
        WHERE tk.group_id = '{group_id}';
        '''

        return list(db.engine.execute(stmt))

    def delete_tracked_token(self, token_id):
        try:
            token = TrackedToken.query.filter_by(id=token_id).first()
            token.chain = []
            db.session.delete(token)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error deleting tracked token: {e}")
            return False

    def is_group_in_focus(self, update: Update, context: CallbackContext):
        group_id = context.chat_data.get('group_id', None)

        if group_id is None:
            update.message.reply_text(
                text="<i> ❌ No group in focus; use group link first. </i>",
                parse_mode=ParseMode.HTML)
            return False

        return True
