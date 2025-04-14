document.addEventListener("DOMContentLoaded", function () {
  const loginBtn = document.getElementById("loginBtn");
  const rampBtn = document.getElementById("rampBtn");
  const mintBtn = document.getElementById("mintBtn");

  // 🕒 Enforce YET Business Hours (Mon/Wed/Fri, 09:00–11:00 PST)
  function isWithinYETHours() {
    const now = new Date();
    const day = now.getUTCDay(); // Sunday = 0, Monday = 1, etc.
    const hour = now.getUTCHours(); // UTC hours
    const pstHour = (hour + 24 - 7) % 24; // Convert to PST (UTC-7)

    const isOpenDay = [1, 3, 5].includes(day); // Mon, Wed, Fri
    const isOpenTime = pstHour >= 9 && pstHour < 11;

    return isOpenDay && isOpenTime;
  }

  function blockActionsIfClosed() {
    if (!isWithinYETHours()) {
      const elements = [loginBtn, rampBtn, mintBtn];
      elements.forEach(el => {
        if (el) el.disabled = true;
      });
      const status = document.getElementById("rampStatus");
      if (status) status.textContent = "⏳ YET is closed. Try again Mon/Wed/Fri 09–11 AM PST.";
    }
  }

  // ✅ LOGIN
  if (loginBtn) {
    loginBtn.addEventListener("click", function () {
      const savings_id = parseInt(document.getElementById("username").value);
      const phone = document.getElementById("password").value;

      if (!savings_id || !phone) {
        alert("Please enter both Savings ID and Phone Number.");
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
            document.getElementById("loginView").style.display = "none";
            document.getElementById("dashboardView").style.display = "block";
            document.getElementById("loanDiskBalance").textContent = `$${parseFloat(data.balance).toFixed(2)}`;
            fetchTotalMinted();
            renderRampLog();
          } else {
            alert("Login failed. Check your credentials.");
          }
        })
        .catch(error => {
          console.error("Login Error:", error);
          alert("Server error. Please try again later.");
        });
    });
  }

  // ✅ MINT
  if (mintBtn) {
    mintBtn.addEventListener("click", function () {
      const wallet = document.getElementById("walletAddress").value;
      const amount = document.getElementById("usdAmount").value;

      fetch("http://127.0.0.1:8000/send-stablecoin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ to_address: wallet, usd_amount: parseFloat(amount) })
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

  // ✅ RAMP OFF
  if (rampBtn) {
    rampBtn.addEventListener("click", function () {
      const bank = document.getElementById("bankName").value;
      const routing = document.getElementById("routingNumber").value;
      const account = document.getElementById("accountNumber").value;
      const amount = document.getElementById("rampAmount").value;
      const option = document.getElementById("destinationOption").value;
      const priority = option === "Personal Bank" ? "wire" : "standard";

      fetch("http://127.0.0.1:8000/ramp-off", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bank_name: bank,
          routing_number: routing,
          account_number: account,
          usd_amount: parseFloat(amount),
          destination_option: option,
          savings_id: parseInt(sessionStorage.getItem("savings_id")),
          priority: priority
        })
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById("rampStatus").textContent = `✅ Ramp off complete: ${data.status}`;
          renderRampLog(); // refresh log
        })
        .catch(() => alert("Ramp off failed."));
    });
  }

  // ✅ Fetch Mint Total
  function fetchTotalMinted() {
    fetch("http://127.0.0.1:8000/get-total-minted")
      .then(res => res.json())
      .then(data => {
        document.getElementById("totalMinted").textContent = `$${data.total.toFixed(2)}`;
      });
  }

  // ✅ Render Ramp Log Viewer
  function renderRampLog() {
    fetch("http://127.0.0.1:8000/get-ramp-log")
      .then(res => res.json())
      .then(data => {
        const viewer = document.getElementById("rampLogViewer");
        if (viewer) {
          let html = "<h3>Ramp-Off History</h3><ul>";
          data.log.slice(1).reverse().forEach(row => {
            html += `<li>💸 $${row[1]} → ${row[4]} (${row[2]}) — ${row[5]}</li>`;
          });
          html += "</ul>";
          viewer.innerHTML = html;
        }
      });
  }

  // 🕒 Block if outside business hours
  blockActionsIfClosed();
});
