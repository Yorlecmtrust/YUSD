import os
import requests
import time
from dotenv import load_dotenv
from loandisk2 import withdraw_from_loandisk
from serverStablecoin import generate_and_send_remittance, PayoutRequest

# ✅ Load environment
load_dotenv("C:/Users/yorle/Downloads/MyProject/StableCoin/.env")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_BASE_URL = os.getenv("STRIPE_BASE_URL", "https://api.stripe.com")

# ✅ Ledger + Recipient Data
savings_id = 1239111
amount = 612430.91
name = "WHOLESALE PROPERTY INVESTMENTS INC"
email = "whlspropii@gmail.com"
routing = "322271724"
account = "208521864"
description = "Commercial redevelopment 2025 acquisition funding"
account_type = "company"
recipient_key = "archive"

# ✅ Step 1: Withdraw from private ledger
print("💸 Withdrawing from private ledger...")
withdraw_from_loandisk(amount, savings_id)
print("✅ Ledger withdrawal complete")

# ✅ Step 2: Create connected Stripe account
headers = {
    "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
    "Content-Type": "application/x-www-form-urlencoded"
}
acct_payload = {
    "type": "custom",
    "country": "US",
    "email": email,
    "business_type": "company",
    "capabilities[transfers][requested]": "true"
}
acct_response = requests.post(f"{STRIPE_BASE_URL}/v1/accounts", data=acct_payload, headers=headers)
acct_result = acct_response.json()
print("👤 Connected Account Created:", acct_result)

if "id" not in acct_result:
    raise Exception(f"❌ Account creation failed: {acct_result}")
stripe_account_id = acct_result["id"]

# ✅ Step 2.5: Patch required TOS, URL, Company Name
patch_payload = {
    "tos_acceptance[date]": str(int(time.time())),
    "tos_acceptance[ip]": "8.8.8.8",  # Replace with real server IP if known
    "business_profile[url]": "https://ugetityet.com",
    "company[name]": name
}
patch_response = requests.post(
    f"{STRIPE_BASE_URL}/v1/accounts/{stripe_account_id}",
    data=patch_payload,
    headers=headers
)
patch_result = patch_response.json()
if patch_response.status_code != 200:
    raise Exception(f"❌ Patch failed: {patch_result}")
print("🧾 TOS & Profile Updated:", patch_result)

# ✅ Step 3: Attach external bank
ext_payload = {
    "external_account[object]": "bank_account",
    "external_account[country]": "US",
    "external_account[currency]": "usd",
    "external_account[routing_number]": routing,
    "external_account[account_number]": account,
    "external_account[account_holder_name]": name,
    "external_account[account_holder_type]": account_type
}
ext_response = requests.post(
    f"{STRIPE_BASE_URL}/v1/accounts/{stripe_account_id}/external_accounts",
    data=ext_payload,
    headers=headers
)
ext_result = ext_response.json()
print("🏦 Bank Attached:", ext_result)
if "id" not in ext_result:
    raise Exception(f"❌ Bank attach failed: {ext_result}")

# ✅ Step 4: Create Treasury financial account
fa_payload = {
    "supported_currencies[]": "usd",
    "features[balance]": "true",
    "features[inbound_transfers]": "ach",
    "features[outbound_transfers]": "us_domestic_wire",
    "features[financial_addresses]": "aba"
}
fa_response = requests.post(
    f"{STRIPE_BASE_URL}/v1/treasury/financial_accounts",
    data=fa_payload,
    headers={**headers, "Stripe-Account": stripe_account_id}
)
fa_result = fa_response.json()
print("🏛️ Treasury Account Created:", fa_result)

if "id" not in fa_result:
    raise Exception(f"❌ Treasury account creation failed: {fa_result}")

# ✅ Step 5: Send payout
payout_payload = {
    "amount": int(amount * 100),
    "currency": "usd",
    "description": description,
    "method": "standard"
}
payout_response = requests.post(
    f"{STRIPE_BASE_URL}/v1/accounts/{stripe_account_id}/payouts",
    data=payout_payload,
    headers={**headers, "Stripe-Account": stripe_account_id}
)
payout_result = payout_response.json()
print("📤 Payout Response:", payout_result)

if "id" not in payout_result:
    raise Exception(f"❌ Stripe payout failed.")

# ✅ Step 6: Send PDF Confirmation
print("📧 Sending remittance PDF...")
req = PayoutRequest(
    savings_id=savings_id,
    recipient_key=recipient_key,
    amount=amount,
    description=description,
    name=name,
    email=email,
    account=account,
    routing=routing,
    type="ACH"
)
generate_and_send_remittance(req)

print("✅ Stripe Transaction Complete — Exit Code 0")
