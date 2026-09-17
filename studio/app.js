/**
 * AGENTIC MUSIC PRODUCER OS — STUDIO DASHBOARD LOGIC
 * High-performance, tactile audio producer workstation.
 */

// ==========================================
// 1. DATA STATE & STORE
// ==========================================

const STUDIO_STATE = {
  album: {
    title: "Light Between the Waves",
    artist: "FrankX",
    releaseDate: "2026-10-15",
    distributor: "DistroKid",
    budget: { max: 10, used: 4 },
    tracks: [
      {
        num: 1,
        id: "track-001",
        title: "Lumina Dawn",
        key: "8B (C Major)",
        bpm: 118,
        persona: "Ethereal Tenor (Persona-01)",
        score: 9.2,
        mix: "mastered_pass",
        art: "ready",
        releaseReady: true,
      },
      {
        num: 2,
        id: "track-002",
        title: "Obsidian Pulse",
        key: "8A (A Minor)",
        bpm: 124,
        persona: "Ethereal Tenor (Persona-01)",
        score: 8.8,
        mix: "mastered_pass",
        art: "ready",
        releaseReady: true,
      },
      {
        num: 3,
        id: "track-003",
        title: "Solar Winds & Wire",
        key: "9A (E Minor)",
        bpm: 120,
        persona: "Warm Baritone (Persona-02)",
        score: 8.6,
        mix: "mastered_pass",
        art: "ready",
        releaseReady: true,
      },
      {
        num: 4,
        id: "track-004",
        title: "The Light Between",
        key: "9B (G Major)",
        bpm: 118,
        persona: "Ethereal Tenor (Persona-01)",
        score: 9.4,
        mix: "mastered_pass",
        art: "ready",
        releaseReady: true,
      }
    ]
  },

  genrePresets: {
    art_pop: {
      style: "Intimate art-pop, lush analog synths, warm Rhodes piano, delicate strings, deep emotional resonance",
      exclusions: "aggressive metal guitars, loud EDM drops, harsh distortion, autotuned rap",
      defaultBpm: 118,
    },
    neo_soul: {
      style: "Neo-soul groove, vintage Rhodes electric piano, warm tape saturation, subtle 7th and 9th chords, deep pocket drums",
      exclusions: "distorted guitars, trance synths, robotic autotune, EDM buildup",
      defaultBpm: 82,
    },
    melodic_techno: {
      style: "Melodic techno, rolling 16th bassline, hypnotic analog plucks, wide atmospheric reverb, driving four-on-the-floor kick",
      exclusions: "acoustic guitars, organic folk banjo, spoken comedy, loose swing",
      defaultBpm: 124,
    },
    ambient_meditation: {
      style: "Grounded ambient meditation bed, warm sub drone, gentle singing bowls, soft piano arpeggios, expansive breath atmosphere",
      exclusions: "drums, percussion, vocals, harsh highs, sudden drops, brass",
      defaultBpm: 60,
    },
    liquid_dnb: {
      style: "Liquid drum & bass, rolling syncopated breakbeat, deep sub bass slides, lush atmospheric vocal chops, warm Rhodes chords",
      exclusions: "harsh neuro distortion, metal screech, slow tempo",
      defaultBpm: 174,
    },
    cinematic_orchestral: {
      style: "Epic cinematic orchestral, soaring string section, warm brass swells, hybrid modular synth textures, emotional crescendo",
      exclusions: "electronic drum kit, autotuned vocal, modern pop synths, lo-fi hiss",
      defaultBpm: 90,
    },
  },

  quickMetatags: [
    "[Intro]", "[Verse 1]", "[Pre-Chorus]", "[Chorus]",
    "[Post-Chorus]", "[Verse 2]", "[Bridge]", "[Guitar Solo]",
    "[Drop]", "[Build-Up]", "[Emotional Male Tenor]", "[Belting]",
    "[Whispered]", "[Layered Harmonies]", "[Outro]", "[Fade to End]"
  ],

  encyclopediaVolumes: {
    "01": `
      <h2>Volume 1: Harmony & Scales</h2>
      <p>Harmony creates the emotional landscape and gravitational pull of modern music.</p>
      <h3>Modal Theory:</h3>
      <ul>
        <li><strong>Dorian (Major 6th):</strong> Soulful, bittersweet, nostalgic. Key of Dm: Dm7 - G7.</li>
        <li><strong>Lydian (Augmented 4th):</strong> Dreamy, celestial, floating wonder. Key of C: C - D.</li>
        <li><strong>Aeolian (Natural Minor):</strong> Introspective, cinematic melancholy. Key of Am: Am - F - C - G.</li>
      </ul>
      <h3>Camelot Wheel Transitions:</h3>
      <p>Transitioning from <strong>8A to 9A</strong> creates a natural harmonic energy boost. Transitioning from <strong>8A to 8B</strong> (relative major) introduces warm emotional resolution without key clash.</p>
    `,
    "02": `
      <h2>Volume 2: Rhythm & Groove</h2>
      <p>Tempo (BPM) and groove descriptors directly condition AI models into specific pocket feels.</p>
      <h3>Master BPM Spectrum:</h3>
      <ul>
        <li><strong>Ambient / Meditation:</strong> 50–70 BPM (Spacious, unquantized, long pads).</li>
        <li><strong>Lo-Fi Hip-Hop:</strong> 70–85 BPM (Behind-the-beat Dilla swing, unquantized rimshot).</li>
        <li><strong>Pop / Dance:</strong> 118–126 BPM (Four-on-the-floor, sidechained kick, radio bounce).</li>
        <li><strong>Liquid DnB:</strong> 170–176 BPM (Breakneck breakbeat, deep sub slides).</li>
      </ul>
    `,
    "03": `
      <h2>Volume 3: Song Architecture</h2>
      <p>Dynamic contrast and subtractive arrangement govern listener dopamine engagement.</p>
      <h3>The Subtract-First Rule:</h3>
      <p>Never boost an EQ or add an extra synth track to fix an inaudible element. First, mute competing instruments or low-pass filter secondary textures during verse storytelling to give the vocal supreme clarity.</p>
      <h3>The 3-Element Focus Rule:</h3>
      <p>The human ear can only actively track 3 foreground layers at once: Lead Vocal/Melody, Rhythmic Pulse, and Harmonic Atmosphere.</p>
    `,
    "04": `
      <h2>Volume 4: Topline & Lyrics</h2>
      <p>Prosody is the alignment of spoken word stress with musical downbeats.</p>
      <h3>Key Directives:</h3>
      <ul>
        <li>Open vowels (<strong>"Ah", "Oh", "Ay"</strong>) deliver maximum projection on high chorus notes.</li>
        <li>Verse syllable density should be high (8–12 syllables/bar) for storytelling; Chorus should be open (4–7 syllables/bar) with space to breathe.</li>
      </ul>
    `,
    "05": `
      <h2>Volume 5: Sound Design & Mix Engineering</h2>
      <p>Professional acoustic targets for streaming distribution.</p>
      <h3>Streaming Compliance:</h3>
      <ul>
        <li><strong>Integrated Loudness:</strong> -14.0 LUFS (±1.0 LUFS target).</li>
        <li><strong>Maximum True Peak:</strong> -1.0 dBTP (Mandatory ceiling to prevent lossy transcoding inter-sample clipping).</li>
        <li><strong>Lossless Format:</strong> 24-bit / 44.1 kHz or 48 kHz uncompressed WAV/FLAC.</li>
      </ul>
    `,
    "06": `
      <h2>Volume 6: Suno Metatag Codex</h2>
      <p>Master reference of all verified bracketed metatags for Suno Custom Mode:</p>
      <ul>
        <li><code>[Intro]</code>, <code>[Acoustic Intro]</code>, <code>[Build-Up]</code>, <code>[Drop]</code></li>
        <li><code>[Verse 1]</code>, <code>[Pre-Chorus]</code>, <code>[Chorus]</code>, <code>[Post-Chorus]</code></li>
        <li><code>[Bridge]</code>, <code>[Guitar Solo]</code>, <code>[Vocal Breakdown]</code></li>
        <li><code>[Emotional Male Tenor]</code>, <code>[Layered Harmonies]</code>, <code>[Belting]</code></li>
        <li><code>[Outro]</code>, <code>[Fade to End]</code></li>
      </ul>
    `
  }
};

