const state = {
  sessionId: null,
  mode: null,
  index: 0,
  total: 0,
  answers: {},
  timerId: null,
  endsAt: null,
};

const screens = {
  home: document.getElementById("screen-home"),
  exam: document.getElementById("screen-exam"),
  results: document.getElementById("screen-results"),
};

function showScreen(name) {
  Object.values(screens).forEach((el) => el.classList.remove("active"));
  screens[name].classList.add("active");
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function stopTimer() {
  if (state.timerId) {
    clearInterval(state.timerId);
    state.timerId = null;
  }
  document.getElementById("timer").classList.add("hidden");
}

function startTimer(minutes, startedAt) {
  stopTimer();
  const timerEl = document.getElementById("timer");
  timerEl.classList.remove("hidden");
  const durationMs = minutes * 60 * 1000;
  state.endsAt = startedAt * 1000 + durationMs;

  const tick = () => {
    const remaining = Math.max(0, Math.floor((state.endsAt - Date.now()) / 1000));
    timerEl.textContent = `Time remaining: ${formatTime(remaining)}`;
    if (remaining === 0) {
      stopTimer();
      finishSession();
    }
  };
  tick();
  state.timerId = setInterval(tick, 1000);
}

async function loadMeta() {
  const res = await fetch("/api/meta");
  const meta = await res.json();
  const stats = document.getElementById("meta-stats");
  stats.innerHTML = `
    <div><dt>Question bank</dt><dd>${meta.question_bank_size} questions</dd></div>
    <div><dt>Mock exam length</dt><dd>${meta.mock_question_count} questions / ${meta.mock_duration_minutes} min</dd></div>
    <div><dt>Pass threshold</dt><dd>${meta.pass_score_percent}% (aligned to ~700/1000)</dd></div>
  `;
  const select = document.getElementById("domain-select");
  select.innerHTML = meta.domains
    .map((d) => `<option value="${d.id}">${d.label}</option>`)
    .join("");
}

async function startSession(mode, domain) {
  const res = await fetch("/api/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode, domain: domain || null }),
  });
  if (!res.ok) {
    alert("Could not start session");
    return;
  }
  const data = await res.json();
  state.sessionId = data.session_id;
  state.mode = data.mode;
  state.index = 0;
  state.total = data.total_questions;
  state.answers = {};
  showScreen("exam");
  if (data.duration_minutes) {
    const qRes = await fetch(`/api/sessions/${state.sessionId}/questions/0`);
    const qData = await qRes.json();
    startTimer(data.duration_minutes, qData.started_at);
  } else {
    stopTimer();
  }
  await loadQuestion(0);
}

function renderNavigator() {
  const map = document.getElementById("question-map");
  map.innerHTML = "";
  for (let i = 0; i < state.total; i += 1) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "q-btn";
    btn.textContent = String(i + 1);
    if (i === state.index) btn.classList.add("current");
    const ans = state.answers[i];
    if (ans) {
      btn.classList.add("answered");
      btn.classList.add(ans.correct ? "correct" : "incorrect");
    }
    btn.addEventListener("click", () => loadQuestion(i));
    map.appendChild(btn);
  }
  document.getElementById("progress-label").textContent = `${state.index + 1}/${state.total}`;
}

function getSelectedIndices(form, multi) {
  if (multi) {
    return [...form.querySelectorAll('input[name="opt"]:checked')].map((el) =>
      Number(el.value)
    );
  }
  const checked = form.querySelector('input[name="opt"]:checked');
  return checked ? [Number(checked.value)] : [];
}

function renderFeedback(feedback, isCorrect) {
  const box = document.getElementById("feedback");
  box.classList.remove("hidden", "correct", "incorrect");
  box.classList.add(isCorrect ? "correct" : "incorrect");

  if (isCorrect) {
    box.innerHTML = `
      <strong>Correct</strong>
      <p>${feedback.explanation}</p>
      <p><a href="${feedback.study_url}" target="_blank" rel="noopener">Study on Microsoft Learn</a></p>
    `;
  } else {
    box.innerHTML = `
      <strong>Incorrect</strong>
      <p>${feedback.why_wrong}</p>
      <p>${feedback.explanation}</p>
      <p><strong>Correct:</strong> ${feedback.correct_options.join("; ")}</p>
      <p><a href="${feedback.study_url}" target="_blank" rel="noopener">Study on Microsoft Learn</a></p>
    `;
  }
}

