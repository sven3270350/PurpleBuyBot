import configparser
import os

PATH_TO_APP_CFG = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'app.cfg')


class AppConfigs:
    def __init__(self):
        self._config = configparser.RawConfigParser()
        self._config.read([PATH_TO_APP_CFG])

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