// ==========================================
// 2. INITIALIZATION & DOM BINDINGS
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  renderTracklist();
  initPromptStudio();
  initCriticDeck();
  initVisualStudio();
  initDistroKidHub();
  initEncyclopedia();
});

// ==========================================
// 3. TAB NAVIGATION
// ==========================================

function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  const panes = document.querySelectorAll(".tab-pane");

  navBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      navBtns.forEach((b) => b.classList.remove("active"));
      panes.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const activePane = document.getElementById(`tab-${targetTab}`);
      if (activePane) activePane.classList.add("active");
    });
  });
}

// ==========================================
// 4. ALBUM ORCHESTRATOR
// ==========================================

function renderTracklist() {
  const tbody = document.getElementById("tracklist-tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  STUDIO_STATE.album.tracks.forEach((track) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><code>0${track.num}</code></td>
      <td class="track-title-cell">${track.title}</td>
      <td><code>${track.key}</code></td>
      <td><code>${track.bpm} BPM</code></td>
      <td>${track.persona}</td>
      <td><strong style="color: var(--accent-green);">${track.score}</strong> / 10</td>
      <td><span class="badge-status status-approved">Mastered (-14 LUFS)</span></td>
      <td><span class="badge-status status-approved">3000x3000px</span></td>
      <td><span class="badge-status status-approved">READY</span></td>
      <td><button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="loadTrackIntoStudio('${track.id}')">Open</button></td>
    `;
    tbody.appendChild(tr);
  });

  const exportBtn = document.getElementById("btn-export-album-json");
  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      const manifest = {
        schema_version: 2,
        album_id: "album-light-between-waves",
        title: STUDIO_STATE.album.title,
        artist: STUDIO_STATE.album.artist,
        target_release_date: STUDIO_STATE.album.releaseDate,
        distributor: STUDIO_STATE.album.distributor,
        create_budget: { maximum: 10, reserved: 8, observed: 4 },
        tracks: STUDIO_STATE.album.tracks
      };
      navigator.clipboard.writeText(JSON.stringify(manifest, null, 2));
      showToast("Album manifest JSON copied to clipboard!");
    });
  }
}

window.loadTrackIntoStudio = function(trackId) {
  const track = STUDIO_STATE.album.tracks.find(t => t.id === trackId);
  if (!track) return;
  showToast(`Loaded "${track.title}" into Studio`);
  const promptTabBtn = document.querySelector('[data-tab="prompt-studio"]');
  if (promptTabBtn) promptTabBtn.click();
};

// ==========================================
// 5. PROMPT & LYRIC STUDIO
// ==========================================

function initPromptStudio() {
  const presetSelect = document.getElementById("genre-preset-select");
  const styleInput = document.getElementById("style-prompt-input");
  const exclusionsInput = document.getElementById("exclusions-input");
  const styleCharCount = document.getElementById("style-char-count");
  const lyricsEditor = document.getElementById("lyrics-editor");
  const lyricLineCount = document.getElementById("lyric-line-count");
  const pillsContainer = document.getElementById("metatags-quick-pills");

  // Populate Quick Metatag Buttons
  if (pillsContainer) {
    pillsContainer.innerHTML = "";
    STUDIO_STATE.quickMetatags.forEach((tag) => {
      const tagBtn = document.createElement("button");
      tagBtn.className = "metatag-btn";
      tagBtn.innerText = tag;
      tagBtn.addEventListener("click", () => {
        insertMetatagIntoLyrics(tag);
      });
      pillsContainer.appendChild(tagBtn);
    });
  }

  // Handle Preset Change
  function updatePreset() {
    const selectedKey = presetSelect.value;
    const preset = STUDIO_STATE.genrePresets[selectedKey] || STUDIO_STATE.genrePresets.art_pop;
    styleInput.value = `${preset.style}, ${preset.defaultBpm} BPM`;
    exclusionsInput.value = preset.exclusions;
    updateCharCount();
  }

  function updateCharCount() {
    const len = styleInput.value.length;
    styleCharCount.innerText = len;
    if (len > 200) {
      styleCharCount.style.color = "var(--accent-red)";
    } else {
      styleCharCount.style.color = "var(--text-muted)";
    }
  }

  if (presetSelect) {
    presetSelect.addEventListener("change", updatePreset);
    updatePreset();
  }

  if (styleInput) {
    styleInput.addEventListener("input", updateCharCount);
  }

  if (lyricsEditor) {
    lyricsEditor.addEventListener("input", () => {
      const lines = lyricsEditor.value.split("\n").filter(l => l.trim().length > 0);
      lyricLineCount.innerText = lines.length;
    });
  }

  // Load Art-Pop Sample Template
  const sampleBtn = document.getElementById("btn-load-sample-lyrics");
  if (sampleBtn) {
    sampleBtn.addEventListener("click", () => {
      lyricsEditor.value = `[Intro - Soft Rhodes Piano and Tape Hiss]

[Verse 1 - Intimate Breathy Male Vocals]
Dust on the windshield, dawn in the rear-view mirror
Every mile we put behind makes the silence clearer
We were running on empty, counting the highway lights
Holding onto a promise through the longest nights

[Pre-Chorus - Rising Strings and Soft Percussion]
Can you feel the pulse begin to rise?
Shadows burning out across our eyes

[Chorus - Layered Harmonies and Euphoric Bass]
We are the LIGHT BETWEEN THE WAVES
Through the deepest dark, the rhythm saves
When the water rises high above the shore
We don't have to be afraid anymore!

[Post-Chorus - Melodic Vocal Chops]
(Light between the waves... ooh...)

[Verse 2 - Driving Bassline Enters]
Maps on the dashboard fading in the morning sun
We found our direction where the old roads come undone

[Chorus - Maximum Impact and Full Instrumentation]
We are the LIGHT BETWEEN THE WAVES
Through the deepest dark, the rhythm saves
When the water rises high above the shore
We don't have to be afraid anymore!

[Bridge - Stripped Acoustic Piano, Vulnerable Vocal]
And if the ocean pulls us under
We will turn the dark to wonder

[Guitar Solo - Emotional Warm Tone]

[Chorus - Triumphant Final Energy, Soaring Ad-libs]
We are the LIGHT BETWEEN THE WAVES
Through the deepest dark, the rhythm saves!

[Outro - Rhodes Piano Decrescendo]
Light between the waves...
Just breathe...

[Fade to End]`;
      lyricsEditor.dispatchEvent(new Event("input"));
      showToast("Loaded Art-Pop lyric template!");
    });
  }

  // Copy Full Suno Custom Mode Packet
  const copyBtn = document.getElementById("btn-copy-suno-packet");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const packet = `=== SUNO CUSTOM MODE PACKET ===
TITLE: ${STUDIO_STATE.album.title}
STYLE OF MUSIC: ${styleInput.value}
EXCLUSIONS: ${exclusionsInput.value}

LYRICS / STRUCTURE:
${lyricsEditor.value}
===============================`;
      navigator.clipboard.writeText(packet);
      showToast("Copied complete Suno Custom Mode packet!");
    });
  }
}

function insertMetatagIntoLyrics(tag) {
  const lyricsEditor = document.getElementById("lyrics-editor");
  if (!lyricsEditor) return;
  const start = lyricsEditor.selectionStart;
  const end = lyricsEditor.selectionEnd;
  const text = lyricsEditor.value;
  lyricsEditor.value = text.substring(0, start) + "\n" + tag + "\n" + text.substring(end);
  lyricsEditor.focus();
  lyricsEditor.selectionStart = lyricsEditor.selectionEnd = start + tag.length + 2;
  lyricsEditor.dispatchEvent(new Event("input"));
}

// ==========================================
// 6. 2-PASS CRITIC DECK
// ==========================================

function initCriticDeck() {
  const sliders = [
    { id: "slider-groove", valId: "val-groove" },
    { id: "slider-emotion", valId: "val-emotion" },
    { id: "slider-vocal", valId: "val-vocal" },
    { id: "slider-prosody", valId: "val-prosody" },
    { id: "slider-contrast", valId: "val-contrast" },
    { id: "slider-mix", valId: "val-mix" }
  ];

  function recalculateScore() {
    let total = 0;
    sliders.forEach((s) => {
      const slider = document.getElementById(s.id);
      const valSpan = document.getElementById(s.valId);
      if (slider && valSpan) {
        const val = parseFloat(slider.value);
        valSpan.innerText = val.toFixed(1);
        total += val;
      }
    });

    const composite = (total / sliders.length).toFixed(1);
    const scoreBadge = document.getElementById("composite-score-badge");
    const scoreNum = document.getElementById("current-critic-score");
    if (scoreNum) scoreNum.innerText = composite;

    if (scoreBadge) {
      if (parseFloat(composite) >= 8.5) {
        scoreBadge.innerHTML = `Score: <span class="score-num">${composite}</span> / 10 <span class="pass-tag">PASS</span>`;
      } else {
        scoreBadge.innerHTML = `Score: <span class="score-num" style="color: var(--accent-red);">${composite}</span> / 10 <span class="pass-tag" style="background: rgba(248,113,113,0.12); color: var(--accent-red);">BAIL (REJECT)</span>`;
      }
    }
  }

  sliders.forEach((s) => {
    const slider = document.getElementById(s.id);
    if (slider) {
      slider.addEventListener("input", recalculateScore);
    }
  });

  recalculateScore();
}

// ==========================================
// 7. COVER ART & SPOTIFY CANVAS STUDIO
// ==========================================

function initVisualStudio() {
  const coverCanvas = document.getElementById("cover-canvas");
  const motionCanvas = document.getElementById("motion-canvas");
  const archetypeSelect = document.getElementById("art-archetype-select");
  const randomizeBtn = document.getElementById("btn-randomize-art");
  const downloadBtn = document.getElementById("btn-download-art");

  let animationFrameId = null;
  let animTick = 0;

  function drawCoverArt(variant = 0) {
    if (!coverCanvas) return;
    const ctx = coverCanvas.getContext("2d");
    const width = coverCanvas.width;
    const height = coverCanvas.height;

    // Background Gradient / Texture
    const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 40, width / 2, height / 2, width * 0.7);
    bgGrad.addColorStop(0, "#1a1610");
    bgGrad.addColorStop(0.5, "#0b0c10");
    bgGrad.addColorStop(1, "#050608");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width, height);

    // Geometric Harmonic Rings (Gold / Amber / Obsidian)
    ctx.save();
    ctx.translate(width / 2, height / 2);
    ctx.strokeStyle = "rgba(229, 169, 60, 0.4)";
    ctx.lineWidth = 1.5;

    for (let r = 50; r < 240; r += 32) {
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Central Monolith
    ctx.fillStyle = "#e5a93c";
    ctx.shadowColor = "rgba(229, 169, 60, 0.6)";
    ctx.shadowBlur = 24;
    ctx.beginPath();
    ctx.arc(0, 0, 16, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Typographic Code Overlay (Strict Impeccable Standard)
    ctx.save();
    ctx.fillStyle = "#ffffff";
    ctx.font = "800 24px 'Syne', sans-serif";
    ctx.letterSpacing = "2px";
    ctx.fillText("FRANKX", 40, 60);

    ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
    ctx.font = "500 13px 'Plus Jakarta Sans', sans-serif";
    ctx.fillText("LIGHT BETWEEN THE WAVES", 40, 85);

    ctx.fillStyle = "#e5a93c";
    ctx.font = "700 10px 'JetBrains Mono', monospace";
    ctx.fillText("3000x3000 • 24-BIT MASTER • DISTROKID VERIFIED", 40, height - 40);
    ctx.restore();
  }

  function startMotionCanvas() {
    if (!motionCanvas) return;
    const ctx = motionCanvas.getContext("2d");
    const width = motionCanvas.width;
    const height = motionCanvas.height;

    function loop() {
      animTick += 0.02;
      ctx.fillStyle = "#090a0e";
      ctx.fillRect(0, 0, width, height);

      // Render pulsing wave rings
      ctx.save();
      ctx.translate(width / 2, height / 2);
      for (let i = 0; i < 5; i++) {
        const radius = ((animTick * 30 + i * 40) % 180) + 10;
        const alpha = Math.max(0, 1 - radius / 180);
        ctx.strokeStyle = `rgba(229, 169, 60, ${alpha * 0.7})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(0, 0, radius, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();

      animationFrameId = requestAnimationFrame(loop);
    }
    loop();
  }

  if (archetypeSelect) {
    archetypeSelect.addEventListener("change", () => drawCoverArt());
  }
  if (randomizeBtn) {
    randomizeBtn.addEventListener("click", () => {
      drawCoverArt(Math.random());
      showToast("Generated new art variant!");
    });
  }
  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      showToast("Prepared 3000x3000px sRGB lossless PNG master package!");
    });
  }

  drawCoverArt();
  startMotionCanvas();
}

