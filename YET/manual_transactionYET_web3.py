import os
import requests
from web3 import Web3
from dotenv import load_dotenv
from blockchainETH2_web3 import convert_usd_to_eth, send_eth

# ✅ Load environment
load_dotenv()

INFURA_URL = os.getenv("INFURA_API_URL")
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

RECIPIENT_WALLET = os.getenv("WALLET_ADDRESS")  # Trust Wallet address
RECIPIENT_PRIVATE_KEY = os.getenv("RECIPIENT_PRIVATE_KEY")  # MetaMask private key
SAVINGS_ID = os.getenv("SAVINGS_ID")

# ✅ Step 1: Set USD withdrawal amount
amount_usd = 25
print(f"✅ Amount to Withdraw: {amount_usd} USD")

# ✅ Step 2: Simulate LoanDisk Withdrawal (replace with real API call)
print("🔹 Withdrawing from LoanDisk...")
print("✅ LoanDisk Response:", {
    "response": {"transaction_id": "SIMULATED_TXN_ID"},
    "http": {"code": 200, "message": "OK"}
})

# ✅ Step 3: Convert USD to ETH
eth_amount = convert_usd_to_eth(amount_usd)
if eth_amount is None:
    print("❌ Failed to fetch ETH price.")
    exit()
print(f"✅ ETH Amount to Transfer: {eth_amount} ETH")

# ✅ Step 4: Check sender wallet ETH balance
sender_account = web3.eth.account.from_key(RECIPIENT_PRIVATE_KEY)
sender_address = sender_account.address
eth_balance_wei = web3.eth.get_balance(sender_address)
eth_balance_eth = web3.from_wei(eth_balance_wei, "ether")
print(f"✅ ETH Balance in Sender Wallet: {eth_balance_eth} ETH")

# ✅ Step 5: Estimate gas + ensure enough ETH
eth_amount_wei = int(web3.to_wei(eth_amount, "ether"))
gas_limit = 21000
gas_price = web3.eth.gas_price
required_eth = float(web3.from_wei(gas_price * gas_limit, "ether")) + float(eth_amount)

if eth_balance_eth < required_eth:
    print(f"❌ Not enough ETH! Required: {required_eth}, Available: {eth_balance_eth}")
    exit()

# ✅ Step 6: Execute ETH Transfer
tx_hash = send_eth(RECIPIENT_PRIVATE_KEY, RECIPIENT_WALLET, eth_amount_wei)
print(f"✅ ETH Transfer Transaction Hash: {tx_hash}")

# ✅ Step 7: Mint YET Tokens via API call
mint_api_url = "http://localhost:8000/mint-token/"
try:
    mint_payload = {
        "to_address": RECIPIENT_WALLET,
        "usd_amount": amount_usd
    }
    mint_response = requests.post(mint_api_url, json=mint_payload)
    mint_data = mint_response.json()

    if mint_response.status_code == 200:
        print(f"✅ YET Tokens Minted: TX Hash {mint_data['tx_hash']}")
    else:
        print(f"❌ Minting Failed: {mint_data.get('detail', 'Unknown error')}")
except Exception as e:
    print(f"❌ Mint API Error: {str(e)}")
