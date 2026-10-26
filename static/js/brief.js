// 90-Second Brief — step-by-step questionnaire with branching support.
// Questions come from core/brief.py via the #brief-data JSON block,
// so the backend validation and this wizard share one source of truth.
document.addEventListener("DOMContentLoaded", function () {
  var panel = document.querySelector("[data-brief-wizard]");
  if (!panel) return;

  var dataEl = panel.querySelector("#brief-data");
  var data;
  try {
    data = JSON.parse(dataEl.textContent);
  } catch (err) {
    return;
  }

  // Calculate total steps: fork step + track-specific questions + email step
  var TOTAL = 8;
  if (data.tracks) {
    var trackKeys = Object.keys(data.tracks);
    if (trackKeys.length > 0) {
      TOTAL = 1 + data.tracks[trackKeys[0]].length + 1;
    }
  } else if (data.questions) {
    TOTAL = data.questions.length + 1;
  }

  var progressFill = panel.querySelector(".brief-progress-fill");
  var countEl = panel.querySelector(".brief-count");
  var questionEl = panel.querySelector(".brief-question");
  var multiHint = panel.querySelector(".brief-multi-hint");
  var optionsEl = panel.querySelector(".brief-options");
  var emailBox = panel.querySelector(".brief-email");
  var emailInput = panel.querySelector("#brief-email");
  var emailLabel = panel.querySelector(".brief-email-label");
  var errorEl = panel.querySelector(".brief-error");
  var backBtn = panel.querySelector(".brief-back");
  var nextBtn = panel.querySelector(".brief-next");
  var successBox = panel.querySelector(".brief-success");
  var csrfInput = panel.querySelector("input[name=csrfmiddlewaretoken]");

  var step = 0;
  var answers = {};
  var selected = null;
  var submitting = false;

  // Returns active question list based on currently chosen track
  function getActiveQuestions() {
    if (!data.fork_question) {
      return data.questions || [];
    }
    var forkQ = data.fork_question;
    var chosenTrack = answers[forkQ.id];
    var trackQuestions = (chosenTrack && data.tracks && data.tracks[chosenTrack]) || [];
    return [forkQ].concat(trackQuestions);
  }

  // Replays the rise animation so each step reads as a deliberate change.
  function replayIn(el) {
    el.classList.remove("step-in");
    void el.offsetWidth;
    el.classList.add("step-in");
  }

  // ── Rendering ─────────────────────────────────────────────────────────
  function render() {
    errorEl.textContent = "";
    panel.querySelector(".brief-progress").hidden = false;
    countEl.hidden = false;
    successBox.hidden = true;

    var activeQuestions = getActiveQuestions();
    var isEmailStep = (step >= activeQuestions.length && activeQuestions.length > 1) || (step === TOTAL - 1);
    var q = activeQuestions[step];

    if (isEmailStep) {
      questionEl.textContent = "";
      multiHint.hidden = true;
      optionsEl.innerHTML = "";
      optionsEl.hidden = true;
      emailBox.hidden = false;
      if (emailLabel.textContent === "") emailLabel.textContent = data.email_step;
      nextBtn.hidden = false;
      nextBtn.textContent = data.cta;
      nextBtn.disabled = false;
      progressFill.style.width = "100%";
      countEl.textContent = "FINAL STEP / " + TOTAL;
      backBtn.hidden = false;
      emailInput.focus();
      return;
    }

    emailBox.hidden = true;
    optionsEl.hidden = false;
    questionEl.hidden = false;
    questionEl.textContent = q ? q.question : "";
    countEl.textContent = "QUESTION " + (step + 1) + " / " + TOTAL;
    progressFill.style.width = ((step) / TOTAL) * 100 + "%";
    backBtn.hidden = step === 0;

    // Multi-select steps use the Continue button; single-select advances on choice.
    var isMulti = !!(q && q.multi);
    multiHint.hidden = !isMulti;
    optionsEl.setAttribute("role", isMulti ? "group" : "radiogroup");
    nextBtn.hidden = !isMulti;
    if (isMulti) {
      nextBtn.textContent = "Continue →";
      nextBtn.disabled = !(selected && selected.length);
    }

    optionsEl.innerHTML = "";
    if (!q || !q.options) return;

    var focusFirst = true;
    q.options.forEach(function (option) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "brief-option";
      btn.textContent = option;
      var isSel = isMulti
        ? !!(selected && selected.indexOf(option) !== -1)
        : selected === option;
      if (isMulti) {
        btn.setAttribute("role", "checkbox");
        btn.setAttribute("aria-pressed", isSel ? "true" : "false");
      } else {
        btn.setAttribute("role", "radio");
        btn.setAttribute("aria-checked", isSel ? "true" : "false");
      }
      if (isSel) btn.classList.add("selected");
      if (focusFirst && isSel) { focusFirst = false; setTimeout(function () { btn.focus(); }, 0); }
      btn.addEventListener("click", function () {
        isMulti ? toggleOption(option) : selectOption(option);
      });
      optionsEl.appendChild(btn);
    });
  }

  function restoreSelection() {
    var activeQuestions = getActiveQuestions();
    if (step < activeQuestions.length) {
      var q = activeQuestions[step];
      if (q && q.multi) {
        return (answers[q.id] || []).slice();
      }
      return q ? answers[q.id] || null : null;
    }
    return null;
  }

  function advance() {
    step += 1;
    selected = restoreSelection();
    render();
    replayIn(panel.querySelector(".brief-ask"));
    if (!optionsEl.hidden) replayIn(optionsEl);
  }

  function selectOption(option) {
    var activeQuestions = getActiveQuestions();
    var currentQ = activeQuestions[step];

    // If changing the fork question on step 0, clear downstream answers
    if (step === 0 && data.fork_question && answers[data.fork_question.id] !== option) {
      answers = {};
    }

    selected = option;
    answers[currentQ.id] = option;

    // Brief pause so the choice is visible before moving on.
    Array.prototype.forEach.call(optionsEl.children, function (btn) {
      btn.disabled = true;
      if (btn.textContent === option) btn.classList.add("chosen");
    });
    setTimeout(advance, 320);
  }

  function toggleOption(option) {
    var activeQuestions = getActiveQuestions();
    var currentQ = activeQuestions[step];
    var picked = (selected || []).slice();
    var at = picked.indexOf(option);
    if (at === -1) picked.push(option);
    else picked.splice(at, 1);
    selected = picked;
    answers[currentQ.id] = picked;
    Array.prototype.forEach.call(optionsEl.children, function (btn) {
      var on = picked.indexOf(btn.textContent) !== -1;
      btn.classList.toggle("selected", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    nextBtn.disabled = !picked.length;
  }

  backBtn.addEventListener("click", function () {
    if (step === 0) return;
    step -= 1;
    selected = restoreSelection();
    render();
    replayIn(panel.querySelector(".brief-ask"));
    if (!optionsEl.hidden) replayIn(optionsEl);
  });

  // Enter on the email input submits.
  emailInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      submitBrief();
    }
  });

  // ── Navigation / submission ───────────────────────────────────────────
  nextBtn.addEventListener("click", function () {
    var activeQuestions = getActiveQuestions();
    if (step < activeQuestions.length) {
      if (selected && selected.length) advance();
      return;
    }
    submitBrief();
  });

  function submitBrief() {
    if (submitting) return;
    var email = emailInput.value.trim();
    if (!email || email.indexOf("@") < 1) {
      errorEl.textContent = "Please enter a valid email address.";
      emailInput.focus();
      return;
    }
    errorEl.textContent = "";
    submitting = true;
    nextBtn.disabled = true;
    nextBtn.textContent = "sending…";
    progressFill.style.width = "100%";

    fetch(panel.dataset.submitUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfInput ? csrfInput.value : "",
      },
      body: JSON.stringify({ email: email, answers: answers, honeypot: "" }),
    })
      .then(function (res) {
        return res.json().catch(function () {
          throw new Error("Something went wrong — please try again.");
        });
      })
      .then(function (result) {
        if (!result.ok) {
          throw new Error(result.error || "Something went wrong — please try again.");
        }
        showSuccess();
      })
      .catch(function (err) {
        errorEl.textContent = err.message;
        nextBtn.disabled = false;
        nextBtn.textContent = data.cta;
        submitting = false;
      });
  }

  function showSuccess() {
    submitting = false;
    panel.querySelector(".brief-progress").hidden = true;
    countEl.hidden = true;
    questionEl.hidden = true;
    multiHint.hidden = true;
    optionsEl.hidden = true;
    emailBox.hidden = true;
    panel.querySelector(".brief-nav").hidden = true;
    successBox.hidden = false;

    var successSub = panel.querySelector(".brief-success-sub");
    if (successSub && data.fork_question && answers[data.fork_question.id] === data.fork_question.options[1]) {
      successSub.textContent = "Your answers are on their way. I’ll review your project details and reply to your email with initial thoughts and next steps.";
    }

    replayIn(successBox);
  }

  // Initial render of step 1.
  render();
});
