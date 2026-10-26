/* Inner-page motion — GSAP entrances, pixel-wipe page transitions, brief option pops. */
(function () {
  'use strict';
  if (!window.gsap || !document.body.classList.contains('pg')) return;

  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced) gsap.defaults({ duration: 0 });

  // ── Pixel wipe overlay ───────────────────────────────────────────────────
  var wipe = document.createElement('div');
  wipe.className = 'pg-wipe';
  wipe.setAttribute('aria-hidden', 'true');
  for (var i = 0; i < 96; i++) wipe.appendChild(document.createElement('i'));
  document.body.appendChild(wipe);
  var cells = $$('i', wipe);
  var each = { amount: 0.1, from: 'random' };

  function wipeOut() {
    gsap.set(cells, { scale: 1.02 });
    gsap.to(cells, { scale: 0, duration: 0.15, stagger: each, ease: 'steps(3)' });
  }

  function leave(url) {
    if (reduced) { location.href = url; return; }
    gsap.to(cells, { scale: 1.02, duration: 0.15, stagger: each, ease: 'steps(3)', onComplete: function () { location.href = url; } });
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (a.target === '_blank' || a.hasAttribute('download')) return;
    if (a.origin !== location.origin) return;
    if (a.pathname === location.pathname && a.search === location.search) return;
    if (a.hash) return;
    e.preventDefault();
    leave(a.href);
  });
  // Back/forward cache: never leave the screen covered.
  window.addEventListener('pageshow', function (e) { if (e.persisted) gsap.set(cells, { scale: 0 }); });

  // ── Entrances ────────────────────────────────────────────────────────────
  if (!reduced) wipeOut();
  else { gsap.set(cells, { scale: 0 }); return; }

  gsap.from('.site-header', { y: -60, opacity: 0, duration: 0.5, ease: 'steps(5)' });
  gsap.from('.page-head > *, .journal-detail > .eyebrow, .journal-detail > h1', {
    y: 36, opacity: 0, duration: 0.5, stagger: 0.09, delay: 0.25, ease: 'back.out(1.6)'
  });

  // Scroll-in for repeated blocks.
  var targets = $$('.project-card, .entries li, .case-study-facts article, .case-study-section, .project-cover, .project-gallery figure, .contact-banner, .journal-detail .body > *');
  if ('IntersectionObserver' in window && targets.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        gsap.from(en.target, { y: 50, opacity: 0, scale: 0.97, duration: 0.5, ease: 'back.out(1.4)', clearProps: 'transform,opacity' });
      });
    }, { threshold: 0.12 });
    targets.forEach(function (t) { io.observe(t); });
  }

  // ── Brief wizard: options pop in every step ──────────────────────────────
  var opts = document.querySelector('.brief-options');
  if (opts && 'MutationObserver' in window) {
    new MutationObserver(function () {
      gsap.from(opts.children, { x: -40, opacity: 0, duration: 0.35, stagger: 0.06, ease: 'back.out(1.8)', clearProps: 'transform,opacity' });
      var q = document.querySelector('.brief-question');
      if (q) gsap.from(q, { y: 20, opacity: 0, duration: 0.3, clearProps: 'transform,opacity' });
    }).observe(opts, { childList: true });
  }

  // ── Error screens ────────────────────────────────────────────────────────
  var big = document.getElementById('pg-big');
  if (big && !reduced) {
    gsap.from(big, { scale: 0.3, rotation: -8, opacity: 0, duration: 0.7, delay: 0.3, ease: 'back.out(2)' });
    gsap.to(big, { x: '+=6', duration: 0.08, repeat: -1, repeatDelay: 2.4, yoyo: true, ease: 'steps(1)' });
  }
  var sprite = document.getElementById('pg-sprite');
  if (sprite && !reduced) gsap.to(sprite, { y: -16, duration: 1.1, yoyo: true, repeat: -1, ease: 'sine.inOut' });
  var art = document.querySelector('.pg-denied-art');
  if (art && !reduced) gsap.from(art, { rotation: -12, scale: 0.5, opacity: 0, duration: 0.6, ease: 'back.out(2)' });
})();
