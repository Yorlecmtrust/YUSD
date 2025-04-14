document.addEventListener("DOMContentLoaded", function () {
  const loginBtn = document.getElementById("loginBtn");
  if (loginBtn) {
    loginBtn.addEventListener("click", function () {
      const savings_id_raw = document.getElementById("username").value;
      const phone = document.getElementById("password").value;
      const savings_id = parseInt(savings_id_raw);

      console.log("Sending login:", {
        savings_id,
        phone,
        type_id: typeof savings_id
      });


      if (!savings_id || !phone) {
        alert("Please enter both Savings ID and Phone Number.");
        return;
      }

      fetch("http://127.0.0.1:8000/get-user-balance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ savings_id, phone })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          if (data.savings_id && data.balance !== undefined) {
            sessionStorage.setItem("savings_id", data.savings_id);
            sessionStorage.setItem("balance", data.balance);
            document.getElementById("loginView").style.display = "none";
            document.getElementById("dashboardView").style.display = "block";
            document.getElementById("loanDiskBalance").textContent = `$${parseFloat(data.balance).toFixed(2)}`;
            fetchTotalMinted();
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

  // MINT
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
        .then(res => res.json())
        .then(data => {
          document.getElementById("mintStatus").textContent = `✅ Sent ${data.usd_amount} YUSD`;
          document.getElementById("mintTx").textContent = `TX Hash: ${data.tx_hash}`;
          fetchTotalMinted();
        })
        .catch(() => alert("Minting failed."));
    });
  }

  // RAMP OFF
  const rampBtn = document.getElementById("rampBtn");
  if (rampBtn) {
    rampBtn.addEventListener("click", function () {
      const bank = document.getElementById("bankName").value;
      const routing = document.getElementById("routingNumber").value;
      const account = document.getElementById("accountNumber").value;
      const amount = document.getElementById("rampAmount").value;
      const option = document.getElementById("destinationOption").value;

      fetch("http://127.0.0.1:8000/ramp-off", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bank_name: bank,
          routing_number: routing,
          account_number: account,
          usd_amount: parseFloat(amount),
          destination_option: option,
          savings_id: sessionStorage.getItem("savings_id")
        })
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById("rampStatus").textContent = `✅ Ramp off complete: ${data.status}`;
        })
        .catch(() => alert("Ramp off failed."));
    });
  }

  // TOTAL MINTED
  function fetchTotalMinted() {
    fetch("http://127.0.0.1:8000/get-total-minted")
      .then(res => res.json())
      .then(data => {
        document.getElementById("totalMinted").textContent = `$${data.total.toFixed(2)}`;
      });
  }
});
