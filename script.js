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
