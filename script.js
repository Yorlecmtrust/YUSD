
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const dashboard = document.getElementById("dashboard");

  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const pass = document.getElementById("password").value;
    if (email && pass) {
      loginForm.style.display = "none";
      dashboard.style.display = "block";
    } else {
      alert("Login failed");
    }
  });

  document.getElementById("logoutBtn").addEventListener("click", () => {
    dashboard.style.display = "none";
    loginForm.style.display = "block";
  });

  fetch("http://localhost:8000/get-loandisk-balance")
    .then(res => res.json())
    .then(data => {
      document.getElementById("loandiskBalance").textContent = data.balance.toFixed(2);
    });

  fetch("http://localhost:8000/get-price")
    .then(res => res.json())
    .then(data => {
      document.getElementById("priceUSD").textContent = `$${data.price_usd.toFixed(2)}`;
    });
});
