from services.web3_service import Web3Service
from models import db, Group, Wallet, SupportedChain


class BotService:

    def create_new_bot_user(self, chat_id, chat_title):
        group_instance = Group(chat_id, chat_title)
        (wallet_address, wallet_private_key) = Web3Service().create_wallet()
        group_instance.wallet = Wallet(wallet_address, wallet_private_key)
        db.session.add(group_instance)
        db.session.commit()

    def get_supported_chains(self):
        chains = SupportedChain.query.all()
        return chains
