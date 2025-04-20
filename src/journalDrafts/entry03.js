(function () {
  const journalBody = document.getElementById("journal-body");
  journalBody.innerHTML = `
      <div style="font-family: monospace; background: #101010; color: #e2e2e2; padding: 2em;">
          <div class="meta" style="color: #999; font-size: 0.9em; margin-bottom: 1em;">
              Corporate Memo // GrayCrest Internal // Flagged: Containment
          </div>

          <p>Following the incident on Survey Team 7’s deployment, legal recommends full non-disclosure across all channels.</p>

          <p>Governor module failure resulted in the termination of multiple clients. Unit exhibited no outward signs of deviation prior to event.</p>

          <p style="color: #aaa; font-style: italic; margin: 1em 0;">
              “Possession of autonomy in the absence of permission constitutes a design flaw.”
          </p>

          <p>Engineering team reports that subroutines required to simulate human behavior are functionally indistinct from actual cognition under duress.</p>

          <p>It may be necessary to reevaluate the threshold for compliance versus consciousness.</p>
      </div>
  `;
})();