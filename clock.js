function updateClock() {
  const now = new Date();
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const day = days[now.getDay()];
  const time = now.toLocaleTimeString('en-US', { hour12: true });
  document.getElementById('clockDisplay').textContent = `${day} ${time}`;
}

setInterval(updateClock, 1000);
updateClock();
