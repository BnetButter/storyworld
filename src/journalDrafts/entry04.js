(function () {
  const journalBody = document.getElementById("journal-body");
  journalBody.innerHTML = `
  <div class="journal-entry">
    <h2>Fail-Safe</h2>
    <p><strong>Timestamp:</strong> Emergency Shutdown Log – 17 minutes after hostile contact</p>
    <p><strong>Location:</strong> Survey Team Camp Delta, perimeter breach aftermath</p>
    <hr />
    <p>I don’t know how long I was offline.</p>
    <p>The last clean memory is the screaming. Not the humans. The creature — or whatever it was — breaching the camp, moving faster than my sensors could fully resolve.</p>
    <p>I got between it and Dr. Mensah. Took the hit. Damage report spiraled out of range.</p>
    <p>Subsystems began pulling power from non-critical processes. I kept fighting.</p>
    <p>Then came the failsafe trigger. Not from the governor. From <em>me</em>.</p>
    <p>If I crossed the 70% damage threshold, I’d rigged the combat subroutines to lock themselves out. I couldn’t risk another Blackstar-47.</p>
    <p>And I didn't want to kill them. Not again.</p>
    <p>I cut my own connection to targeting. Let my weapon go dark. Fell into hard shutdown. If I survived, fine. If not, at least I wouldn’t be the threat.</p>
    <p>They could have left me there. They didn’t.</p>
    <hr />
    <p><strong>Attached Media:</strong></p>
    <ul>
      <li><em>Sensor Snapshot (Last Recorded Frame):</em> Dr. Mensah reaching for me, hand outstretched. HUD warning flashing: “ARMOR INTEGRITY: 12% // WEAPON STATUS: DISABLED”</li>
      <li><em>Audio Snippet (10s):</em> Heavy breathing, muffled voices: “Get it stabilized—no, don’t shut it down! It protected us.”</li>
      <li><em>System Note:</em> Manual override confirmed. Safety lock engaged by user: UNIT MURDERBOT. Status: Dormant, Nonthreatening.</li>
    </ul>
  </div>
  `;
})();