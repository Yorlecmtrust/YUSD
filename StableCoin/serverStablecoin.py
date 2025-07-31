# SECTION 1: Imports, Setup
import os
import json
import logging
import requests
import time
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from loandisk2 import get_balance_by_id, withdraw_from_loandisk, get_borrower_profile

# ✅ Initial setup
load_dotenv(dotenv_path=Path("C:/Users/yorle/Downloads/MyProject/StableCoin/.env"))
print("🚀 FastAPI loaded loandisk2.py")
print("🧪 STRIPE_PUBLISHABLE_KEY is loaded:", os.getenv("STRIPE_PUBLISHABLE_KEY")[:30])

YET_SMTP_PASSWORD = os.getenv("YET_SMTP_PASSWORD")  # Email password
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_BASE_URL = os.getenv("STRIPE_BASE_URL", "https://api.stripe.com")

# 🚀 FastAPI server startup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ✅ Supports recipient_key (like "paymaster", "wholesale", etc.)
class PayoutRequest(BaseModel):
    savings_id: int
    recipient_key: str  # label for UUID inside recipient_map.json
    amount: float
    description: str
    name: str
    email: str
    account: str
    routing: str
    type: str

class LoginRequest(BaseModel):
    savings_id: int
    phone: str

class RecipientRegistration(BaseModel):
    savings_id: int
    name: str
    email: str

def generate_remittance_pdf(savings_id, amount, bank, account, routing, destination, priority, memo=None, wire_id=None):
    filename = f"remittance_{savings_id}_{account}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Header
    c.drawString(50, 750, "YORLECM EXPRESS TRUST - Remittance Confirmation")

    # Core wire details
    c.drawString(50, 720, f"Recipient: {savings_id}")
    c.drawString(50, 705, f"Amount Sent: ${amount:,.2f}")
    c.drawString(50, 690, f"Receiving Bank: Citibank")
    c.drawString(50, 675, f"Account Number: {account}")
    c.drawString(50, 660, f"Routing Number: {routing}")
    c.drawString(50, 645, f"Transfer Type: {destination}")
    c.drawString(50, 630, f"Priority: {priority}")

    # Optional memo and wire ID
    if memo:
        c.drawString(50, 610, f"Memo: {memo}")
    if wire_id:
        c.drawString(50, 595, f"Wire ID: {wire_id}")

    # Final status
    c.drawString(50, 575, "Status: ✅ Funds dispatched successfully")

    # Custom footer message
    c.setFont("Helvetica", 10)
    c.drawString(50, 545, "Thank you for using Yorlecm Express Trust.")
    c.drawString(50, 530, "Your funds have been dispatched. Please see attached for confirmation.")
    c.drawString(50, 515, "– YET Treasury Ledger")

    c.save()
    return filename

def send_remittance_email(savings_id, email, pdf_path):
    msg = EmailMessage()
    msg["Subject"] = "YET Remittance Confirmation"
    msg["From"] = "admin@ugetityet.com"
    msg["To"] = email
    msg.set_content(f"Attached is your remittance confirmation for savings ID {savings_id}.")

    with open(pdf_path, "rb") as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=pdf_path)

    with smtplib.SMTP_SSL("smtp.privateemail.com", 465) as server:
        server.login("admin@ugetityet.com", YET_SMTP_PASSWORD)
        server.send_message(msg)

def generate_and_send_remittance(req: PayoutRequest):
    try:
        pdf_path = generate_remittance_pdf(
            savings_id=req.name,
            amount=req.amount,
            bank=req.name,  # Bank name placeholder
            account=req.account,
            routing=req.routing,
            destination=req.type,
            priority="High",
            memo = req.description  # ✅ Uses the live memo from the wire
        )
        send_remittance_email(req.name, req.email, pdf_path)
    except Exception as e:
        logging.error(f"❌ Background Remittance Failed: {str(e)}")

import base64

