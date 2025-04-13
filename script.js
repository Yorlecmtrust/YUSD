// ✅ script.js - Final

document.addEventListener("DOMContentLoaded", function () {
  // Login section
  const loginBtn = document.querySelector("button");
  if (loginBtn) {
    loginBtn.addEventListener("click", function () {
      const email = document.getElementById("username").value;
      const phone = document.getElementById("password").value;

      fetch("http://127.0.0.1:8000/get-user-balance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, phone })
      })
      .then(response => response.json())
      .then(data => {
        if (data.savings_id && data.balance !== undefined) {
          sessionStorage.setItem("savings_id", data.savings_id);
          sessionStorage.setItem("balance", data.balance);
          window.location.href = "dashboard.html";
        } else {
          alert("Login failed. Please check your credentials.");
        }
      })
      .catch(error => {
        console.error("Login Error:", error);
        alert("Server error. Please try again later.");
      });
    });
  }

  // Mint YUSD section
  const mintBtn = document.getElementById("mintBtn");
  if (mintBtn) {
    mintBtn.addEventListener("click", function () {
      const wallet = document.getElementById("walletAddress").value;
      const amount = document.getElementById("usdAmount").value;

      fetch("http://127.0.0.1:8000/send-stablecoin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ to_address: wallet, usd_amount: parseFloat(amount) })
      })
      .then(response => response.json())
      .then(data => {
        document.getElementById("mintStatus").textContent = `✅ Sent ${data.usd_amount} YUSD`;
        document.getElementById("mintTx").textContent = `TX Hash: ${data.tx_hash}`;
        fetchTotalMinted();
      })
      .catch(error => {
        console.error("Mint Error:", error);
        alert("Minting failed.");
      });
    });
  }

  // Ramp Off section
  const rampBtn = document.getElementById("rampBtn");
  if (rampBtn) {
    rampBtn.addEventListener("click", function () {
      const bankName = document.getElementById("bankName").value;
      const routing = document.getElementById("routingNumber").value;
      const account = document.getElementById("accountNumber").value;
      const amount = document.getElementById("rampAmount").value;
      const destination = document.getElementById("destinationOption").value;

      fetch("http://127.0.0.1:8000/ramp-off", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bank_name: bankName,
          routing_number: routing,
          account_number: account,
          usd_amount: parseFloat(amount),
          destination_option: destination,
          savings_id: sessionStorage.getItem("savings_id")
        })
      })
      .then(response => response.json())
      .then(data => {
        document.getElementById("rampStatus").textContent = `✅ Ramp off complete: ${data.status}`;
      })
      .catch(error => {
        console.error("Ramp Off Error:", error);
        alert("Ramp off failed.");
      });
    });
  }

  // Fetch totals
  function fetchTotalMinted() {
    fetch("http://127.0.0.1:8000/get-total-minted")
      .then(response => response.json())
      .then(data => {
        document.getElementById("totalMinted").textContent = `$${data.total.toFixed(2)}`;
      });
  }

  function fetchLoanDiskBalance() {
    fetch("http://127.0.0.1:8000/get-loandisk-balance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ savings_id: sessionStorage.getItem("savings_id") })
    })
    .then(response => response.json())
    .then(data => {
      document.getElementById("loanDiskBalance").textContent = `$${data.balance.toFixed(2)}`;
    });
  }

  fetchLoanDiskBalance();
  fetchTotalMinted();
});
