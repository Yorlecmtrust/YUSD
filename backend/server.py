import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from web3 import Web3
import requests

# Load environment variables
load_dotenv()

app = FastAPI()

# Connect to Ethereum Node (Infura, Alchemy, or self-hosted)
web3 = Web3(Web3.HTTPProvider(os.getenv("INFURA_API_URL")))

# Load Contract ABI
with open("backend/contract_abi.json", "r") as f:
    contract_abi = json.load(f)

# Deployed Contract Address
contract_address = os.getenv("CONTRACT_ADDRESS")

# Create Contract Instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)


@app.get("/get-usdt-price/{usd_amount}")
def get_usdt_price(usd_amount: int):
    """Fetch the USDT equivalent for the given USD amount using Chainlink price feed"""
    try:
        usdt_amount = contract.functions.getUsdtFromUsd(usd_amount).call()
        return {"usd_amount": usd_amount, "usdt_amount": usdt_amount}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-withdrawal")
def process_withdrawal(usd_amount: int):
    """Processes withdrawal from LoanDisk and sends USDT"""
    try:
        private_key = os.getenv("PRIVATE_KEY")
        account = web3.eth.account.from_key(private_key)

        # Build transaction
        nonce = web3.eth.get_transaction_count(account.address)
        transaction = contract.functions.processWithdrawal(usd_amount).build_transaction({
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price
        })

        # Sign transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return {"status": "pending", "transaction_hash": tx_hash.hex()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/loandisk-withdrawal")
def loandisk_withdrawal(account_id: str, transaction_id: str, usd_amount: float):
    """Withdraws USD from LoanDisk before processing blockchain transaction"""
    try:
        loandisk_response = requests.post(
            f"https://api-main.loandisk.com/{os.getenv('LOANDISK_PUBLIC_KEY')}/{os.getenv('LOANDISK_BRANCH_ID')}/saving_transaction",
            json={
                "account_id": account_id,
                "transaction_id": transaction_id,
                "amount": usd_amount,
                "currency": "USD",
                "transaction_type": 2
            },
            headers={"Authorization": f"Bearer {os.getenv('LOANDISK_AUTH_CODE')}"}
        )

        loandisk_response.raise_for_status()
        return {"status": "success", "message": "LoanDisk withdrawal processed"}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"LoanDisk API error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
