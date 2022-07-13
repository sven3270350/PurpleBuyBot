from xmlrpc.client import Boolean
from services.web3_service import Web3Service
from models import db, Group, Wallet, SupportedChain, TrackedToken, SupportedExchange, SupportedPairs
from telegram.ext import CallbackContext


class BotService:

    def create_new_bot_user(self, chat_id, chat_title, username) -> Boolean:

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

    def get_supported_pairs(self, chain_index):
        pairs = SupportedPairs.query.filter_by(chain_id=chain_index).all()
        return pairs

    def get_supported_pair_by_id(self, pair_id):
        pair = SupportedPairs.query.filter_by(id=pair_id).first()
        return pair

    def get_tracked_tokens(self, group_id):
        tokens = TrackedToken.query.filter_by(group_id=str(group_id)).all()
        return tokens

    def add_token_for_group(self, group_id, token_address):

        # get token symbol, decimal and name from the token address
        # save the token to the database

        # get pair address from the token address
        # reply with round pair address
        pass
