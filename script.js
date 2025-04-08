function login() {
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;

  if (email && phone) {
    fetch('http://localhost:8000/get-user-balance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, phone: phone })
    })
      .then(res => res.json())
      .then(data => {
        console.log("✅ Account found:", data);
        document.getElementById('loginPanel').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        document.getElementById('yetBalance').textContent = `$${parseFloat(data.balance).toFixed(2)}`;
        fetchTotalMinted(); // Keep this
      })
      .catch(err => {
        console.error("❌ Login failed:", err);
        alert("Login failed. Account not found.");
      });
  } else {
    alert('Please enter email and phone number.');
  }
}

function fetchYETBalance() {
  fetch('http://localhost:8000/get-loandisk-balance')
    .then(response => {
      if (!response.ok) throw new Error(`Status ${response.status}`);
      return response.json();
    })
    .then(data => {
      console.log("✅ LoanDisk balance fetched:", data);
      document.getElementById('yetBalance').textContent = `$${parseFloat(data.balance).toFixed(2)}`;
    })
    .catch(err => {
      console.error('❌ Error fetching LoanDisk balance:', err);
      document.getElementById('yetBalance').textContent = '$—';
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
