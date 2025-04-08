document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const dashboard = document.getElementById("dashboard");
  const loginPage = document.getElementById("loginPage");

  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      localStorage.setItem("loggedIn", "true");
      loginPage.classList.add("hidden");
      dashboard.classList.remove("hidden");
    });
  }

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("loggedIn");
      location.reload();
    });
  }

  const makeAnotherBtn = document.getElementById("anotherBtn");
  if (makeAnotherBtn) {
    makeAnotherBtn.addEventListener("click", () => {
      document.getElementById("transactionForm").reset();
      document.getElementById("status").classList.add("hidden");
    });
  }

  const priceElement = document.getElementById("priceUSD");
  if (priceElement) {
    fetch("http://localhost:8000/get-price")
      .then(res => res.json())
      .then(data => priceElement.textContent = `$${data.price_usd.toFixed(2)}`)
      .catch(() => priceElement.textContent = "Unavailable");
  }

  const loandiskElement = document.getElementById("loandiskBalance");
  if (loandiskElement) {
    fetch("http://localhost:8000/get-loandisk-balance")
      .then(res => res.json())
      .then(data => loandiskElement.textContent = `$${data.balance.toFixed(2)}`)
      .catch(() => loandiskElement.textContent = "$0.00");
  }

  const form = document.getElementById("transactionForm");
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const to_address = document.getElementById("wallet").value;
      const usd_amount = document.getElementById("amount").value;

      const payload = { to_address, usd_amount: parseFloat(usd_amount) };
      try {
        const res = await fetch("http://localhost:8000/send-stablecoin", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (res.ok) {
          document.getElementById("result").textContent = `✅ Minted ${usd_amount} YUSD to ${to_address}`;
        } else {
          document.getElementById("result").textContent = `❌ ${data.detail}`;
        }
        document.getElementById("status").classList.remove("hidden");
      } catch (err) {
        document.getElementById("result").textContent = `❌ ${err.message}`;
        document.getElementById("status").classList.remove("hidden");
      }
    });
  }

  setInterval(() => {
    const now = new Date();
    const clock = document.getElementById("clock");
    if (clock) clock.textContent = now.toLocaleTimeString();
  }, 1000);
});
