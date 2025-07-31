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

savings_id = 1239109  # Default savings ID

LOANDISK_BASE_URL: str = f"https://api-main.loandisk.com/{LOANDISK_PUBLIC_KEY}/{LOANDISK_BRANCH_ID}"  # LoanDisk API URL


def get_balance():
    """Retrieve account balance from LoanDisk2 for a specific savings ID."""
    try:
        print(f"Fetching balance for savings_id: {savings_id}")

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
                    return record  # Return matched savings record

            raise Exception(f"Record with ID {savings_id} not found.")

        raise Exception("Failed to fetch balance from LoanDisk.")

    except requests.exceptions.RequestException as e:
        raise Exception(f"LoanDisk API request error: {e}")


def withdraw_from_loandisk2(amount, savings_id):
    """Withdraw USD from LoanDisk account and prepare for conversion."""
    logging.info("Initiating LoanDisk2 withdrawal...")

    if not LOANDISK_API_KEY or not LOANDISK_PUBLIC_KEY or not LOANDISK_BRANCH_ID:
        raise Exception(" LoanDisk API credentials missing in environment variables.")

    current_date = datetime.now().strftime("%m/%d/%Y")
    current_time = datetime.now().strftime("%I:%M %p")
    logging.info(f"Date: {current_date},  Time: {current_time}")

    data = {
        "savings_id": savings_id,
        "transaction_date": current_date,
        "transaction_time": current_time,
        "transaction_type_id": 2,  # Withdrawal
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

    response_data = response.json()
    logging.info("Response:", response_data)

    if response.status_code == 200:
        logging.info("✅ LoanDisk2 withdrawal successful!")
        return response.json()

    raise Exception("Failed to withdraw from LoanDisk2.")
