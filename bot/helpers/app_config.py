import configparser
import os
import json
from pathlib import Path

PATH_TO_APP_CFG = os.path.join(os.path.dirname(
    Path(__file__).parent.parent), 'app.cfg')

PATH_TO_ERC_20_ABI = os.path.join(os.path.dirname(
    Path(__file__)), "erc20abi.json"
)

PATH_TO_FACTORY_ABI = os.path.join(os.path.dirname(
    Path(__file__)), "factoryAbi.json"
)

PATH_TO_PAIR_ABI = os.path.join(os.path.dirname(
    Path(__file__)), "pairAbi.json"
)


class AppConfigs:
    def __init__(self):
        self._config = configparser.RawConfigParser()
        self._config.read([PATH_TO_APP_CFG])

    def get_secret_key(self):
        return self._config.get("SECRETS", "secret_key")

    def get_explorer(self, chain_id):
        chain_id = int(chain_id)
        explorers = {
            1: "etherscan",
            56: "bscscan",
            25: "cronoscan",
            3: "ropsten",
            97: "bscTestnet",
            338: "croTest",
        }
        key = explorers[chain_id]

        return self._config.get("EXPLORERS", key)

    def get_chain(self, chain_id):
        chain_id = int(chain_id)
        chain_name = {
            1: "ETH",
            56: "BSC",
            25: "CRO",
            3: "Ropsten",
            97: "BSCTestnet",
            338: "CROTestnet",
        }
        return chain_name[chain_id]

    def get_erc20_abi(self):
        with open(PATH_TO_ERC_20_ABI) as AbiData:
            return json.dumps(json.loads(AbiData.read()))

    def get_factory_abi(self):
        with open(PATH_TO_FACTORY_ABI) as AbiData:
            return json.dumps(json.loads(AbiData.read()))

    def get_pair_abi(self):
        with open(PATH_TO_PAIR_ABI) as AbiData:
            return json.dumps(json.loads(AbiData.read()))

    def get_provider(self, chain_id):
        chain_id = int(chain_id)
        explorers = {
            1: "ethProvider",
            56: "bscProvider",
            25: "croProvider",
            3: "testnetEthProvider",
            97: "testnetBscProvider",
            338: "testnetCroProvider",
        }
        key = explorers[chain_id]

        return self._config.get("WEB3_PROVIDER", key)

    def get_cg_id(self, chain_id):
        chain_id = int(chain_id)
        explorers = {
            1: "ethid",
            56: "bscid",
            25: "croid",
            3: "ethid",
            97: "bscid",
            338: "croid",
        }
        key = explorers[chain_id]

        return self._config.get("COINGECKO_IDs", key)
