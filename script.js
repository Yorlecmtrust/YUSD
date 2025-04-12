function login() {
  const savingsId = parseInt(document.getElementById('savingsId').value);
  const phone = document.getElementById('phone').value;

  if (!savingsId || !phone) {
    alert('Enter both Savings ID and Phone Number.');
    return;
  }

  fetch('http://localhost:8000/get-user-balance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ savings_id: savingsId, phone: phone })
  })
    .then(res => res.json())
    .then(data => {
      console.log("✅ Account found:", data);
      document.getElementById('loginPanel').style.display = 'none';
      document.getElementById('dashboard').style.display = 'block';
      document.getElementById('yetBalance').textContent = `$${parseFloat(data.balance).toFixed(2)}`;
      fetchTotalMinted();
    })
    .catch(err => {
      console.error("❌ Login failed:", err);
      alert("Login failed. Account not found.");
    });
}

function fetchTotalMinted() {
  fetch('http://localhost:8000/get-total-minted')
    .then(response => {
      if (!response.ok) throw new Error(`Status ${response.status}`);
      return response.json();
    })
    .then(data => {
      console.log("✅ Total minted fetched:", data);
      document.getElementById('totalMinted').textContent = `$${parseFloat(data.total).toFixed(2)}`;
    })
    .catch(err => {
      console.error('❌ Error fetching total minted:', err);
      document.getElementById('totalMinted').textContent = '$—';
    });
}

function mintYUSD() {
  const wallet = document.getElementById('walletAddress').value;
  const amount = document.getElementById('usdAmount').value;
  const status = document.getElementById('mintStatus');

  if (!wallet || !amount) {
    status.textContent = 'Please enter wallet and amount.';
    return;
  }

  status.textContent = 'Processing...';

  fetch('http://localhost:8000/send-stablecoin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      to_address: wallet,
      usd_amount: parseFloat(amount)
    })
  })
    .then(res => res.json())
    .then(res => {
      if (res.status === 'success') {
        status.textContent = `✅ Success! ${res.usd_amount.toFixed(2)} YUSD minted to ${wallet}`;
        fetchTotalMinted();
      } else {
        status.textContent = `❌ Error: ${res.detail || 'Unknown error'}`;
      }
    })
    .catch(err => {
      console.error('❌ Minting error:', err);
      status.textContent = 'Failed to mint YUSD.';
    });
}

function submitRampOff() {
  const account = document.getElementById('bankAccount').value;
  const routing = document.getElementById('routingNumber').value;
  const amount = parseFloat(document.getElementById('rampAmount').value);
  const destination = document.getElementById('destination').value;
  const rampStatus = document.getElementById('rampStatus');

  if (!account || !routing || !amount || !destination) {
    rampStatus.textContent = "❌ Please complete all fields.";
    return;
  }

  rampStatus.textContent = "Processing Ramp Off...";

  fetch("http://localhost:8000/ramp-off", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      bank_account: account,
      routing_number: routing,
      amount_usd: amount,
      destination: destination
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === "success") {
        rampStatus.textContent = `✅ Ramp Off of $${amount} submitted to ${destination}`;
      } else {
        rampStatus.textContent = `❌ Ramp Off Failed: ${data.detail}`;
      }
    })
    .catch(err => {
      console.error("❌ Ramp Off error:", err);
      rampStatus.textContent = "❌ Ramp Off request failed.";
    });
}

function logout() {
  document.getElementById("dashboard").style.display = "none";
  document.getElementById("loginPanel").style.display = "flex";
}