@app.post("/stripe-send-payout")
def stripe_send_payout(req: PayoutRequest = Body(...)):
    try:
        print(f"💸 Stripe payout initiated for ${req.amount:.2f} to {req.name}")

        headers = {
            "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        account_payload = {
           "type": "custom",
           "country": "US",
           "email": req.email,
           "business_type": "company" if req.type.lower() == "company" else "individual",
           "capabilities[transfers][requested]": "true",
        }

        acct_response = requests.post(
        f"{STRIPE_BASE_URL}/v1/accounts",
            data=account_payload,
            headers=headers
        )
        acct_result = acct_response.json()
        print("👤 Connected Account:", acct_result)

        if "id" not in acct_result:
           raise HTTPException(status_code=400, detail=f"❌ Account creation failed: {acct_result}")
        stripe_account_id = acct_result["id"]


        patch_payload = {
           "tos_acceptance[date]": str(int(time.time())),
           "tos_acceptance[ip]": "8.8.8.8",
           "business_profile[url]": "https://ugetityet.com",
           "company[name]": req.name
        }

        patch_response = requests.post(
       f"{STRIPE_BASE_URL}/v1/accounts/{stripe_account_id}",
           data=patch_payload,
           headers=headers
        )
        patch_result = patch_response.json()
        if patch_response.status_code != 200:
           raise HTTPException(status_code=400, detail=f"❌ TOS patch failed: {patch_result}")

        bank_payload = {
           "external_account[object]": "bank_account",
           "external_account[country]": "US",
           "external_account[currency]": "usd",
           "external_account[routing_number]": req.routing,
           "external_account[account_number]": req.account,
           "external_account[account_holder_name]": req.name,
           "external_account[account_holder_type]": req.type.lower()
        }

        ext_response = requests.post(
        f"{STRIPE_BASE_URL}/v1/accounts/{stripe_account_id}/external_accounts",
            data=bank_payload,
            headers=headers
        )
        ext_result = ext_response.json()
        print("🏦 Bank Attached:", ext_result)
        if "id" not in ext_result:
            raise HTTPException(status_code=400, detail=f"❌ Bank attach failed: {ext_result}")

            # ✅ 3. Transfer funds from Ledger to Stripe Treasury (connected account)
        transfer_payload = {
            "amount": int(req.amount * 100),
            "currency": "usd",
            "destination": stripe_account_id,  # This is the connected Stripe account ID
            "description": req.description
        }

        transfer_response = requests.post(
            f"{STRIPE_BASE_URL}/v1/transfers",
            data=transfer_payload,
           headers=headers
        )
        transfer_result = transfer_response.json()
        print("💸 Transfer Response:", transfer_result)
        if "id" not in transfer_result:
            raise Exception(f"❌ Stripe transfer failed: {transfer_result}")

        # ✅ 4. Payout to bank from connected account
        payout_payload = {
            "amount": int(req.amount * 100),
            "currency": "usd",
            "description": req.description,
            "method": "standard"
        }

        payout_response = requests.post(
            f"{STRIPE_BASE_URL}/v1/payouts",
            data=payout_payload,
            headers={**headers, "Stripe-Account": stripe_account_id}
        )
        payout_result = payout_response.json()
        print("📤 Payout Response:", payout_result)
        if "id" not in payout_result:
            raise Exception(f"❌ Stripe payout failed: {payout_result}")

        # ✅ 5. Remittance confirmation
        generate_and_send_remittance(req)

        return {
            "status": "sent",
       #     "transfer_id": transfer_result["id"],
            "payout_id": payout_result["id"],
            "amount": req.amount
        }

    except Exception as e:
        logging.error(f"❌ Stripe payout error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-user-balance")
def get_user_balance(req: LoginRequest = Body(...)):
    try:
        record = get_balance_by_id(req.savings_id)
        if float(record["savings_balance"]) < 100:
            raise HTTPException(status_code=403, detail="Minimum balance required.")
        return {
            "savings_id": record["savings_id"],
            "balance": float(record["savings_balance"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    try:
        payload = await request.body()
        print("📩 Stripe Webhook Received:", payload.decode())
        return {"status": "received"}
    except Exception as e:
        print("❌ Webhook Error:", str(e))
        raise HTTPException(status_code=500, detail="Webhook processing failed.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("serverStablecoin:app", host="127.0.0.1", port=8000, reload=False)

print("💤 Server is idle and ready.")
