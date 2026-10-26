/* Home game controller — scenes, pixel-wipe transitions, level select, coins. GSAP 3. */
(function () {
  'use strict';
  if (!window.gsap) return;

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var game = $('#game');
  if (!game) return;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(pointer: fine)').matches;
  if (reduced) gsap.defaults({ duration: 0 });

  var scenes = {};
  $$('.scene').forEach(function (s) { scenes[s.dataset.scene] = s; });
  var TOTAL_COINS = 5;
  var COIN_HOME = ['hub', 'levels', 'player', 'hub', 'title'];
  var state = { scene: 'title', busy: false, coins: {}, lv: 0, isPlayerFlipped: false };
  var sceneTimeline;
  var sceneFocus = {};
  game.classList.add('is-ready');

  var elLv = $('#g-lv');
  var elXp = $('#g-xp');
  var pips = $$('#g-coins b');

  // ── Pixel wipe ───────────────────────────────────────────────────────────
  var wipe = $('#g-wipe');
  for (var i = 0; i < 96; i++) wipe.appendChild(document.createElement('i'));
  var cells = $$('i', wipe);

  function go(name, fromHistory) {
    if (!scenes[name]) return;
    if (state.busy) {
      if (!fromHistory) return;
      sceneTimeline.kill();
      gsap.set(cells, { scale: 0 });
      state.busy = false;
    }
    if (name === state.scene) return;
    if (scenes[state.scene].contains(document.activeElement)) {
      sceneFocus[state.scene] = document.activeElement;
    }
    if (!fromHistory) history.pushState(null, '', '#' + name);
    state.busy = true;
    if (reduced) { swap(name); state.busy = false; return; }
    sceneTimeline = gsap.timeline({ onComplete: function () { state.busy = false; } })
      .to(cells, { scale: 1.02, duration: 0.08, stagger: { amount: 0.045, from: 'random' }, ease: 'steps(3)' })
      .add(function () { swap(name); })
      .to(cells, { scale: 0, duration: 0.08, stagger: { amount: 0.045, from: 'random' }, ease: 'steps(3)' });
  }

  function swap(name) {
    scenes[state.scene].classList.remove('is-active');
    state.scene = name;
    game.dataset.scene = name;
    scenes[name].classList.add('is-active');
    spawnCoins();
    if (!reduced && enter[name]) enter[name]();
    else if (name === 'levels') select(index, true);
    var focus = name === 'hub' && sceneFocus.hub;
    if (!focus || !focus.isConnected) focus = $('h1, .scene-heading', scenes[name]);
    if (focus) focus.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  // ── Scene entrances ──────────────────────────────────────────────────────
  var enter = {
    title: function () {
      gsap.fromTo('#cart', { scale: 0.4, rotation: -10, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.7, ease: 'back.out(1.7)' });
      gsap.fromTo('#g-start', { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, delay: 0.5, ease: 'steps(4)' });
    },
    hub: function () {
      gsap.fromTo('.tile', { y: 50, scale: 0.8, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: 0.5, stagger: 0.08, ease: 'back.out(1.8)' });

    },
    levels: function () {
      select(index, true);
      gsap.fromTo('.lv-card', { y: 60, opacity: 0 }, { y: 0, duration: 0.5, stagger: 0.07, ease: 'back.out(1.5)', overwrite: 'auto',
        onComplete: function () { select(index, true); } });
    },
    player: function () {
      gsap.fromTo('#p-card-3d', { scale: 0.7, rotationY: -35, opacity: 0 }, { scale: 1, rotationY: state.isPlayerFlipped ? 180 : 0, opacity: 1, duration: 0.7, ease: 'back.out(1.6)' });
      gsap.fromTo('.p-side > *', { x: 50, opacity: 0 }, { x: 0, opacity: 1, duration: 0.45, stagger: 0.08, delay: 0.2 });

    }
  };

  // ── Level select carousel ────────────────────────────────────────────────
  var view = $('#lv-view');
  var track = $('#lv-track');
  var cards = $$('.lv-card');
  var dots = $$('#lv-dots i');
  var index = 0;
  var dragged = false;

  function select(n, instant) {
    if (!cards.length) return;
    index = Math.max(0, Math.min(cards.length - 1, n));
    var c = cards[index];
    var x = view.clientWidth / 2 - (c.offsetLeft + c.offsetWidth / 2);
    gsap.to(track, { x: x, duration: instant || reduced ? 0 : 0.5, ease: 'power3.out', overwrite: 'auto' });
    cards.forEach(function (el, k) {
      var on = k === index;
      el.classList.toggle('is-on', on);
      el.tabIndex = on ? 0 : -1;
      if (on) el.setAttribute('aria-current', 'true');
      else el.removeAttribute('aria-current');
      gsap.to(el, { scale: on ? 1 : 0.82, opacity: on ? 1 : 0.45, duration: instant || reduced ? 0 : 0.4, overwrite: 'auto' });
    });
    dots.forEach(function (d, k) { d.classList.toggle('on', k === index); });
    $('#lv-prev').disabled = index === 0;
    $('#lv-next').disabled = index === cards.length - 1;
  }

  $('#lv-prev').addEventListener('click', function () { select(index - 1); });
  $('#lv-next').addEventListener('click', function () { select(index + 1); });
  cards.forEach(function (el, k) {
    el.addEventListener('click', function (e) {
      if (dragged || k !== index) { e.preventDefault(); if (!dragged) select(k); }
    });
  });
  var sx = null;
  view.addEventListener('pointerdown', function (e) { sx = e.clientX; dragged = false; });
  window.addEventListener('pointerup', function (e) {
    if (sx === null) return;
    var dx = e.clientX - sx;
    sx = null;
    if (Math.abs(dx) > 50) { dragged = true; select(index + (dx < 0 ? 1 : -1)); setTimeout(function () { dragged = false; }, 50); }
  });
  window.addEventListener('resize', function () { if (state.scene === 'levels') select(index, true); });

  // ── Navigation wiring ────────────────────────────────────────────────────
  $$('[data-go]').forEach(function (b) {
    b.addEventListener('click', function (e) {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      go(b.dataset.go);
    });
  });
  function sceneFromHash() {
    var name = location.hash.slice(1);
    return scenes[name] ? name : 'title';
  }
  window.addEventListener('hashchange', function () { go(sceneFromHash(), true); });
  $('#g-start').addEventListener('click', function () { go('hub'); });

  document.addEventListener('keydown', function (e) {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey ||
        e.target.closest('input, textarea, select, summary, [contenteditable]')) return;
    var interactive = e.target.closest('a, button');
    if (interactive && e.key !== 'Escape' && e.key.indexOf('Arrow') !== 0) return;
    var s = state.scene;
    if (e.key === 'Escape') {
      if (s === 'levels' || s === 'player') go('hub');
    } else if (s === 'title' && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault(); go('hub');
    } else if (s === 'player' && (e.key === 'f' || e.key === 'F' || e.key === ' ')) {
      e.preventDefault();
      flipPlayerCard();
    } else if (s === 'levels') {
      if (interactive && !interactive.closest('.scene-levels')) return;
      if (e.key === 'ArrowRight') { e.preventDefault(); select(index + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); select(index - 1); }
      if (e.key === 'Enter' && cards[index] && document.activeElement.tagName !== 'BUTTON') cards[index].click();
    } else if (s === 'hub') {
      if (interactive && !interactive.closest('.hub')) return;
      var tiles = $$('.tile');
      var at = tiles.indexOf(document.activeElement);
      var step = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: 2, ArrowUp: -2 }[e.key];
      if (step) { e.preventDefault(); tiles[Math.max(0, Math.min(tiles.length - 1, at + step))].focus(); }
    }
  });

  // ── 3D Player Card Flip & Tilt ───────────────────────────────────────────
  function flipPlayerCard() {
    var card = $('#p-card-3d');
    if (!card) return;
    state.isPlayerFlipped = !state.isPlayerFlipped;
    $('#p-flip').setAttribute('aria-pressed', String(state.isPlayerFlipped));
    $('.p-front').setAttribute('aria-hidden', String(state.isPlayerFlipped));
    $('.p-back').setAttribute('aria-hidden', String(!state.isPlayerFlipped));
    if (reduced) {
      card.style.transform = state.isPlayerFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)';
      return;
    }
    gsap.to(card, {
      rotationY: state.isPlayerFlipped ? 180 : 0,
      duration: 0.65,
      ease: 'power3.inOut',
      transformPerspective: 1200
    });
  }

  var pCard = $('#p-card-3d');
  $('#p-flip').addEventListener('click', flipPlayerCard);

  var pScene = $('#p-scene');
  var pSheens = $$('.p-card-sheen');
  if (pScene && pCard && fine && !reduced) {
    var pRotX = gsap.quickTo(pCard, 'rotationX', { duration: 0.25, ease: 'power2.out' });
    var pRotY = gsap.quickTo(pCard, 'rotationY', { duration: 0.25, ease: 'power2.out' });
    var sheenUpdaters = pSheens.map(function (s) {
      return {
        x: gsap.quickTo(s, 'x', { duration: 0.25, ease: 'power2.out' }),
        y: gsap.quickTo(s, 'y', { duration: 0.25, ease: 'power2.out' })
      };
    });
    gsap.set(pCard, { transformPerspective: 1200 });

    pScene.addEventListener('pointermove', function (e) {
      var r = pScene.getBoundingClientRect();
      var nx = (e.clientX - r.left) / r.width - 0.5;
      var ny = (e.clientY - r.top) / r.height - 0.5;
      var baseY = state.isPlayerFlipped ? 180 : 0;
      pRotY(baseY + nx * 28);
      pRotX(-ny * 24);
      sheenUpdaters.forEach(function (u) {
        u.x(nx * 140);
        u.y(ny * 140);
      });
    });

    pScene.addEventListener('pointerleave', function () {
      pRotX(0);
      pRotY(state.isPlayerFlipped ? 180 : 0);
      sheenUpdaters.forEach(function (u) {
        u.x(0);
        u.y(0);
      });
    });
  }

  // ── Tile tilt (desktop) ──────────────────────────────────────────────────
  if (fine && !reduced) {
    $$('.tile').forEach(function (t) {
      var rx = gsap.quickTo(t, 'rotationX', { duration: 0.3 });
      var ry = gsap.quickTo(t, 'rotationY', { duration: 0.3 });
      gsap.set(t, { transformPerspective: 700 });
      t.addEventListener('pointermove', function (e) {
        var r = t.getBoundingClientRect();
        ry(((e.clientX - r.left) / r.width - 0.5) * 14);
        rx(-((e.clientY - r.top) / r.height - 0.5) * 14);
      });
      t.addEventListener('pointerleave', function () { rx(0); ry(0); });
    });
    var cart = gsap.quickTo('#cart', 'x', { duration: 0.6 });
    var cartY = gsap.quickTo('#cart', 'y', { duration: 0.6 });
    var glow = gsap.quickTo('.g-glow', 'x', { duration: 1.2 });
    var glowY = gsap.quickTo('.g-glow', 'y', { duration: 1.2 });
    window.addEventListener('pointermove', function (e) {
      var nx = e.clientX / innerWidth - 0.5, ny = e.clientY / innerHeight - 0.5;
      if (state.scene === 'title') { cart(nx * 30); cartY(ny * 20); }
      glow(nx * 120); glowY(ny * 120);
    });
  }

  // ── Coins (collectibles) ─────────────────────────────────────────────────
  function spawnCoins() {
    $$('.coin').forEach(function (c) { c.remove(); });
    COIN_HOME.forEach(function (home, n) {
      if (home !== state.scene || state.coins[n]) return;
      var c = document.createElement('button');
      c.type = 'button';
      c.className = 'coin';
      c.setAttribute('aria-label', 'Collect');
      c.style.left = (8 + Math.random() * 80) + '%';
      c.style.top = (16 + Math.random() * 60) + '%';
      game.appendChild(c);
      if (!reduced) gsap.from(c, { scale: 0, rotation: 180, duration: 0.5, delay: 0.6 + Math.random() * 0.6, ease: 'back.out(2)' });
      if (!reduced) gsap.to(c, { y: -14, duration: 1 + Math.random() * 0.6, yoyo: true, repeat: -1, ease: 'sine.inOut' });
      c.addEventListener('click', function () { collect(n, c); });
    });
  }

  function collect(n, el) {
    if (state.coins[n]) return;
    state.coins[n] = true;
    var r = el.getBoundingClientRect();
    burst(r.left + r.width / 2, r.top + r.height / 2, 10);
    gsap.killTweensOf(el);
    if (reduced) el.remove();
    else gsap.to(el, { scale: 0, opacity: 0, duration: 0.2, onComplete: function () { el.remove(); } });
    var total = Object.keys(state.coins).length;
    pips[total - 1].classList.add('on');
    elLv.textContent = total + 1;
    gsap.to(elXp, { scaleX: total / TOTAL_COINS, duration: reduced ? 0 : 0.4, ease: 'steps(8)' });
    if (!reduced) gsap.fromTo('.g-stats', { scale: 1.15 }, { scale: 1, duration: 0.3, transformOrigin: 'right center' });
    if (total === TOTAL_COINS) levelUp();
  }

  function burst(cx, cy, count) {
    if (reduced) return;
    for (var k = 0; k < count; k++) {
      var p = document.createElement('i');
      p.className = 'g-spark';
      p.style.left = cx + 'px';
      p.style.top = cy + 'px';
      game.appendChild(p);
      var a = (k / count) * Math.PI * 2, d = 40 + Math.random() * 70;
      gsap.to(p, { x: Math.cos(a) * d, y: Math.sin(a) * d, opacity: 0, rotation: 90, duration: 0.6 + Math.random() * 0.3,
        ease: 'steps(6)', onComplete: function () { this.targets()[0].remove(); } });
    }
  }

  function levelUp() {
    var toast = $('#g-toast');
    toast.classList.add('is-on');
    if (reduced) {
      $('#tile-join').classList.add('is-hot');
      setTimeout(function () { toast.classList.remove('is-on'); }, 2600);
      return;
    }
    gsap.fromTo(toast, { opacity: 0 }, { opacity: 1, duration: 0.2 });
    gsap.fromTo('#g-toast img', { scale: 0, rotation: -20 }, { scale: 1, rotation: 0, duration: 0.6, ease: 'back.out(2)' });
    gsap.fromTo('#g-toast h2', { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, delay: 0.3, ease: 'steps(5)' });
    burst(innerWidth / 2, innerHeight / 2, 24);
    $('#tile-join').classList.add('is-hot');
    function close() {
      gsap.to(toast, { opacity: 0, duration: 0.2, onComplete: function () { toast.classList.remove('is-on'); } });
      toast.removeEventListener('click', close);
    }
    toast.addEventListener('click', close);
    setTimeout(close, 2600);
  }

  // ── Boot ─────────────────────────────────────────────────────────────────
  gsap.set(cells, { scale: 0 });
  gsap.set(elXp, { scaleX: 0 });
  if (sceneFromHash() === 'title') {
    if (!reduced) enter.title();
    spawnCoins();
  } else {
    swap(sceneFromHash());
  }
})();
