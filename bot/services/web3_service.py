from decimal import Decimal
from web3 import Web3
from eth_account import Account
import secrets
from web3.middleware import geth_poa_middleware
from helpers.utils import decimals_to_unit
from helpers.app_config import AppConfigs
from models import Wallet
from decouple import config
from datetime import datetime

admin_wallet = config('ADMIN_WALLET_ADDRESS')


class Web3Service:
    # create a unique wallet address for each group and save the address and private key
    def create_wallet(self):
        # create a new wallet
        key = secrets.token_hex(32)
        wallet_private_key = "0x" + key
        wallet = Account.from_key(wallet_private_key)
        wallet_address = wallet.address
        return wallet_address, wallet_private_key

    def get_wallet_balance(self, chain_id, wallet_address):
        provider = AppConfigs().get_provider(chain_id)
        web3 = Web3(Web3.HTTPProvider(provider))
        return web3.eth.get_balance(Web3.toChecksumAddress(wallet_address))

    def transfer_balance_to_admin(self, chain_id, wallet_id):
        provider = AppConfigs().get_provider(chain_id)
        web3 = Web3(Web3.HTTPProvider(provider))

        wallet: Wallet = Wallet.query.filter_by(id=wallet_id).first()

        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        web3.eth.default_account = wallet.wallet_address

        nonce = web3.eth.get_transaction_count(wallet.wallet_address)
        gas_price = web3.eth.gas_price
        balance = web3.eth.get_balance(
            Web3.toChecksumAddress(wallet.wallet_address))
        tx_fee = gas_price * 21000

        if tx_fee/balance > Decimal(0.25):
            return False

        # build a transaction in a dictionary
        tx = {
            'nonce': nonce,
            'to':  Web3.toChecksumAddress(admin_wallet),
            'value': (balance - tx_fee),
            'gas': 21000,
            'gasPrice': gas_price
        }

        # sign the transaction
        signed_tx = web3.eth.account.sign_transaction(
            tx, wallet.wallet_private_key)

        # send transaction
        web3.eth.sendRawTransaction(signed_tx.rawTransaction)

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

        # get reserves and check if token0 is greater than 0
        try:
            pair = web3.eth.contract(
                address=pair_address, abi=AppConfigs().get_pair_abi()
            )
            (token0_reserve, token1_reserve,
             _blockTimestampLast) = pair.functions.getReserves().call()
            return token1_name, token1_symbol, token1_decimal, pair_address, int(token0_reserve) > 0
        except Exception as e:
            print(e)
            return token1_name, token1_symbol, token1_decimal, pair_address, False

    # given chainId and transaction hash, return the transaction receipt
    def get_transaction_receipt(self, chain_id, tx_hash):
        provider = AppConfigs().get_provider(chain_id)
        web3 = Web3(Web3.HTTPProvider(provider))
        tx_receipt = web3.eth.get_transaction(tx_hash)
        return tx_receipt

    def wait_for_tx_receipt(self, chain_id, tx_hash):
        provider = AppConfigs().get_provider(chain_id)
        web3 = Web3(Web3.HTTPProvider(provider))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def get_block_timestamp(self, chain_id, block_number):
        provider = AppConfigs().get_provider(chain_id)
        web3 = Web3(Web3.HTTPProvider(provider))
        block = web3.eth.get_block(block_number)
        return datetime.fromtimestamp(block.timestamp)

    def get_readable_amount(self, amount, decimals):
        return Web3.fromWei(amount, decimals_to_unit(int(decimals)))

    def ellipse_address(self, address):
        return address[:6] + "..." + address[-4:]

    def get_swap_event_from_pair_address(self, chain_id, pair_address):
        provider = AppConfigs().get_provider(chain_id)
        web3 = Web3(Web3.HTTPProvider(provider))
        pair = web3.eth.contract(
            address=pair_address, abi=AppConfigs().get_pair_abi()
        )
        return pair.events.Swap.createFilter(fromBlock='latest')

    def swap_even_handler(self, pair: str, data: dict):
        amount_0_in = data.get('amount0In')
        amount_1_out = data.get('amount1Out')
        to = data.get('to')

        if amount_0_in > 0:
            return {
                'pair': pair,
                'amount0In': amount_0_in,
                'amount1Out': amount_1_out,
                'to': to
            }
        else:
            return None
