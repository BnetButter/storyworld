(function () {
  const journalBody = document.getElementById("journal-body");
  journalBody.innerHTML = `
      <div style="font-family: monospace; background: #111; color: #d0d0d0; padding: 2em;">
          <div class="meta" style="color: #888; font-size: 0.9em; margin-bottom: 1em;">
              Log Entry // Dr. Volescu // PreservationAux
          </div>

          <p>This was supposed to be a routine survey. Mild atmospheric variables, standard geological markers. Low threat assessment.</p>

          <p>We arrived on-site with one (1) SecUnit assigned to our group. Standard corporate issue. I remember thinking it looked... bored. Not that they’re supposed to feel that.</p>

          <p>First anomaly was logged twelve hours after arrival. That’s when things started to feel 
              <span class="glitch" style="color: #f66; text-decoration: line-through;">off</span> interesting.
          </p>

          <p>I should have paid more attention to what it wasn’t saying.</p>
      </div>
  `;
})();