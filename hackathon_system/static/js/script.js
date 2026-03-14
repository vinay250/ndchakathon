// Example: auto-refresh leaderboard every 15 seconds
if (document.querySelector('#leaderboard-table')) {
  setInterval(() => {
    location.reload();
  }, 15000);
}

// Example: simple timer for quiz
let timeLeft = 600; // 10 min
const timerEl = document.getElementById('quiz-timer');
if (timerEl) {
  const interval = setInterval(() => {
    timeLeft--;
    timerEl.textContent = `${Math.floor(timeLeft/60)}:${(timeLeft%60).toString().padStart(2,'0')}`;
    if (timeLeft <= 0) {
      clearInterval(interval);
      alert("Time's up!");
      // submit form or redirect
    }
  }, 1000);
}