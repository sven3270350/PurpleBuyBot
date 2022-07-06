from xmlrpc.client import Boolean
from services.web3_service import Web3Service
from models import db, Group, Wallet, SupportedChain, TrackedToken


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

    def get_supported_chains(self):
        chains = SupportedChain.query.all()
        return chains

    def get_tracked_tokens(self, group_id):
        tokens = TrackedToken.query.filter_by(group_id=str(group_id)).all()
        return tokens
