import streamlit as st
import requests
import uuid  # Generate unique transaction IDs
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI backend URL
BASE_URL = "http://127.0.0.1:8000"  # Change if deployed

# Fetch predefined LoanDisk values from .env
DEFAULT_ACCOUNT_ID = os.getenv("LOANDISK_ACCOUNT_ID", "51283")  # Default value if missing
AUTO_TRANSACTION_ID = str(uuid.uuid4())  # Generate a unique transaction ID automatically

st.title("YORLCM EXPRESS TRUST ")

# --- Section 1: Check USDT Conversion Rate ---
st.header("Get USDT Equivalent")
usd_amount = st.number_input("Enter USD amount:", min_value=1, step=1)

if st.button("Get USDT Equivalent"):
    response = requests.get(f"{BASE_URL}/get-usdt-price/{usd_amount}")

    if response.status_code == 200:
        data = response.json()
        st.success(f"{usd_amount} USD ≈ {data['usdt_amount']} USDT")
    else:
        st.error("Failed to fetch USDT price. Please try again.")

# --- Section 2: Withdraw from LoanDisk ---
st.header("Withdraw from LoanDisk")

# Allow user to override default values
account_id = st.text_input("LoanDisk Account ID", DEFAULT_ACCOUNT_ID)
transaction_id = st.text_input("Transaction ID (Auto-Generated)", AUTO_TRANSACTION_ID)

if st.button("Withdraw from LoanDisk"):
    withdrawal_data = {
        "account_id": account_id,  # User can override
        "transaction_id": transaction_id,  # Auto-generated but editable
        "usd_amount": usd_amount
    }

    loandisk_response = requests.post(f"{BASE_URL}/loandisk-withdrawal", json=withdrawal_data)

    if loandisk_response.status_code == 200:
        st.success(f"LoanDisk withdrawal successful! Transaction ID: {transaction_id}")
    else:
        st.error("LoanDisk withdrawal failed. Check API or balance.")

# --- Section 3: Process Ethereum Transfer ---
st.header("Send USDT to Ethereum")

wallet_address = st.text_input("Ethereum Wallet Address", placeholder="Enter recipient wallet address")

if st.button("Process Blockchain Transfer"):
    if not wallet_address:
        st.error("Please enter a valid Ethereum wallet address!")
    else:
        tx_payload = {
            "usd_amount": usd_amount,
            "wallet_address": wallet_address  # Include wallet address in request
        }

        tx_response = requests.post(f"{BASE_URL}/process-withdrawal", json=tx_payload)

        if tx_response.status_code == 200:
            tx_data = tx_response.json()
            tx_hash = tx_data["transaction_hash"]
            st.success(f"USDT Sent to {wallet_address}! Transaction Hash: {tx_hash}")
            st.markdown(f"[View on Etherscan](https://etherscan.io/tx/{tx_hash})")
        else:
            st.error("Failed to process USDT transfer. Check blockchain network.")
