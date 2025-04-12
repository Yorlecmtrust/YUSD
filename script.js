// ================== LOGIN ==================
document.getElementById("loginForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const savingsId = document.getElementById("savingsId").value;
  const phone = document.getElementById("phone").value;

  const response = await fetch("http://localhost:8000/get-user-balance", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ savings_id: parseInt(savingsId), phone: phone })
  });

  if (response.ok) {
    localStorage.setItem("savings_id", savingsId);
    window.location.href = "dashboard.html";
  } else {
    alert("Login failed. Please check your credentials.");
  }
});
// ================== DASHBOARD ==================
async function loadDashboard() {
  const savingsId = localStorage.getItem("savings_id");

  const [balanceRes, priceRes, mintedRes] = await Promise.all([
    fetch("http://localhost:8000/get-loandisk-balance"),
    fetch("http://localhost:8000/get-price"),
    fetch("http://localhost:8000/get-total-minted")
  ]);

  const balance = await balanceRes.json();
  const price = await priceRes.json();
  const minted = await mintedRes.json();

  document.getElementById("balance").innerText = `$${balance.balance.toLocaleString()}`;
  document.getElementById("price").innerText = `$${price.price_usd.toFixed(2)}`;
  document.getElementById("minted").innerText = `$${minted.total.toFixed(2)}`;
}
// ================== MINT YUSD ==================
document.getElementById("mintForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const wallet = document.getElementById("wallet").value;
  const amount = parseFloat(document.getElementById("usd").value);

  const response = await fetch("http://localhost:8000/send-stablecoin", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ to_address: wallet, usd_amount: amount })
  });

  const data = await response.json();
  document.getElementById("mintStatus").innerText = response.ok
    ? `✅ Minted $${data.usd_amount} to ${data.to_address}`
    : `❌ Error: ${data.detail}`;
});
// ================== RAMP OFF ==================
document.getElementById("rampForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const bankName = document.getElementById("bankName").value;
  const routing = document.getElementById("routing").value;
  const account = document.getElementById("account").value;
  const amount = parseFloat(document.getElementById("rampAmount").value);
  const destination = document.getElementById("destination").value;

  const response = await fetch("http://localhost:8000/ramp-off", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      bank_name: bankName,
      routing_number: routing,
      account_number: account,
      amount_usd: amount,
      destination: destination
    })
  });

  const result = await response.json();
  document.getElementById("rampStatus").innerText = response.ok
    ? `✅ Ramp Off Successful: $${amount} sent to ${destination}`
    : `❌ Ramp Off Error: ${result.detail}`;
});
// ================== CLOCK ==================
function updateClock() {
  const now = new Date();
  const options = { hour: '2-digit', minute: '2-digit', second: '2-digit', weekday: 'short', hour12: true };
  document.getElementById("clockDisplay").textContent = now.toLocaleTimeString("en-US", options);
}
setInterval(updateClock, 1000);
updateClock();
