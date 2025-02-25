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

dotenv_path = Path(__file__).resolve().parent / ".env"
if not load_dotenv(dotenv_path):
    print("WARNING: .env file not found or not loaded properly!")


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
    logging.error("contract_abi.json file not found.")
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
    wallet_address: str



@app.post("/process_withdrawal")
def process_withdrawal(request: WithdrawalRequest = Body(...)):
    """
    Combines LoanDisk withdrawal and blockchain withdrawal into one endpoint.
    1. Withdraws USD from LoanDisk using the provided account and transaction details.
    2. Processes a blockchain transaction to convert and transfer USDT.
    """
    try:
        # -- Part 1: LoanDisk Withdrawal --
        loandisk_url = f"https://api-main.loandisk.com/{os.getenv('LOANDISK_PUBLIC_KEY')}/{os.getenv('LOANDISK_BRANCH_ID')}/saving_transaction"
        loan_payload = {
            "account_id": request.account_id,
            "transaction_id": request.transaction_id,
            "amount": request.usd_amount,
            "currency": "USD",
            "transaction_type": 2  # Withdrawal type
        }
        headers = {"Authorization": f"Bearer {os.getenv('LOANDISK_AUTH_CODE')}"}
        loandisk_response = requests.post(loandisk_url, json=loan_payload, headers=headers)
        loandisk_response.raise_for_status()
        loan_disk_result = {"status": "success", "message": "LoanDisk withdrawal processed"}
        logging.info("LoanDisk withdrawal processed successfully.")

        # -- Part 2: Blockchain Transaction --
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            logging.error("PRIVATE_KEY is missing in .env file.")
            raise HTTPException(status_code=500, detail="Missing PRIVATE_KEY in .env")
        account = web3.eth.account.from_key(private_key)

        wallet_address = request.wallet_address.strip()
        if not wallet_address or not web3.is_address(wallet_address):
            logging.error("Invalid or missing wallet address.")
            raise HTTPException(status_code=400, detail="Invalid or missing Ethereum wallet address")

        nonce = web3.eth.get_transaction_count(account.address)
        transaction = contract.functions.processWithdrawal(request.usd_amount, wallet_address).build_transaction({
            'nonce': nonce,
            'gas': 210000,
            'gasPrice': web3.eth.gas_price
        })
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        blockchain_result = {"status": "pending", "transaction_hash": tx_hash.hex()}
        logging.info("Blockchain withdrawal transaction sent successfully.")

        # -- Combined Response --
        return {
            "loan_disk": loan_disk_result,
            "blockchain": blockchain_result,
            "usd_amount": request.usd_amount,
            "wallet_address": wallet_address
        }

    except Exception as e:
        logging.error(f"Error in combined withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logging.info(" Starting FastAPI backend on http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
