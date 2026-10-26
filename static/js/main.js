document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", function () {
  // ── Scroll-reveal ─────────────────────────────────────────────────────────
  var reveals = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("visible"); });
  } else {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    reveals.forEach(function (el) { observer.observe(el); });
  }

  var formFeedback = document.querySelector('.form-errors, #message-status');
  if (formFeedback) {
    window.addEventListener("pageshow", function () {
      requestAnimationFrame(function () { formFeedback.focus(); });
    });
  }

  // ── Contact form submit guard ─────────────────────────────────────────────
  var contactForm = document.querySelector(".contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", function () {
      var button = contactForm.querySelector("button[type=submit]");
      if (button && !button.disabled) {
        var original = button.textContent;
        button.disabled = true;
        button.textContent = "sending…";
        // Restore if submission didn't navigate (e.g. validation errors shown)
        setTimeout(function () {
          button.disabled = false;
          button.textContent = original;
        }, 8000);
      }
    });
  }

  // ── Lightbox ──────────────────────────────────────────────────────────────
  var lb      = document.getElementById("lightbox");
  var lbImg   = lb && lb.querySelector(".lb-img");
  var lbCap   = lb && lb.querySelector(".lb-caption");
  var lbClose = lb && lb.querySelector(".lb-close");
  var lbTrigger = null;

  function openLightbox(src, caption) {
    if (!lb) return;
    lbTrigger = document.activeElement;
    lbImg.src = src;
    lbImg.alt = caption || "";
    lbCap.textContent = caption || "";
    lb.hidden = false;
    document.body.classList.add("lightbox-open");
    lbClose.focus();
  }

  function closeLightbox() {
    if (!lb) return;
    lb.hidden = true;
    lbImg.src = "";
    document.body.classList.remove("lightbox-open");
    if (lbTrigger && document.contains(lbTrigger)) {
      lbTrigger.focus();
    }
    lbTrigger = null;
  }

  // Delegate clicks on any image with data-lb-src
  document.addEventListener("click", function (e) {
    var img = e.target.closest("[data-lb-src]");
    if (img) {
      e.preventDefault();
      openLightbox(img.dataset.lbSrc, img.dataset.lbCaption);
      return;
    }
    // Close when clicking the backdrop (not the image)
    if (lb && !lb.hidden && e.target === lb) {
      closeLightbox();
    }
  });

  if (lbClose) {
    lbClose.addEventListener("click", closeLightbox);
  }

  // Keyboard: Escape closes, Tab is trapped inside the dialog
  document.addEventListener("keydown", function (e) {
    if (!lb || lb.hidden) return;
    if (e.key === "Escape") {
      closeLightbox();
    } else if (e.key === "Tab" && lbClose) {
      // Only the close button is focusable in the dialog — keep it that way
      e.preventDefault();
      lbClose.focus();
    }
  });
});
