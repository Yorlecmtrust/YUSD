import streamlit as st
import requests

# FastAPI backend URL
BASE_URL = "http://127.0.0.1:8000"  # Change if deployed

st.title("USD to USDT Transfer")

# User input for amount
usd_amount = st.number_input("Enter USD amount:", min_value=1, step=1)

# Button to fetch USDT conversion
if st.button("Get USDT Equivalent"):
    response = requests.get(f"{BASE_URL}/get-usdt-price/{usd_amount}")

    if response.status_code == 200:
        data = response.json()
        st.success(f" {usd_amount} USD ≈ {data['usdt_amount']} USDT")
    else:
        st.error(" Failed to fetch USDT price. Please try again.")

# User input for transaction
st.subheader("Process Withdrawal")
wallet_address = st.text_input("Ethereum Wallet Address")

if st.button("Withdraw & Transfer"):
    withdrawal_data = {
        "account_id": account_id,
        "transaction_id": transaction_id,
        "usd_amount": usd_amount
    }
    # Step 1: Withdraw from LoanDisk
    loandisk_response = requests.post(f"{BASE_URL}/loandisk-withdrawal", json=withdrawal_data)

    if loandisk_response.status_code == 200:
        st.success("LoanDisk withdrawal successful!")

        # Step 2: Process USDT transaction
        tx_response = requests.post(f"{BASE_URL}/process-withdrawal", json={"usd_amount": usd_amount})

        if tx_response.status_code == 200:
            tx_data = tx_response.json()
            st.success(f" USDT Sent! Transaction Hash: {tx_data['transaction_hash']}")
        else:
            st.error("Failed to process USDT transfer.")
    else:
        st.error("LoanDisk withdrawal failed.")