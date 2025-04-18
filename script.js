document.addEventListener("DOMContentLoaded", function () {
  const loginBtn = document.getElementById("loginBtn");
  const rampBtn = document.getElementById("rampBtn");
  const mintBtn = document.getElementById("mintBtn");
  const bitpayBtn = document.getElementById("bitpayBtn");
  const bridgeBtn = document.getElementById("bridgeBtn");

  function isWithinYETHours() {
    const now = new Date();
    const day = now.getUTCDay();
    const hour = now.getUTCHours();
    const pstHour = (hour + 24 - 7) % 24;
    return [1, 3, 5].includes(day) && pstHour >= 9 && pstHour < 11;
  }

  function blockActionsIfClosed() {
    if (!isWithinYETHours()) {
      const elements = [loginBtn, rampBtn, mintBtn, bridgeBtn];
      elements.forEach(el => { if (el) el.disabled = true; });
      const status = document.getElementById("rampStatus");
      if (status) status.textContent = "⏳ YET is closed. Try again Mon/Wed/Fri 09–11 AM PST.";
    }
  }

  // ✅ Login
  if (loginBtn) {
    loginBtn.addEventListener("click", function () {
      const savings_id = parseInt(document.getElementById("username").value);
      const phone = document.getElementById("password").value;
      const email = document.getElementById("email").value;

      if (!savings_id || !phone || !email) {
        alert("Please enter Savings ID, Phone Number, and Email.");
        return;
      }

      fetch("http://127.0.0.1:8000/get-user-balance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ savings_id, phone })
      })
        .then(res => res.json())
        .then(data => {
          if (data.savings_id && data.balance !== undefined) {
            sessionStorage.setItem("savings_id", data.savings_id);
            sessionStorage.setItem("balance", data.balance);
            sessionStorage.setItem("email", email);
            document.getElementById("loginView").style.display = "none";
            document.getElementById("dashboardView").style.display = "block";
            document.getElementById("loanDiskBalance").textContent = `$${parseFloat(data.balance).toFixed(2)}`;
            fetchTotalMinted();
            renderRampLog();
          } else {
            alert("Login failed.");
          }
        })
        .catch(() => alert("Server error. Try again."));
    });
  }

  // ✅ Mint
  if (mintBtn) {
    mintBtn.addEventListener("click", function () {
      const wallet = document.getElementById("walletAddress").value;
      const amount = parseFloat(document.getElementById("usdAmount").value);
      const email = sessionStorage.getItem("email");

      if (!wallet || !amount || !email) {
        alert("Enter wallet, amount, and make sure you're logged in with email.");
        return;
      }

      fetch("http://127.0.0.1:8000/send-stablecoin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ to_address: wallet, usd_amount: amount, email: email })
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById("mintStatus").textContent = `✅ Sent ${data.usd_amount} YUSD`;
          document.getElementById("mintTx").textContent = `TX Hash: ${data.tx_hash}`;
          fetchTotalMinted();
        })
        .catch(() => alert("Minting failed."));
    });
  }

  // ✅ Ramp Off
  if (rampBtn) {
    rampBtn.addEventListener("click", function () {
      const bank = document.getElementById("bankName").value;
      const routing = document.getElementById("routingNumber").value;
      const account = document.getElementById("accountNumber").value;
      const amount = parseFloat(document.getElementById("rampAmount").value);
      const option = document.getElementById("destinationOption").value;
      const savings_id = parseInt(sessionStorage.getItem("savings_id"));
      const priority = option === "Personal Bank" ? "wire" : "standard";

      const payload = {
        savings_id: savings_id,
        account_number: account || "ZELLE-ONLY",
        routing_number: routing || "N/A",
        bank_name: bank || "Zelle",
        amount: amount,
        destination: option,
        priority: priority
      };

      fetch("http://127.0.0.1:8000/ramp-off", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById("rampStatus").textContent = `✅ Ramp off complete: ${data.status}`;
          renderRampLog();
        })
        .catch(() => alert("Ramp off failed."));
    });
  }

  // ✅ Bridge to NOWPayments
  if (bridgeBtn) {
    bridgeBtn.addEventListener("click", function () {
      const amount = parseFloat(document.getElementById("bridgeAmount").value);

      if (!amount) {
        alert("Please enter the amount to bridge.");
        return;
      }

      fetch("http://127.0.0.1:8000/bridge-to-nowpayments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount: amount })
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById("bridgeStatus").textContent =
            `✅ Bridged to NOWPayments. TX: ${data.tx_hash}`;
        })
        .catch(() => {
          document.getElementById("bridgeStatus").textContent =
            `❌ Failed to bridge to NOWPayments.`;
        });
    });
  }

  // ✅ BitPay Invoice
  if (bitpayBtn) {
    bitpayBtn.addEventListener("click", () => {
      const invoice_url = document.getElementById("bitpayUrl").value;
      const amount = parseFloat(document.getElementById("bitpayAmount").value);
      const email = sessionStorage.getItem("email");

      if (!invoice_url || !amount || !email) {
        alert("Please enter invoice URL, amount, and be logged in with email.");
        return;
      }

      fetch("http://127.0.0.1:8000/pay-bitpay-invoice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ invoice_url, amount, email })
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById("bitpayStatus").textContent =
            `✅ Invoice sent: ${data.payout_id}`;
        })
        .catch(() => {
          document.getElementById("bitpayStatus").textContent =
            `❌ Failed to send invoice`;
        });
    });
  }

  // ✅ Fetch Total Minted
  function fetchTotalMinted() {
    fetch("http://127.0.0.1:8000/get-total-minted")
      .then(res => res.json())
      .then(data => {
        document.getElementById("totalMinted").textContent = `$${data.total.toFixed(2)}`;
      });
  }

  // ✅ Ramp Log Viewer (safe check fix)
  function renderRampLog() {
    fetch("http://127.0.0.1:8000/get-ramp-log")
      .then(res => res.json())
      .then(data => {
        const viewer = document.getElementById("rampLogViewer");
        if (!data.log || !Array.isArray(data.log)) return;
        let html = "<h3>Ramp-Off History</h3><ul>";
        data.log.slice(1).reverse().forEach(row => {
          html += `<li>💸 $${row[1]} → ${row[4]} (${row[2]}) — ${row[5]}</li>`;
        });
        html += "</ul>";
        viewer.innerHTML = html;
      });
  }

  // 🕒 Optional: block access outside hours
  // blockActionsIfClosed();
});
