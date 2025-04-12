function updateClock() {
  const now = new Date();
  const timeString = now.toLocaleTimeString("en-US", {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });

  const dateString = now.toLocaleDateString("en-US", {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  const clockElement = document.getElementById("clockDisplay");
  if (clockElement) {
    clockElement.textContent = `${dateString} — ${timeString}`;
  }
}

// Call it once immediately, then every second
updateClock();
setInterval(updateClock, 1000);