async function loadQuestion(index) {
  state.index = index;
  const res = await fetch(`/api/sessions/${state.sessionId}/questions/${index}`);
  if (!res.ok) {
    alert("Could not load question");
    return;
  }
  const data = await res.json();
  const q = data.question;
  document.getElementById("q-domain").textContent = q.domain_label;
  document.getElementById("q-type").textContent = q.is_multi_select
    ? "Select all that apply"
    : "Single answer";
  document.getElementById("q-text").textContent = q.question_text;

  const form = document.getElementById("options-form");
  form.innerHTML = q.options
    .map(
      (opt, i) => `
      <label class="option">
        <input type="${q.is_multi_select ? "checkbox" : "radio"}" name="opt" value="${i}" />
        <span>${opt}</span>
      </label>`
    )
    .join("");

  const feedback = document.getElementById("feedback");
  feedback.classList.add("hidden");
  feedback.innerHTML = "";

  const submitBtn = document.getElementById("btn-submit");
  if (data.answered && data.prior_submission) {
    state.answers[index] = {
      selected: data.prior_submission.selected,
      correct: data.prior_submission.correct,
    };
    form.querySelectorAll("input").forEach((input) => {
      input.disabled = true;
      if (data.prior_submission.selected.includes(Number(input.value))) {
        input.checked = true;
      }
    });
    submitBtn.disabled = true;
    if (data.feedback) {
      renderFeedback(data.feedback, data.is_correct);
    }
  } else {
    submitBtn.disabled = false;
  }

  renderNavigator();
}

document.getElementById("options-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const multi = document.getElementById("q-type").textContent.includes("all");
  const selected = getSelectedIndices(form, multi);
  if (!selected.length) {
    alert("Select at least one answer.");
    return;
  }

  const res = await fetch(
    `/api/sessions/${state.sessionId}/questions/${state.index}/submit`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selected }),
    }
  );
  if (!res.ok) {
    alert("Submit failed");
    return;
  }
  const data = await res.json();
  state.answers[state.index] = {
    selected,
    correct: data.is_correct,
  };
  form.querySelectorAll("input").forEach((input) => {
    input.disabled = true;
  });
  document.getElementById("btn-submit").disabled = true;
  renderFeedback(data.feedback, data.is_correct);
  renderNavigator();
});

document.getElementById("btn-prev").addEventListener("click", () => {
  if (state.index > 0) loadQuestion(state.index - 1);
});

document.getElementById("btn-next").addEventListener("click", () => {
  if (state.index < state.total - 1) loadQuestion(state.index + 1);
});

async function finishSession() {
  stopTimer();
  const res = await fetch(`/api/sessions/${state.sessionId}/complete`, { method: "POST" });
  if (!res.ok) {
    alert("Could not complete session");
    return;
  }
  const data = await res.json();
  showScreen("results");
  document.getElementById("results-summary").textContent = `You scored ${data.score_percent}% (${data.correct_count}/${data.total} correct). ${data.answered} questions answered.`;
  const badge = document.getElementById("results-badge");
  badge.textContent = data.passed ? "Pass" : "Below pass threshold";
  badge.className = `badge ${data.passed ? "pass" : "fail"}`;

  const list = document.getElementById("wrong-list");
  if (!data.wrong_questions.length) {
    list.innerHTML = "<p>No missed questions — great job.</p>";
  } else {
    list.innerHTML = data.wrong_questions
      .map(
        (w) => `
      <details>
        <summary>Question ${w.index + 1}: ${w.question_text.slice(0, 90)}…</summary>
        <p>${w.why_wrong}</p>
        <p>${w.explanation}</p>
        <p><strong>Correct:</strong> ${w.correct_options.join("; ")}</p>
        <p><a href="${w.study_url}" target="_blank" rel="noopener">Study on Microsoft Learn</a></p>
      </details>`
      )
      .join("");
  }
}

document.getElementById("btn-mock").addEventListener("click", () => startSession("mock"));
document.getElementById("btn-practice").addEventListener("click", () => {
  const domain = document.getElementById("domain-select").value;
  startSession("practice", domain);
});
document.getElementById("btn-finish").addEventListener("click", finishSession);
document.getElementById("btn-home").addEventListener("click", () => {
  showScreen("home");
});

loadMeta();
