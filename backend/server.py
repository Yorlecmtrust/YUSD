import json
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from web3 import Web3
import requests
from pathlib import Path
from pydantic import BaseModel
from fastapi import Body

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables explicitly
dotenv_path = Path(__file__).resolve().parent / ".env"
if not load_dotenv(dotenv_path):
    logging.warning(".env file not loaded. Make sure it exists in the backend directory.")

# Initialize FastAPI app
app = FastAPI()

# Connect to Ethereum Node (Infura, Alchemy, or self-hosted)
INFURA_API_URL = os.getenv("INFURA_API_URL")
if not INFURA_API_URL:
    logging.error(" INFURA_API_URL is missing in .env file.")
    raise Exception("INFURA_API_URL is required but not set.")

web3 = Web3(Web3.HTTPProvider(INFURA_API_URL))
if not web3.is_connected():
    logging.error(" Web3 is not connected. Check INFURA_API_URL or network status.")
    raise Exception("Web3 connection failed. Check Ethereum provider.")

# Load Contract ABI
abi_path = Path(__file__).resolve().parent / "contract_abi.json"
try:
    with open(abi_path, "r") as f:
        contract_abi = json.load(f)
except FileNotFoundError:
    logging.error(" contract_abi.json file not found.")
    raise Exception("contract_abi.json file is missing.")
except json.JSONDecodeError:
    logging.error("contract_abi.json contains invalid JSON.")
    raise Exception("Invalid JSON in contract_abi.json.")

# Load Deployed Contract Address
contract_address = os.getenv("CONTRACT_ADDRESS")
if not contract_address:
    logging.error(" CONTRACT_ADDRESS is missing in .env file.")
    raise Exception("CONTRACT_ADDRESS is required but not set.")

# Create Contract Instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

@app.get("/get-usdt-price/{usd_amount}")
def get_usdt_price(usd_amount: int):
    """Fetch the USDT equivalent for the given USD amount using Chainlink price feed."""
    try:
        usdt_amount = contract.functions.getUsdtFromUsd(usd_amount).call()
        return {"usd_amount": usd_amount, "usdt_amount": usdt_amount}
    except Exception as e:
        logging.error(f"Error fetching USDT price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class WithdrawalRequest(BaseModel):
    usd_amount: int

@app.post("/process-withdrawal")
def process_withdrawal(request: WithdrawalRequest = Body(...)):
    """Processes withdrawal from LoanDisk and sends USDT."""
    try:
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            logging.error(" PRIVATE_KEY is missing in .env file.")
            raise HTTPException(status_code=500, detail="Missing PRIVATE_KEY in .env")

        account = web3.eth.account.from_key(private_key)

        # Extract usd_amount from JSON request
        usd_amount = request.usd_amount

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
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return {"status": "pending", "transaction_hash": tx_hash.hex()}

    except Exception as e:
        logging.error(f"Error processing withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
from fastapi import Body

class LoanDiskWithdrawalRequest(BaseModel):
    account_id: str
    transaction_id: str
    usd_amount: float

@app.post("/loandisk-withdrawal")
def loandisk_withdrawal(request: LoanDiskWithdrawalRequest = Body(...)):
    """Withdraws USD from LoanDisk before processing blockchain transaction"""
    try:
        loandisk_response = requests.post(
            f"https://api-main.loandisk.com/{os.getenv('LOANDISK_PUBLIC_KEY')}/{os.getenv('LOANDISK_BRANCH_ID')}/saving_transaction",
            json={
                "account_id": request.account_id,
                "transaction_id": request.transaction_id,
                "amount": request.usd_amount,
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
    logging.info(" Starting FastAPI backend on http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
