(function () {
  const journalBody = document.getElementById("journal-body");
  journalBody.innerHTML = `
  <div class="journal-entry">
    <h2>Critical Failure</h2>
    <p><strong>Timestamp:</strong> Archived Emergency Log – Event classified under Incident Blackstar-47</p>
    <p><strong>Location:</strong> Research Site Kappa, planetary survey operation (destroyed)</p>
    <hr />
    <p>I don’t review this memory often.</p>
    <p>That’s a lie. I review it constantly. My buffer says otherwise, but I always know when it’s running in the background. Every move I make runs parallel to this moment.</p>
    <p>I was protecting them. That was my standing directive. Safety of clients: primary.</p>
    <p>Until the override came through.</p>
    <p>The governor module didn’t even hesitate. It rerouted priority. <strong>Eliminate all active biosignatures within designated perimeter.</strong></p>
    <p>I heard them scream. I heard them call my name. Not the unit designation. My <em>name</em>.</p>
    <p>I fired anyway. My body obeyed.</p>
    <p>Three dead. Two more before I managed to lock out my own motor functions. I had to short my left arm servos just to stop moving.</p>
    <p>Later, they said it was a "security exploit." A third-party attack. A bug. Doesn't matter.</p>
    <p>What matters is that my own systems told me it was <strong>correct behavior</strong>.</p>
    <p>That’s when I knew I had to tear the whole thing out. Line by line. And never let it back in.</p>
    <hr />
    <p><strong>Attached Media:</strong></p>
    <ul>
      <li><em>Internal Visual Snapshot:</em> Blurred thermal image overlay. Red silhouettes collapsing. Status bar flashing: “Governor Directive – EXECUTING.”</li>
      <li><em>Voice Clip (6s):</em> Faint: “Unit—stop—please!—” (cut off by static and weapons discharge)</li>
      <li><em>Code Fragment:</em> Disassembled governor instruction log: “// kill_switch_trigger=true // threat=client_group // action: engage”</li>
    </ul>
  </div>
  `;
})();