import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

LOANDISK_API_KEY = os.getenv("LOANDISK_API_KEY")
LOANDISK_PUBLIC_KEY = os.getenv("LOANDISK_PUBLIC_KEY")
LOANDISK_BRANCH_ID = os.getenv("LOANDISK_BRANCH_ID")

LOANDISK_BASE_URL: str = f"https://api-main.loandisk.com/{LOANDISK_PUBLIC_KEY}/{LOANDISK_BRANCH_ID}"

# ✅ Fake test borrower (placeholder if real API fails)
def get_borrower_profile(borrower_id):
    try:
        response = requests.get(
            f"{LOANDISK_BASE_URL}/borrower/{borrower_id}",
            headers={
                "Authorization": f"Basic {LOANDISK_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Failed to fetch borrower profile: {e}")
        return {"error": "Borrower profile not found."}

# ✅ Used in your main FastAPI app
def get_balance_by_id(savings_id):
    try:
        logging.info(f"Fetching balance for savings_id: {savings_id}")

        response = requests.get(
            f"{LOANDISK_BASE_URL}/saving/from/1/count/10",
            headers={
                "Authorization": f"Basic {LOANDISK_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if response.status_code == 200:
            response_data = response.json()
            results = response_data.get("response", {}).get("Results", [])

            for record in results:
                if record.get("savings_id") == savings_id:
                    return record

            raise Exception(f"Record with ID {savings_id} not found.")

        raise Exception("Failed to fetch balance from LoanDisk.")

    except requests.exceptions.RequestException as e:
        raise Exception(f"LoanDisk API request error: {e}")

# ✅ Same logic, just renamed so FastAPI import matches
def withdraw_from_loandisk(amount, savings_id):
    logging.info("Initiating LoanDisk withdrawal...")

    if not LOANDISK_API_KEY or not LOANDISK_PUBLIC_KEY or not LOANDISK_BRANCH_ID:
        raise Exception("LoanDisk API credentials missing in environment variables.")

    current_date = datetime.now().strftime("%m/%d/%Y")
    current_time = datetime.now().strftime("%I:%M %p")

    data = {
        "savings_id": savings_id,
        "transaction_date": current_date,
        "transaction_time": current_time,
        "transaction_type_id": 2,
        "transaction_amount": amount,
        "transaction_description": "client withdraws",
    }

    response = requests.post(
        f"{LOANDISK_BASE_URL}/saving_transaction",
        headers={
            "Authorization": f"Basic {LOANDISK_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data
    )

    if response.status_code == 200:
        logging.info("✅ LoanDisk withdrawal successful!")
        return response.json()
    else:
        logging.error(f"Failed withdrawal: {response.text}")
        raise Exception("Failed to withdraw from LoanDisk.")
