import os
import json
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

INFURA_URL = os.getenv("INFURA_API_URL")
PRIVATE_KEY = os.getenv("RECIPIENT_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("YET_TOKEN_CONTRACT")

# 🧪 Debug prints
print(f"🧪 CONTRACT_ADDRESS loaded: {CONTRACT_ADDRESS}")
print(f"🧪 Is valid address: {Web3.is_address(CONTRACT_ADDRESS)}")

web3 = Web3(Web3.HTTPProvider(INFURA_URL))
ACCOUNT = web3.eth.account.from_key(PRIVATE_KEY).address

# ✅ Load the deployed token ABI
with open("yet_abi.json", "r") as f:
    token_abi = json.load(f)

contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=token_abi)

def get_eth_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        response = requests.get(url)
        return response.json()["ethereum"]["usd"]
    except Exception as e:
        print(f"❌ Error fetching ETH price: {e}")
        return None

def convert_usd_to_eth(usd_amount):
    eth_price = get_eth_price()
    if eth_price:
        return usd_amount / eth_price
    return None

def mint_yet_tokens(to_address, usd_amount):
    eth_amount = convert_usd_to_eth(usd_amount)
    if not eth_amount:
        return "❌ Failed to convert USD to ETH"

    amount_wei = int(web3.to_wei(eth_amount, "ether"))
    nonce = web3.eth.get_transaction_count(ACCOUNT)
    gas_price = web3.eth.gas_price

    tx = contract.functions.mint(to_address, amount_wei).build_transaction({
        'from': ACCOUNT,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': gas_price,
        'chainId': 1
    })

    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"✅ Minted {eth_amount:.6f} ETH worth of YET tokens to {to_address}")
    return tx_hash.hex()
