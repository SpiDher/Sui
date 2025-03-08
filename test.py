
from pysui.abstracts.client_keypair import SignatureScheme
from pysui.sui.sui_config import SuiConfig
from pysui.sui.sui_crypto import SuiKeyPair,create_new_address
from pysui.sui.sui_client import SuiClient
config = SuiConfig.user_config(rpc_url='https://sui-testnet-endpoint.blockvision.org')
wallet = create_new_address(word_counts=12,keytype=SignatureScheme.ED25519)
first,key,third = wallet
# client = SyncGqlClient()
address = '0xd5db541629460f17db406d6c1222190d3d0d16634d57fc0b6f5fcc15eb49228c'

# ed_mnemonics, ed_address = config.create_new_keypair_and_address(scheme=SignatureScheme.ED25519)
# # balances = client.
# wallet = config.create_new_keypair_and_address(scheme=SignatureScheme.ED25519)

# print(ed_mnemonics)
# print(ed_address)
client = SuiClient("https://fullnode.mainnet.sui.io") 