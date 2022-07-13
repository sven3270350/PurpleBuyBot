from web3 import Web3, middleware
from eth_account import Account
import secrets
from web3.middleware import geth_poa_middleware
from helpers.app_config import AppConfigs
from models import db, Wallet, Subscription, TrackedToken, ActiveCompetition, BiggestBuyCampaign
from decouple import config
from datetime import datetime, timedelta


class Web3Service:
    # create a unique wallet address for each group and save the address and private key
    def create_wallet(self):
        # create a new wallet
        key = secrets.token_hex(32)
        wallet_private_key = "0x" + key
        wallet = Account.from_key(wallet_private_key)
        wallet_address = wallet.address
        return wallet_address, wallet_private_key

    # listen for new deposits on wallet address and move the funds to the admin wallet
    def listen_for_deposits(self, group_id):
        # get the wallet address and private key from the database
        wallet_instance = Wallet.query.filter_by(group_id=group_id).first()
        wallet_address = wallet_instance.wallet_address
        wallet_private_key = wallet_instance.wallet_private_key

        # create a web3 instance with the wallet address and private key
        web3 = Web3(Web3.WebsocketProvider(config('WEB3_PROVIDER')))

        web3.middleware_stack.inject(geth_poa_middleware, layer=0)

        # listen for new deposits on the wallet address
        web3.eth.watch(wallet_address)
        # get the admin wallet address from env file
        admin_wallet_address = config('ADMIN_WALLET_ADDRESS')
        #  create a new transaction to move the funds to the admin wallet
        transaction = {
            'from': wallet_address,
            'to': admin_wallet_address,
            'value': web3.eth.getBalance(wallet_address)
        }

        # sign the transaction with the private key
        signed_transaction = web3.eth.account.signTransaction(
            transaction, wallet_private_key)

        # send the transaction
        tx_hash = web3.eth.sendRawTransaction(
            signed_transaction.rawTransaction)
        # get the transaction hash
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        # if transaction completed successfully, create a weekly subscription for the group for which the end date is set to the next week
        if tx_receipt.status == 1:
            subscription_instance = Subscription(group_id, wallet_address,
                                                 datetime.now(), datetime.now() + timedelta(days=7), 'weekly', 'active', tx_hash)
            db.session.add(subscription_instance)
            db.session.commit()
        return tx_receipt

    # for each each token tracked by the group, listen for new buys on the pair and save the transaction to the database for the active campaign
    def listen_for_buys(self, group_id):
        # get group's tracked tokens from the database
        tokens = TrackedToken.query.filter_by(group_id=group_id).all()
        minimum_buy_amount = AppConfigs().get_minimum_buy_amount()

        # get active competion from the database
        active_competition = ActiveCompetition.query.filter_by(
            group_id=group_id).first()
        competition_type = active_competition.competition_type
        competition_id = active_competition.competition_id

        # if competition type is BiggestBuy, get the minimum buy amount from the database
        if competition_type == 'BiggestBuy':
            biggest_buy_campaign = BiggestBuyCampaign.query.filter_by(
                id=competition_id).first()
            minimum_buy_amount = biggest_buy_campaign.minimum_buy_amount

        # for each token, listen for new buys on the pair
        for token in tokens:
            # get pair address
            pair_address = token.pair_address
            pass

    # given token1 address, token2 address, and chain return the token1 name, token1 symbol, token1 decimal and pair address

    def get_token_info(self, token1_address, pair_token1, factory_address, chain):
        provider = AppConfigs().get_provider(chain)
        web3 = Web3(Web3.HTTPProvider(provider))

        token0 = Web3.toChecksumAddress(token1_address)
        token1 = Web3.toChecksumAddress(pair_token1)
        factory_add = Web3.toChecksumAddress(factory_address)

        # get token1 name, symbol, decimal
        token = web3.eth.contract(
            address=token0, abi=AppConfigs().get_erc20_abi()
        )

        token1_name = token.functions.name().call()
        token1_symbol = token.functions.symbol().call()
        token1_decimal = token.functions.decimals().call()

       # get pair address
        factory = web3.eth.contract(
            address=factory_add, abi=AppConfigs().get_factory_abi()
        )

        pair_address = factory.functions.getPair(token0, token1).call()

        return token1_name, token1_symbol, token1_decimal, pair_address