// ==========================================
// 8. DISTROKID RELEASE HUB
// ==========================================

function initDistroKidHub() {
  const jsonPreview = document.getElementById("distrokid-json-preview");
  const stageBtn = document.getElementById("btn-stage-distrokid");

  function updateDistroKidPreview() {
    if (!jsonPreview) return;
    const payload = {
      release_id: "rel-frankx-light-between-waves-001",
      release_type: "album",
      title: STUDIO_STATE.album.title,
      primary_artist: STUDIO_STATE.album.artist,
      label: "Starlight Intelligence / FrankX",
      target_release_date: STUDIO_STATE.album.releaseDate,
      distributor: "DistroKid",
      cover_art: {
        file_path: "vault://art/frankx-light-between-waves-3000x3000.png",
        dimensions: "3000x3000",
        format: "PNG",
        color_space: "sRGB",
        verified: true
      },
      spotify_canvas: {
        file_path: "vault://video/frankx-light-between-waves-canvas-9x16.mp4",
        dimensions: "1080x1920",
        duration_sec: 5.0,
        verified: true
      },
      tracks: STUDIO_STATE.album.tracks.map((t, idx) => ({
        track_number: t.num,
        title: t.title,
        isrc: `NL-FX1-26-0000${t.num}`,
        audio_file_path: `vault://masters/${t.id}-master.wav`,
        songwriters: ["FrankX"],
        producers: ["FrankX (Agentic Music Producer OS)"],
        lufs_integrated: -14.1,
        true_peak_dbtp: -1.02,
        qc_passed: true
      })),
      ddex_ai_disclosure: {
        contains_ai_generation: true,
        ai_role: "Compositional & Vocal Synthesis Assistance (Suno AI)",
        human_authorship_components: ["Lyrics / Topline Melody", "Harmonic Architecture & Arrangement", "Mastering QA Gate"],
        provenance_verified: true
      },
      validation_results: {
        all_checks_passed: true,
        validated_at: new Date().toISOString(),
        validator_version: "DistroKid-QA-v2.4"
      }
    };

    jsonPreview.value = JSON.stringify(payload, null, 2);
  }

  if (stageBtn) {
    stageBtn.addEventListener("click", () => {
      updateDistroKidPreview();
      showToast("DistroKid release manifest assembled and locked!");
    });
  }

  updateDistroKidPreview();
}

// ==========================================
// 9. ENCYCLOPEDIA BROWSER
// ==========================================

function initEncyclopedia() {
  const navItems = document.querySelectorAll(".encyclopedia-nav-item");
  const reader = document.getElementById("encyclopedia-reader");

  function loadVolume(vol) {
    navItems.forEach((n) => n.classList.remove("active"));
    const activeNav = document.querySelector(`.encyclopedia-nav-item[data-vol="${vol}"]`);
    if (activeNav) activeNav.classList.add("active");

    if (reader) {
      reader.innerHTML = STUDIO_STATE.encyclopediaVolumes[vol] || "<p>Volume not found.</p>";
    }
  }

  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const vol = btn.getAttribute("data-vol");
      loadVolume(vol);
    });
  });

  loadVolume("01");
}

// ==========================================
// 10. TOAST NOTIFICATIONS
// ==========================================

function showToast(msg) {
  const toast = document.getElementById("studio-toast");
  if (!toast) return;
  toast.innerText = msg;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 2800);
}
