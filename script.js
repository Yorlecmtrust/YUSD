function login() {
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;

  if (email && phone) {
    document.getElementById('loginPanel').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    fetchYETBalance();
    fetchTotalMinted();
  } else {
    alert('Enter both email and phone number.');
  }
}

function fetchYETBalance() {
  fetch('/get-balance')
    .then(response => response.json())
    .then(data => {
      document.getElementById('yetBalance').textContent = `$${parseFloat(data.balance).toFixed(2)}`;
    })
    .catch(err => {
      console.error('Error fetching balance:', err);
      document.getElementById('yetBalance').textContent = '$—';
    });
}

function fetchTotalMinted() {
  fetch('/get-total-minted')
    .then(response => response.json())
    .then(data => {
      document.getElementById('totalMinted').textContent = `$${parseFloat(data.total).toFixed(2)}`;
    })
    .catch(err => {
      console.error('Error fetching total minted:', err);
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

  fetch('/transfer/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      to_address: wallet,
      amount_usd: parseFloat(amount)
    })
  })
    .then(res => res.json())
    .then(res => {
      if (res.status === 'success') {
        status.textContent = `Success! ${res.amount_usdt.toFixed(2)} YUSD sent to ${wallet}`;
        fetchTotalMinted();
      } else {
        status.textContent = `Error: ${res.detail || 'Unknown error'}`;
      }
    })
    .catch(err => {
      console.error('Minting error:', err);
      status.textContent = 'Failed to mint YUSD.';
    });
}
