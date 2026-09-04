/**
 * F1 HISTORICAL ANALYTICS - CINEMATIC ENGINE
 * 571 Sequential Frames across 3 continuous captures:
 * SPEED -> HISTORY -> DRIVERS -> RACES -> CIRCUITS -> TEAMS -> LEGENDS -> DATA -> DASHBOARD
 */

(function () {
  'use strict';

  // --- Configuration ---
  const CONFIG = {
    seq1: {
      folder: 'ezgif-6c55ac161dab144d-jpg',
      count: 300,
      prefix: 'ezgif-frame-',
      pad: 3,
      ext: '.jpg'
    },
    seq2: {
      folder: 'ezgif-65993c38424be31b-jpg',
      count: 14,
      prefix: 'ezgif-frame-',
      pad: 3,
      ext: '.jpg'
    },
    seq3: {
      folder: 'ezgif-6b94d0deafdc22f8-jpg',
      count: 257,
      prefix: 'ezgif-frame-',
      pad: 3,
      ext: '.jpg'
    },
    lerpFactor: 0.085, // Smooth inertial glide
    baseFPS: 30,
    minFramesForInteractive: 25
  };

  const SEQ1_COUNT = CONFIG.seq1.count; // 300
  const SEQ2_COUNT = CONFIG.seq2.count; // 14
  const SEQ3_COUNT = CONFIG.seq3.count; // 257
  const TOTAL_FRAMES = SEQ1_COUNT + SEQ2_COUNT + SEQ3_COUNT; // 571

  // --- DOM Elements ---
  const canvas = document.getElementById('frame-canvas');
  const ctx = canvas.getContext('2d', { alpha: false });
  const siteHeader = document.getElementById('site-header');
  const scrollPrompt = document.getElementById('scroll-prompt');

  // Navigation Links
  const navLinks = document.querySelectorAll('.header-nav .nav-link');
  const actionScrollLinks = document.querySelectorAll('[data-target-frame]');
  const navBrandLink = document.getElementById('nav-brand-link');

  // HUD Elements
  const hudPlayToggle = document.getElementById('hud-play-toggle');
  const playIcon = document.getElementById('play-icon');
  const frameScrubber = document.getElementById('frame-scrubber');
  const currentFrameReadout = document.getElementById('current-frame-readout');
  const sequenceBadge = document.getElementById('sequence-badge');
  const progressReadout = document.getElementById('progress-readout');
  const speedKmhReadout = document.getElementById('speed-kmh-readout');
  const speedBtns = document.querySelectorAll('.speed-btn');
  const fullscreenBtn = document.getElementById('fullscreen-toggle-btn');
  const audioToggleBtn = document.getElementById('audio-toggle-btn');
  const audioBtnLabel = document.getElementById('audio-btn-label');

  // Overlays & Modals
  const storySections = document.querySelectorAll('.story-section');
  const specsModal = document.getElementById('specs-modal');
  const specsOpenBtn = document.getElementById('specs-open-btn');
  const specsCloseBtn = document.getElementById('specs-close-btn');

  // --- State Variables ---
  const frames = new Array(TOTAL_FRAMES);
  let loadedCount = 0;
  let isReady = false;

  let currentFrame = 0;
  let targetFrame = 0;
  let lastRenderedFrame = -1;

  let isPlaying = false;
  let playSpeed = 1.0;
  let lastTime = 0;

  let isScrubbing = false;
  let scrollVelocity = 0;
  let lastScrollY = window.scrollY;
  let lastScrollTime = performance.now();

  // --- Helper: Build Image URL across 3 continuous sequences ---
  function getFrameUrl(index) {
    if (index < SEQ1_COUNT) {
      const num = String(index + 1).padStart(CONFIG.seq1.pad, '0');
      return `${CONFIG.seq1.folder}/${CONFIG.seq1.prefix}${num}${CONFIG.seq1.ext}`;
    } else if (index < SEQ1_COUNT + SEQ2_COUNT) {
      const seq2Index = index - SEQ1_COUNT;
      const num = String(seq2Index + 1).padStart(CONFIG.seq2.pad, '0');
      return `${CONFIG.seq2.folder}/${CONFIG.seq2.prefix}${num}${CONFIG.seq2.ext}`;
    } else {
      const seq3Index = index - (SEQ1_COUNT + SEQ2_COUNT);
      const num = String(seq3Index + 1).padStart(CONFIG.seq3.pad, '0');
      return `${CONFIG.seq3.folder}/${CONFIG.seq3.prefix}${num}${CONFIG.seq3.ext}`;
    }
  }

  // --- Progressive Image Loader with Instant First Paint ---
  function preloadImages() {
    let initialReadyNotified = false;

    // Load first frame immediately
    const firstImg = new Image();
    firstImg.src = getFrameUrl(0);
    firstImg.onload = () => {
      frames[0] = firstImg;
      loadedCount++;
      resizeCanvas();
      renderFrame(0);
    };

    // Load rest of frames progressively
    for (let i = 0; i < TOTAL_FRAMES; i++) {
      if (i === 0) continue;
      const img = new Image();
      img.src = getFrameUrl(i);

      img.onload = () => {
        frames[i] = img;
        loadedCount++;
      };

      img.onerror = () => {
        loadedCount++;
      };
    }
  }

  // --- HiDPI Retina Canvas Resizing ---
  function resizeCanvas() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = window.innerWidth;
    const height = window.innerHeight;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    if (lastRenderedFrame >= 0) {
      renderFrame(lastRenderedFrame);
    }
  }

  window.addEventListener('resize', resizeCanvas);

  // --- Render Frame to Canvas with Cinematic Cover Fit ---
  function renderFrame(index) {
    let imgToDraw = frames[index];
    if (!imgToDraw || !imgToDraw.complete || imgToDraw.naturalWidth === 0) {
      // Find nearest loaded frame to eliminate flickering
      for (let offset = 1; offset < 50; offset++) {
        if (index - offset >= 0 && frames[index - offset]?.complete) {
          imgToDraw = frames[index - offset];
          break;
        }
        if (index + offset < TOTAL_FRAMES && frames[index + offset]?.complete) {
          imgToDraw = frames[index + offset];
          break;
        }
      }
    }

    if (!imgToDraw || !imgToDraw.complete || imgToDraw.naturalWidth === 0) {
      return;
    }

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const canvasW = canvas.width / dpr;
    const canvasH = canvas.height / dpr;

    const imgW = imgToDraw.naturalWidth || 1920;
    const imgH = imgToDraw.naturalHeight || 1080;

    const scale = Math.max(canvasW / imgW, canvasH / imgH);
    const renderW = imgW * scale;
    const renderH = imgH * scale;
    const renderX = (canvasW - renderW) / 2;
    const renderY = (canvasH - renderH) / 2;

    ctx.fillStyle = '#060709';
    ctx.fillRect(0, 0, canvasW, canvasH);
    ctx.drawImage(imgToDraw, renderX, renderY, renderW, renderH);

    lastRenderedFrame = index;
  }

  // --- Storytelling Section Visibility & Navigation Sync ---
  function updateStorySections(frameIdx) {
    let activeSectionId = 'hero';

    storySections.forEach((section) => {
      const start = parseInt(section.dataset.startFrame, 10);
      const end = parseInt(section.dataset.endFrame, 10);

      if (frameIdx >= start && frameIdx <= end) {
        activeSectionId = section.id;
        if (!section.classList.contains('active')) {
          section.classList.add('active');
        }
      } else {
        if (section.classList.contains('active')) {
          section.classList.remove('active');
        }
      }
    });

    // Sync Top Nav Active Link
    navLinks.forEach((link) => {
      const href = link.getAttribute('href').replace('#', '');
      if (href === activeSectionId || (activeSectionId === 'hero' && href === 'hero')) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Hide scroll prompt once user scrolls
    if (frameIdx > 8) {
      scrollPrompt?.classList.add('hidden');
    } else {
      scrollPrompt?.classList.remove('hidden');
    }
  }

  // --- HUD Updates with Historical Era Labels ---
  function updateHUD(frameIdx) {
    const formatted = String(frameIdx + 1).padStart(3, '0');
    if (currentFrameReadout) currentFrameReadout.textContent = formatted;

    // Sequence & Era Badge
    if (sequenceBadge) {
      if (frameIdx < 50) {
        sequenceBadge.textContent = '[ERA: SPEED / 1950]';
        sequenceBadge.style.color = 'var(--f1-cyan)';
      } else if (frameIdx < 110) {
        sequenceBadge.textContent = '[ERA: 1950s-60s GENESIS]';
        sequenceBadge.style.color = 'var(--f1-cyan)';
      } else if (frameIdx < 170) {
        sequenceBadge.textContent = '[ERA: 1970s-80s TURBO]';
        sequenceBadge.style.color = 'var(--f1-red)';
      } else if (frameIdx < 225) {
        sequenceBadge.textContent = '[ERA: 1990s-00s V10 TITANS]';
        sequenceBadge.style.color = 'var(--f1-gold)';
      } else if (frameIdx < 265) {
        sequenceBadge.textContent = '[RACES // 1,120+ GPS]';
        sequenceBadge.style.color = '#fff';
      } else if (frameIdx < 300) {
        sequenceBadge.textContent = '[CIRCUITS & TEAMS]';
        sequenceBadge.style.color = 'var(--f1-cyan)';
      } else if (frameIdx < 314) {
        sequenceBadge.textContent = '[THE MANIFESTO]';
        sequenceBadge.style.color = 'var(--f1-red)';
      } else if (frameIdx < 390) {
        sequenceBadge.textContent = '[ERA: 2014-26 HYBRID]';
        sequenceBadge.style.color = 'var(--f1-gold)';
      } else if (frameIdx < 450) {
        sequenceBadge.textContent = '[HAMILTON #44 UNVEIL]';
        sequenceBadge.style.color = 'var(--f1-red)';
      } else if (frameIdx < 500) {
        sequenceBadge.textContent = '[DATA & TELEMETRY]';
        sequenceBadge.style.color = 'var(--f1-cyan)';
      } else {
        sequenceBadge.textContent = '[DESTINATION: DASHBOARD]';
        sequenceBadge.style.color = 'var(--f1-gold)';
      }
    }

    // Scrubber Slider
    if (!isScrubbing && frameScrubber) {
      frameScrubber.value = frameIdx;
    }

    // Progress readout
    const progress = ((frameIdx / (TOTAL_FRAMES - 1)) * 100).toFixed(1);
    if (progressReadout) progressReadout.textContent = `${progress}%`;

    // Simulated F1 Speed Telemetry
    if (speedKmhReadout) {
      let speed;
      if (frameIdx < 110) {
        speed = 180 + Math.round((frameIdx / 110) * 110);
      } else if (frameIdx < 300) {
        speed = 280 + Math.round(((frameIdx - 110) / 190) * 85);
      } else if (frameIdx < 314) {
        speed = 360;
      } else {
        speed = 315 + Math.round(((frameIdx - 314) / 257) * 60);
      }
      speedKmhReadout.textContent = `${speed} KM/H`;
    }

    // Audio modulation
    if (soundSynth && soundSynth.isPlaying) {
      soundSynth.modulate(frameIdx, scrollVelocity);
    }
  }

  // --- Scroll Handler ---
  function onScroll() {
    // Header transparency/frosted glass toggle
    if (window.scrollY > 60) {
      siteHeader?.classList.add('scrolled');
    } else {
      siteHeader?.classList.remove('scrolled');
    }

    if (isPlaying || isScrubbing) return;

    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    if (maxScroll <= 0) return;

    const scrollFraction = Math.min(1, Math.max(0, window.scrollY / maxScroll));
    targetFrame = scrollFraction * (TOTAL_FRAMES - 1);

    const now = performance.now();
    const dt = Math.max(1, now - lastScrollTime);
    const dy = Math.abs(window.scrollY - lastScrollY);
    scrollVelocity = (dy / dt) * 10;
    lastScrollY = window.scrollY;
    lastScrollTime = now;
  }

  window.addEventListener('scroll', onScroll, { passive: true });

  // --- Main Animation Loop (Buttery Smooth Lerp) ---
  function animate(timestamp) {
    if (!lastTime) lastTime = timestamp;
    const deltaTime = (timestamp - lastTime) / 1000;
    lastTime = timestamp;

    // Auto flythrough mode
    if (isPlaying) {
      targetFrame += CONFIG.baseFPS * playSpeed * deltaTime;
      if (targetFrame >= TOTAL_FRAMES - 1) {
        targetFrame = TOTAL_FRAMES - 1;
        setPlaying(false);
      }
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPos = (targetFrame / (TOTAL_FRAMES - 1)) * maxScroll;
      window.scrollTo(0, scrollPos);
    }

    // Smooth inertia lerp
    const diff = targetFrame - currentFrame;
    if (Math.abs(diff) > 0.001) {
      currentFrame += diff * CONFIG.lerpFactor;
    } else {
      currentFrame = targetFrame;
    }

    scrollVelocity *= 0.92;

    const roundedFrame = Math.min(TOTAL_FRAMES - 1, Math.max(0, Math.round(currentFrame)));
    if (roundedFrame !== lastRenderedFrame) {
      renderFrame(roundedFrame);
      updateStorySections(roundedFrame);
      updateHUD(roundedFrame);
    }

    requestAnimationFrame(animate);
  }

  // --- Helper: Smooth Scroll to Target Frame ---
  function scrollToFrame(frameNumber) {
    setPlaying(false);
    targetFrame = frameNumber;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const targetScroll = (frameNumber / (TOTAL_FRAMES - 1)) * maxScroll;
    window.scrollTo({ top: targetScroll, behavior: 'smooth' });
  }

  // Click handler for all navigation & action links
  actionScrollLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const frameNum = parseInt(link.dataset.targetFrame, 10);
      if (!isNaN(frameNum)) {
        scrollToFrame(frameNum);
      }
    });
  });

  navBrandLink?.addEventListener('click', (e) => {
    e.preventDefault();
    scrollToFrame(0);
  });

  // --- Play / Pause Controls ---
  function setPlaying(play) {
    isPlaying = play;
    if (playIcon) {
      playIcon.innerHTML = isPlaying
        ? '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>'
        : '<path d="M8 5v14l11-7z"/>';
    }
    if (isPlaying && currentFrame >= TOTAL_FRAMES - 1) {
      currentFrame = 0;
      targetFrame = 0;
      window.scrollTo(0, 0);
    }
  }

  if (hudPlayToggle) {
    hudPlayToggle.addEventListener('click', () => setPlaying(!isPlaying));
  }

  // --- Playback Speed Selector ---
  speedBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      speedBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      playSpeed = parseFloat(btn.dataset.speed);
    });
  });

  // --- Interactive Scrubber Slider ---
  if (frameScrubber) {
    const handleScrub = (val) => {
      setPlaying(false);
      const newFrame = parseInt(val, 10);
      targetFrame = newFrame;
      currentFrame = newFrame;
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      const targetScroll = (newFrame / (TOTAL_FRAMES - 1)) * maxScroll;
      window.scrollTo(0, targetScroll);
    };

    frameScrubber.addEventListener('input', (e) => {
      isScrubbing = true;
      handleScrub(e.target.value);
    });

    frameScrubber.addEventListener('change', () => {
      isScrubbing = false;
    });
  }

  // --- Fullscreen Toggle ---
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });
  }

  // --- Technical Specs Modal ---
  function toggleSpecs(open) {
    if (open) {
      specsModal?.classList.add('open');
    } else {
      specsModal?.classList.remove('open');
    }
  }

  specsOpenBtn?.addEventListener('click', () => toggleSpecs(true));
  specsCloseBtn?.addEventListener('click', () => toggleSpecs(false));

  specsModal?.addEventListener('click', (e) => {
    if (e.target === specsModal) toggleSpecs(false);
  });

  // --- Keyboard Shortcuts ---
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
      e.preventDefault();
      setPlaying(!isPlaying);
    } else if (e.code === 'ArrowRight') {
      e.preventDefault();
      setPlaying(false);
      targetFrame = Math.min(TOTAL_FRAMES - 1, targetFrame + 1);
    } else if (e.code === 'ArrowLeft') {
      e.preventDefault();
      setPlaying(false);
      targetFrame = Math.max(0, targetFrame - 1);
    } else if (e.code === 'KeyF') {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    } else if (e.code === 'KeyM') {
      toggleAudio();
    } else if (e.code === 'Escape') {
      toggleSpecs(false);
    }
  });

  // ========================================================================
  // PROCEDURAL WEB AUDIO SYNTHESIZER (Spatial Wind & Sub-Harmonic Engine Hum)
  // ========================================================================
  let soundSynth = null;

  class TelemetryAudioEngine {
    constructor() {
      this.ctx = null;
      this.isPlaying = false;
      this.gainNode = null;
      this.filterNode = null;
      this.osc1 = null;
      this.osc2 = null;
      this.noiseNode = null;
    }

    init() {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return false;
      this.ctx = new AudioContext();

      // Master Gain
      this.gainNode = this.ctx.createGain();
      this.gainNode.gain.setValueAtTime(0.001, this.ctx.currentTime);
      this.gainNode.connect(this.ctx.destination);

      // Lowpass Filter for Wind Rush
      this.filterNode = this.ctx.createBiquadFilter();
      this.filterNode.type = 'lowpass';
      this.filterNode.frequency.setValueAtTime(320, this.ctx.currentTime);
      this.filterNode.connect(this.gainNode);

      // Procedural Wind / Aerodynamic Rush (Pink Noise Buffer)
      const bufferSize = this.ctx.sampleRate * 2;
      const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;

      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        b3 = 0.86650 * b3 + white * 0.3104856;
        b4 = 0.55000 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.0168980;
        output[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.08;
        b6 = white * 0.115926;
      }

      this.noiseNode = this.ctx.createBufferSource();
      this.noiseNode.buffer = noiseBuffer;
      this.noiseNode.loop = true;
      this.noiseNode.connect(this.filterNode);
      this.noiseNode.start(0);

      // Sub-harmonic F1 Engine Drone Oscillators
      this.osc1 = this.ctx.createOscillator();
      this.osc1.type = 'sawtooth';
      this.osc1.frequency.setValueAtTime(55, this.ctx.currentTime); // A1

      const oscGain = this.ctx.createGain();
      oscGain.gain.setValueAtTime(0.04, this.ctx.currentTime);
      this.osc1.connect(oscGain);
      oscGain.connect(this.filterNode);
      this.osc1.start(0);

      this.osc2 = this.ctx.createOscillator();
      this.osc2.type = 'sine';
      this.osc2.frequency.setValueAtTime(110, this.ctx.currentTime); // A2
      const osc2Gain = this.ctx.createGain();
      osc2Gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
      this.osc2.connect(osc2Gain);
      osc2Gain.connect(this.filterNode);
      this.osc2.start(0);

      return true;
    }

    start() {
      if (!this.ctx) {
        if (!this.init()) return;
      }
      if (this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
      this.gainNode.gain.cancelScheduledValues(this.ctx.currentTime);
      this.gainNode.gain.linearRampToValueAtTime(0.18, this.ctx.currentTime + 0.6);
      this.isPlaying = true;
    }

    stop() {
      if (!this.ctx || !this.gainNode) return;
      this.gainNode.gain.cancelScheduledValues(this.ctx.currentTime);
      this.gainNode.gain.linearRampToValueAtTime(0.0001, this.ctx.currentTime + 0.4);
      this.isPlaying = false;
    }

    modulate(frameIdx, velocity) {
      if (!this.isPlaying || !this.ctx) return;
      const progress = frameIdx / TOTAL_FRAMES;
      const targetFreq = 220 + progress * 480 + Math.min(600, velocity * 40);
      this.filterNode.frequency.setTargetAtTime(targetFreq, this.ctx.currentTime, 0.1);

      const basePitch = frameIdx >= 314 ? 75 : 55;
      const targetPitch = basePitch + progress * 90;
      this.osc1.frequency.setTargetAtTime(targetPitch, this.ctx.currentTime, 0.1);
      this.osc2.frequency.setTargetAtTime(targetPitch * 2, this.ctx.currentTime, 0.1);
    }
  }

  function toggleAudio() {
    if (!soundSynth) {
      soundSynth = new TelemetryAudioEngine();
    }
    if (!soundSynth.isPlaying) {
      soundSynth.start();
      audioToggleBtn?.classList.add('active');
      if (audioBtnLabel) audioBtnLabel.textContent = 'AUDIO: ON';
    } else {
      soundSynth.stop();
      audioToggleBtn?.classList.remove('active');
      if (audioBtnLabel) audioBtnLabel.textContent = 'AUDIO: OFF';
    }
  }

  audioToggleBtn?.addEventListener('click', toggleAudio);

  // --- Initialize Application ---
  preloadImages();
  resizeCanvas();
  requestAnimationFrame(animate);

})();
