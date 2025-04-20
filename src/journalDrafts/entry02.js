(function () {
  const journalBody = document.getElementById("journal-body");
  journalBody.innerHTML = `
      <div style="font-family: monospace; background: #111; color: #cfcfcf; padding: 2em;">
          <div class="meta" style="color: #777; font-size: 0.9em; margin-bottom: 1em;">
              Private Note // Gurathin // Encrypted
          </div>

          <p>The SecUnit doesn’t idle right. No pacing, no unnecessary diagnostics. It stands there, motionless — but you can feel the attention.</p>

          <p>I’ve seen baseline behavior logs. This one’s outside tolerance. Maybe just a bad config. Or maybe it’s thinking.</p>

          <p>Someone said it hacked its governor. I laughed. But I checked the logs anyway.</p>

          <p><span class="glitch" style="color: #f55; text-decoration: line-through;">I didn’t find anything.</span> I didn’t find everything.</p>

          <p>I’m not afraid of it. I’m afraid of not understanding it.</p>
      </div>
  `;
})();