
from pysui.abstracts.client_keypair import SignatureScheme
from pysui.sui.sui_config import SuiConfig


config = SuiConfig.default_config()

mnemonics, ddress = config.create_new_keypair_and_address(SignatureScheme.ED25519)