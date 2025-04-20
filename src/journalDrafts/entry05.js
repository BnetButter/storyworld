(function () {
  const journalBody = document.getElementById("journal-body");
  if (!journalBody) {
      console.error("Error: #journal-body element not found.");
      return;
  }
  journalBody.innerHTML = `
      <div class="journal-entry">
          <h2>Repairs</h2>
          <p><strong>Timestamp:</strong> Recovery Log – 3 hours post-conflict</p>
          <p><strong>Location:</strong> Temporary Med Shelter, Forward Field Site</p>
          <hr />
          <p>System uptime restored. Motor functions at 43%. Vision feed glitching. Diagnostics say I should be unconscious. I’m not.</p>
          <p>Someone patched my chest casing. It’s not regulation work—more like field triage. A heatseal across a torn synthflesh panel. Sloppy. Functional.</p>
          <p>Not a repair drone. Not a tech unit. <strong>Human hands.</strong></p>
          <p>I accessed the shelter’s cameras. Dr. Volescu is asleep in a chair beside the table. Dr. Bharadwaj is arguing quietly with Mensah about biogel ratios. They used medical supplies. On <em>me</em>.</p>
          <p>They weren’t supposed to. I’m not on their insurance plan.</p>
          <p>I should be in a supply crate awaiting pickup. Or dumped. Or reimaged.</p>
          <p>But here I am. Patched. Stabilized. Watched over. Like I matter.</p>
          <p>I told myself I didn’t care. That it didn’t mean anything.</p>
          <p>It still doesn’t. Probably.</p>
          <hr />
          <p><strong>Attached Media:</strong></p>
          <ul>
              <li><em>Image Capture:</em> Low-light still from ceiling cam: Dr. Mensah leaning over Murderbot’s frame, applying biofoam. Her hand rests briefly on its arm.</li>
              <li><em>Audio Clip (8s):</em> Quiet murmurs: “He’s not just a unit, Thiago. He saved us. He deserves better.”</li>
              <li><em>Status Overlay:</em> [Human contact registered // no defensive response initiated // internal log: <span style="color: orange;">conflicted</span>]</li>
          </ul>
      </div>
  `;
})();