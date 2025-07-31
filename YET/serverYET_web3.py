import os
import json
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

# ✅ Setup Web3
INFURA_URL = os.getenv("INFURA_API_URL")
PRIVATE_KEY = os.getenv("RECIPIENT_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("YET_TOKEN_CONTRACT")
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
ACCOUNT = web3.eth.account.from_key(PRIVATE_KEY).address

# ✅ Load Token ABI
try:
    with open("yet_abi.json", "r") as f:
        token_abi = json.load(f)
except Exception as e:
    raise Exception(f"❌ ABI Load Failed: {str(e)}")

token_contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=token_abi)

# ✅ FastAPI App
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ETH server is running 🚀"}

@app.post("/mint-token/")
def mint_token(to_address: str, usd_amount: float):
    try:
        # Convert USD to ETH (via CoinGecko)
        eth_price = get_eth_price()
        if eth_price is None:
            raise HTTPException(status_code=500, detail="Failed to fetch ETH price.")
        eth_equivalent = usd_amount / eth_price
        amount_wei = int(web3.to_wei(eth_equivalent, "ether"))

        # Build Transaction
        nonce = web3.eth.get_transaction_count(ACCOUNT)
        gas_price = web3.eth.gas_price
        tx = token_contract.functions.mint(to_address, amount_wei).build_transaction({
            "from": ACCOUNT,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": gas_price,
            "chainId": 1,
        })

        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return {
            "status": "success",
            "tx_hash": tx_hash.hex(),
            "minted_eth_value": eth_equivalent
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_eth_price():
    import requests
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["ethereum"]["usd"]
    except Exception as e:
        print(f"❌ ETH price fetch failed: {e}")
        return None
