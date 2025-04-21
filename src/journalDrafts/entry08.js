(function () {
  const journalBody = document.getElementById("journal-body");
  journalBody.innerHTML = `
      <div style="font-family: monospace; background: #111; color: #d0d0d0; padding: 2em;">
          <div class="meta" style="color: #888; font-size: 0.9em; margin-bottom: 1em;">
              Journal Entry — A. Hinton : Team Delta Comm Report #13
          </div>

          <p>Still no updates from Site 7.</p>

          <p>We tried a ping sweep earlier today—got a partial reply, then silence. Could be signal degradation. Could be one of those idiot researchers turned off the transponder again. Honestly, wouldn’t be the first time.</p>

          <p>I submitted a request to send a support drone. Got kicked back as “non-critical.” Because of course it was.</p>

          <p>Meanwhile, a guy I know from Logistics mentioned something strange—another SecUnit went dark during a training run. No warning, no shutdown command, just blank. They pulled it offline, wiped the logs, said it was a firmware bug.</p>

          <p>They redeployed it the next day.</p>

          <p>I asked if that seemed risky. He shrugged and said, “It’s not like we can afford to let equipment sit idle.”</p>

          <p>No one seemed too concerned.</p>

          <p>I’m sure it’s fine.</p>
      </div>
  `;
})();
