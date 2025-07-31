import os
import json
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from web3 import Web3
from pydantic import BaseModel

load_dotenv()

# ✅ ENV Variables
INFURA_URL = os.getenv("INFURA_API_URL")
PRIVATE_KEY = os.getenv("RECIPIENT_PRIVATE_KEY")
STABLECOIN_CONTRACT = os.getenv("STABLECOIN_CONTRACT_ADDRESS")  # USDC or USDT
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
ACCOUNT = web3.eth.account.from_key(PRIVATE_KEY).address

# ✅ Minimal ERC20 ABI
erc20_abi = json.loads("""
[
    { "constant": true, "inputs": [], "name": "decimals", "outputs": [{"name":"","type":"uint8"}], "type": "function" },
    { "constant": true, "inputs": [{"name":"owner","type":"address"}], "name": "balanceOf", "outputs": [{"name":"","type":"uint256"}], "type": "function" },
    { "constant": false, "inputs": [{"name":"to","type":"address"},{"name":"value","type":"uint256"}], "name": "transfer", "outputs": [{"name":"","type":"bool"}], "type": "function" }
]
""")

# ✅ Token Contract Instance
token_contract = web3.eth.contract(address=Web3.to_checksum_address(STABLECOIN_CONTRACT), abi=erc20_abi)

# ✅ FastAPI App
app = FastAPI()

class StablecoinTransferRequest(BaseModel):
    wallet_address: str
    usd_amount: float

@app.post("/send-stablecoin")
def send_stablecoin(request: StablecoinTransferRequest):
    try:
        decimals = token_contract.functions.decimals().call()
        amount = int(request.usd_amount * (10 ** decimals))
        nonce = web3.eth.get_transaction_count(ACCOUNT)
        gas_price = web3.eth.gas_price

        tx = token_contract.functions.transfer(Web3.to_checksum_address(request.wallet_address), amount).build_transaction({
            'from': ACCOUNT,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': gas_price,
            'chainId': 1
        })

        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        return {
            "status": "success",
            "tx_hash": tx_hash.hex(),
            "sent_to": request.to_address,
            "usd_amount": request.usd_amount
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")

@app.get("/stablecoin-balance/{address}")
def get_stablecoin_balance(address: str):
    try:
        balance = token_contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
        decimals = token_contract.functions.decimals().call()
        return {"balance": balance / (10 ** decimals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
