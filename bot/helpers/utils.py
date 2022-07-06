
import json
from web3 import HTTPProvider, Web3
from helpers.app_config import AppConfigs


def erc20Abi():
    with open("./erc20abi.json") as ABI:
        return json.dumps(json.load(ABI.read()))


def extract_params(params):
    """
    Extracts the parameters from a string. Skips the first word.
    """
    params = params.split(' ')
    params.pop(0)
    params = [param.strip() for param in params]
    return params


def is_valid_token_address(token_address, chain_id):
    """
    Checks if the address is valid token.
    """
    erc_20_abi = erc20Abi()
    try:
        web3 = Web3(HTTPProvider(
            AppConfigs().get_provider(chain_id)
        ))
        contract = web3.eth.contract(address=token_address, abi=erc_20_abi)
        return bool(contract.functions.name().call())

    except Exception as e:
        print(f"Error checking if token is valid: {e}")
        return False
