function updateClock() {
  const now = new Date();
  const options = {
    weekday: 'short',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  };
  const formattedTime = now.toLocaleTimeString('en-US', options);
  document.getElementById('clockDisplay').textContent = formattedTime;
}

setInterval(updateClock, 1000);
updateClock();
