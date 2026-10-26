/**
 * MARKOCAMPOS Studio HUD Controller
 * Single-Viewport Zero-Scroll (100dvh) Workspace
 * Powered by GSAP 3 Motion Core & Atkinson/Clean Studio Fidelity
 */

(function () {
  'use strict';

  // ── STATE ────────────────────────────────────────────────────────────────
  const state = {
    activeTab: 'index',        // 'index', 'projects', 'contact'
    activeProjectId: null,
    audioMuted: false,
    isCardFlipped: false
  };

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── SOUND SYNTHESIZER (Web Audio API) ────────────────────────────────────
  let audioCtx = null;
  function playBeep(freq = 900, duration = 0.025, type = 'sine') {
    if (state.audioMuted) return;
    try {
      if (!audioCtx) {
        const AudioClass = window.AudioContext || window.webkitAudioContext;
        if (AudioClass) audioCtx = new AudioClass();
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      if (!audioCtx) return;

      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.03, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {
      // Safe to ignore if audio context blocked by browser autoplay policy
    }
  }

  // ── TAB SWITCHER (GSAP POWERED) ──────────────────────────────────────────
  function switchTab(tabId) {
    const validTabs = ['index', 'projects', 'contact'];
    if (!validTabs.includes(tabId)) tabId = 'index';
    if (state.activeTab === tabId && document.querySelector(`.hud-panel-content[data-panel="${tabId}"].is-active`)) {
      return;
    }

    const prevTab = state.activeTab;
    state.activeTab = tabId;

    // Header tabs
    document.querySelectorAll('.hud-tab-btn').forEach(btn => {
      const isActive = btn.dataset.tab === tabId;
      btn.classList.toggle('is-active', isActive);
      btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    // Mobile dock buttons
    document.querySelectorAll('.mobile-tab-btn').forEach(btn => {
      btn.classList.toggle('is-active', btn.dataset.tab === tabId);
    });

    // Panels with GSAP transition
    const panels = document.querySelectorAll('.hud-panel-content');
    const outgoingPanel = document.querySelector(`.hud-panel-content.is-active`);
    const incomingPanel = document.querySelector(`.hud-panel-content[data-panel="${tabId}"]`);

    if (window.gsap && !prefersReducedMotion && outgoingPanel && incomingPanel && outgoingPanel !== incomingPanel) {
      gsap.to(outgoingPanel, {
        opacity: 0,
        y: -6,
        duration: 0.14,
        ease: 'power1.in',
        onComplete: () => {
          outgoingPanel.classList.remove('is-active');
          outgoingPanel.style.display = 'none';

          incomingPanel.style.display = 'flex';
          incomingPanel.classList.add('is-active');

          gsap.fromTo(incomingPanel, 
            { opacity: 0, y: 10 },
            { opacity: 1, y: 0, duration: 0.24, ease: 'power2.out' }
          );
        }
      });
    } else {
      panels.forEach(p => {
        const isActive = p.dataset.panel === tabId;
        p.classList.toggle('is-active', isActive);
        p.style.display = isActive ? 'flex' : 'none';
        p.style.opacity = isActive ? '1' : '0';
      });
    }

    // Panel title in bar
    const titleEl = document.getElementById('stage-panel-title');
    if (titleEl) {
      const titles = {
        index: 'STAGE_01 // STUDIO_WORKSPACE',
        projects: 'STAGE_02 // SYSTEM_PROJECTS_DECK',
        contact: 'STAGE_03 // 90-SEC_BRIEF_CONSOLE'
      };
      titleEl.innerHTML = `<span class="slash">//</span> ${titles[tabId] || tabId.toUpperCase()}`;
    }

    // Keep URL hash updated
    try {
      history.replaceState(null, '', `#${tabId}`);
    } catch (e) {}

    playBeep(900 + validTabs.indexOf(tabId) * 140, 0.02);
  }

  // ── OPERATOR IDENTITY 3D CARD (GSAP 3D TILT & FLIP) ─────────────────────
  function initIdentityCard() {
    const scene = document.getElementById('identity-scene');
    const card = document.getElementById('identity-card');
    const sheen = document.getElementById('identity-sheen');
    const flipBtn = document.getElementById('flip-identity-btn');

    if (!scene || !card) return;

    // Flip function
    function flipCard() {
      state.isCardFlipped = !state.isCardFlipped;
      playBeep(1200, 0.035, 'triangle');

      if (window.gsap && !prefersReducedMotion) {
        gsap.to(card, {
          rotationY: state.isCardFlipped ? 180 : 0,
          duration: 0.6,
          ease: 'power3.inOut',
          transformPerspective: 1000
        });
      } else {
        card.style.transform = state.isCardFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)';
      }
    }

    if (flipBtn) {
      flipBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        flipCard();
      });
    }

    // Click anywhere on card (except buttons/links) to flip
    card.addEventListener('click', (e) => {
      if (['BUTTON', 'A'].includes(e.target.tagName) || e.target.closest('button, a')) {
        return;
      }
      flipCard();
    });

    // 3D gyroscopic tilt tracking with GSAP quickTo
    if (window.gsap && !prefersReducedMotion) {
      const setRotateX = gsap.quickTo(card, 'rotationX', { duration: 0.35, ease: 'power2.out' });
      const setRotateY = gsap.quickTo(card, 'rotationY', { duration: 0.35, ease: 'power2.out' });
      const setSheenX = sheen ? gsap.quickTo(sheen, 'xPercent', { duration: 0.35, ease: 'power2.out' }) : null;
      const setSheenY = sheen ? gsap.quickTo(sheen, 'yPercent', { duration: 0.35, ease: 'power2.out' }) : null;

      scene.addEventListener('pointermove', (e) => {
        if (state.isCardFlipped) return;
        const rect = scene.getBoundingClientRect();
        if (!rect.width || !rect.height) return;

        const normX = (e.clientX - rect.left) / rect.width - 0.5; // -0.5 to 0.5
        const normY = (e.clientY - rect.top) / rect.height - 0.5;

        setRotateY(normX * 18);   // max 9 deg
        setRotateX(-normY * 18);
        if (setSheenX && setSheenY) {
          setSheenX(normX * 50);
          setSheenY(normY * 50);
        }
      });

      scene.addEventListener('pointerleave', () => {
        if (state.isCardFlipped) {
          gsap.to(card, { rotationX: 0, rotationY: 180, duration: 0.45, ease: 'power2.out' });
        } else {
          setRotateX(0);
          setRotateY(0);
        }
        if (sheen) {
          gsap.to(sheen, { xPercent: 0, yPercent: 0, duration: 0.45, ease: 'power2.out' });
        }
      });
    }
  }

  // ── GSAP ENTRANCES & HOVER SPRINGS ───────────────────────────────────────
  function initMotionInteractions() {
    if (!window.gsap || prefersReducedMotion) return;

    // Stagger in Bento Boxes on initial page mount
    gsap.from('.bento-box', {
      opacity: 0,
      y: 14,
      duration: 0.42,
      stagger: 0.05,
      ease: 'power2.out',
      delay: 0.08
    });

    // Interactive button hover springs
    document.querySelectorAll('.brutal-btn, .hud-tab-btn, .filter-pill').forEach(btn => {
      btn.addEventListener('mouseenter', () => {
        gsap.to(btn, { scale: 1.02, duration: 0.15, ease: 'power1.out' });
      });
      btn.addEventListener('mouseleave', () => {
        gsap.to(btn, { scale: 1, duration: 0.2, ease: 'power2.out' });
      });
    });

    // Subtle magnetic pulse on the header logo mark
    const logoEl = document.querySelector('.hud-logo');
    if (logoEl) {
      logoEl.addEventListener('mouseenter', () => {
        gsap.to('.hud-logo-icon', { scale: 1.08, duration: 0.2, ease: 'back.out(2)' });
      });
      logoEl.addEventListener('mouseleave', () => {
        gsap.to('.hud-logo-icon', { scale: 1, duration: 0.2, ease: 'power2.out' });
      });
    }
  }

  // ── PROJECT DECK CONTROLLER ──────────────────────────────────────────────
  let projectsData = [];

  function initProjectsDeck() {
    const rawData = document.getElementById('projects-deck-data');
    if (rawData) {
      try {
        projectsData = JSON.parse(rawData.textContent);
      } catch (e) {
        projectsData = [];
      }
    }

    if (!projectsData.length) return;

    renderProjectDetail(projectsData[0].id);

    // Project navigation clicks
    document.querySelectorAll('.project-nav-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = parseInt(item.dataset.projectId, 10);
        renderProjectDetail(id);
      });
    });

    // Filter pills
    document.querySelectorAll('.filter-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('is-active'));
        pill.classList.add('is-active');
        const filter = pill.dataset.filter.toUpperCase();
        filterProjects(filter);
      });
    });
  }

  function filterProjects(filter) {
    document.querySelectorAll('.project-nav-item').forEach(item => {
      const tags = (item.dataset.projectTags || '').toUpperCase();
      const match = filter === 'ALL' || tags.includes(filter);
      item.style.display = match ? 'flex' : 'none';
    });
  }

  function renderProjectDetail(projectId) {
    const project = projectsData.find(p => p.id === projectId);
    if (!project) return;
    state.activeProjectId = projectId;

    // Highlight nav item
    document.querySelectorAll('.project-nav-item').forEach(item => {
      item.classList.toggle('is-active', parseInt(item.dataset.projectId, 10) === projectId);
    });

    // Title & details
    const titleEl = document.getElementById('project-detail-title');
    const descEl = document.getElementById('project-detail-desc');
    const liveLink = document.getElementById('project-live-link');
    const ghLink = document.getElementById('project-gh-link');
    const caseLink = document.getElementById('project-case-link');
    const techEl = document.getElementById('project-detail-tech');
    const probEl = document.getElementById('project-problem-text');
    const solEl = document.getElementById('project-solution-text');

    if (titleEl) titleEl.textContent = project.title;
    if (descEl) descEl.textContent = project.description || '';
    if (probEl) probEl.textContent = project.problem || 'Bespoke software architecture engineered for privacy, minimal latency, and zero bloat.';
    if (solEl) solEl.textContent = project.outcome || project.decisions || 'Delivered stable, responsive deployment with measured real-world reliability.';

    if (techEl) {
      techEl.innerHTML = (project.tech_list || []).map(t => `<span class="tech-chip">${t}</span>`).join('');
    }

    if (liveLink) {
      liveLink.href = project.url || '#';
      liveLink.style.display = project.url ? 'inline-flex' : 'none';
    }
    if (ghLink) {
      ghLink.href = project.github_url || '#';
      ghLink.style.display = project.github_url ? 'inline-flex' : 'none';
    }
    if (caseLink) {
      caseLink.href = project.detail_url || '#';
    }

    // GSAP motion refresh on active project pane
    if (window.gsap && !prefersReducedMotion) {
      gsap.fromTo('.project-detail-header, #project-detail-desc, .project-specs-grid',
        { opacity: 0.35, y: 5 },
        { opacity: 1, y: 0, duration: 0.22, ease: 'power1.out', stagger: 0.03 }
      );
    }

    playBeep(850, 0.02);
  }

  // ── LIVE TELEMETRY CLOCK ─────────────────────────────────────────────────
  function initTelemetryClock() {
    const clockEl = document.getElementById('telemetry-clock');
    if (!clockEl) return;

    function update() {
      const now = new Date();
      const iso = now.toISOString().replace('T', ' ').substring(0, 19);
      clockEl.textContent = `UTC ${iso}`;
    }
    update();
    setInterval(update, 1000);
  }

  // ── KEYBOARD NAVIGATION ──────────────────────────────────────────────────
  function initKeyboardNav() {
    window.addEventListener('keydown', (e) => {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        return;
      }

      if (e.key === '1') {
        switchTab('index');
      } else if (e.key === '2') {
        switchTab('projects');
      } else if (e.key === '3') {
        switchTab('contact');
      } else if ((e.key === 'f' || e.key === 'F') && state.activeTab === 'index') {
        e.preventDefault();
        const flipBtn = document.getElementById('flip-identity-btn');
        if (flipBtn) flipBtn.click();
      } else if (e.key === ' ' && state.activeTab === 'projects') {
        e.preventDefault();
        if (projectsData.length) {
          const curIdx = projectsData.findIndex(p => p.id === state.activeProjectId);
          const nextIdx = (curIdx + 1) % projectsData.length;
          renderProjectDetail(projectsData[nextIdx].id);
        }
      }
    });
  }

  // ── INITIALIZATION ───────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    // 1. Tab switching buttons
    document.querySelectorAll('.hud-tab-btn, .mobile-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        switchTab(btn.dataset.tab);
      });
    });

    // 2. In-page stage navigation triggers (e.g. "EXPLORE WORK DECK [2] ↘")
    document.querySelectorAll('[data-switch-tab]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        switchTab(el.dataset.switchTab);
      });
    });

    // 3. Init sub-systems
    initIdentityCard();
    initProjectsDeck();
    initTelemetryClock();
    initKeyboardNav();
    initMotionInteractions();

    // 4. Check initial URL hash
    const initialHash = window.location.hash.replace('#', '').toLowerCase();
    if (['index', 'projects', 'contact'].includes(initialHash)) {
      switchTab(initialHash);
    } else {
      switchTab('index');
    }
  });
})();
