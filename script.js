function login() {
  const savingsId = document.getElementById('savingsId').value;
  const phone = document.getElementById('phone').value;

  if (savingsId && phone) {
    fetch('http://localhost:8000/get-user-balance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ savings_id: parseInt(savingsId), phone: phone })
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
  } else {
    alert('Please enter both Savings ID and Phone Number.');
  }
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
    status.textContent = 'Please enter wallet address and amount.';
    return;
  }

  status.textContent = 'Processing...';

  fetch('http://localhost:8000/send-stablecoin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ to_address: wallet, usd_amount: parseFloat(amount) })
  })
  .then(res => res.json())
  .then(res => {
    if (res.status === 'success') {
      status.textContent = `✅ ${res.usd_amount.toFixed(2)} YUSD minted to ${wallet}`;
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

function rampOff() {
  const amount = document.getElementById('rampAmount').value;
  const wallet = document.getElementById('destinationWallet').value;
  const type = document.getElementById('rampType').value;
  const status = document.getElementById('rampStatus');

  if (!amount || !wallet) {
    status.textContent = 'Please enter amount and destination wallet.';
    return;
  }

  status.textContent = 'Processing ramp-off...';

  fetch('http://localhost:8000/ramp-off', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount: parseFloat(amount), destination: wallet, type: type })
  })
  .then(res => res.json())
  .then(res => {
    if (res.status === 'success') {
      status.textContent = `✅ Ramp-Off Complete → ${wallet}`;
    } else {
      status.textContent = `❌ Error: ${res.detail || 'Unknown error'}`;
    }
  })
  .catch(err => {
    console.error('❌ Ramp-Off error:', err);
    status.textContent = 'Ramp-Off failed.';
  });
}

function topUpCard() {
  const amount = document.getElementById('cardAmount').value;
  const status = document.getElementById('cardStatus');

  if (!amount) {
    status.textContent = 'Please enter amount.';
    return;
  }

  status.textContent = 'Topping up card...';

  fetch('http://localhost:8000/top-up-card', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount: parseFloat(amount) })
  })
  .then(res => res.json())
  .then(res => {
    if (res.status === 'success') {
      status.textContent = `✅ Card Topped Up: ${res.amount} YUSD converted to USDC`;
    } else {
      status.textContent = `❌ Error: ${res.detail || 'Unknown error'}`;
    }
  })
  .catch(err => {
    console.error('❌ Card top-up error:', err);
    status.textContent = 'Card Top-Up failed.';
  });
}

function logout() {
  document.getElementById('dashboard').style.display = 'none';
  document.getElementById('loginPanel').style.display = 'flex';
}
