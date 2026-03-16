const state = {
  profile: null,
  session: null,
};

const statusBanner = document.querySelector("#status-banner");
const profileContent = document.querySelector("#profile-content");
const sessionMeta = document.querySelector("#session-meta");
const timelineEl = document.querySelector("#timeline");
const insightEl = document.querySelector("#insight");
const confidenceInput = document.querySelector("#thought-confidence");
const confidenceValue = document.querySelector("#confidence-value");

confidenceInput.addEventListener("input", () => {
  confidenceValue.textContent = Number(confidenceInput.value).toFixed(2);
});

function setStatus(message) {
  statusBanner.textContent = message;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = await response.json();
      detail = payload.detail ?? JSON.stringify(payload);
    } catch {
      detail = await response.text();
    }
    throw new Error(detail || "Request failed");
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function parseTags(rawValue) {
  return rawValue
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatDate(value) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function renderProfile() {
  if (!state.profile) {
    profileContent.innerHTML = '<div class="empty-state">Profile unavailable.</div>';
    return;
  }

  const projects = state.profile.projects
    .map(
      (project) => `
        <article class="section-block">
          <h3>${project.name}</h3>
          <p class="muted">${project.description}</p>
          <div class="chip-list">${project.tags.map((tag) => `<span class="chip">${tag}</span>`).join("")}</div>
        </article>
      `,
    )
    .join("");

  const interests = state.profile.interests.map((interest) => `<span class="chip">${interest}</span>`).join("");
  const questions = state.profile.questions.length
    ? state.profile.questions.map((question) => `<span class="chip">${question}</span>`).join("")
    : '<p class="muted">No saved research questions yet.</p>';

  profileContent.innerHTML = `
    <section class="section-block">
      <h3>Projects</h3>
      <div class="project-list">${projects}</div>
    </section>
    <section class="section-block">
      <h3>Interests</h3>
      <div class="chip-list">${interests || '<span class="muted">No interests yet.</span>'}</div>
    </section>
    <section class="section-block">
      <h3>Questions</h3>
      <div class="chip-list">${questions}</div>
    </section>
  `;
}

function mergeTimeline(session) {
  const listeningEvents = session.listening_events.map((event) => ({
    kind: "Listening",
    title: event.title,
    creator: event.creator,
    occurredAt: event.occurred_at,
    transcript: event.transcript_chunk,
    topics: event.topics,
    meta: [event.platform, event.duration_seconds ? `${event.duration_seconds}s` : null].filter(Boolean).join(" • "),
    url: event.content_url,
  }));

  const thoughtEvents = session.thought_events.map((event, index) => ({
    kind: `Thought ${index + 1}`,
    title: "Voice reflection",
    creator: `confidence ${Number(event.confidence).toFixed(2)}`,
    occurredAt: event.occurred_at,
    transcript: event.transcript_chunk,
    topics: [],
    meta: "mic note",
    url: null,
  }));

  return [...listeningEvents, ...thoughtEvents].sort(
    (left, right) => new Date(left.occurredAt).getTime() - new Date(right.occurredAt).getTime(),
  );
}

function renderSession() {
  if (!state.session) {
    sessionMeta.textContent = "No session yet";
    timelineEl.className = "timeline empty-state";
    timelineEl.textContent = "Start a blank session or load the commute demo to see events here.";
    return;
  }

  sessionMeta.textContent = `${state.session.id.slice(0, 8)} • ${state.session.listening_events.length} listening • ${state.session.thought_events.length} thoughts`;

  const merged = mergeTimeline(state.session);
  if (!merged.length) {
    timelineEl.className = "timeline empty-state";
    timelineEl.textContent = "This session is empty. Add a listening chunk or a thought above.";
    return;
  }

  timelineEl.className = "timeline";
  timelineEl.innerHTML = merged
    .map(
      (entry) => `
        <article class="timeline-card">
          <header>
            <div>
              <p class="timeline-kind">${entry.kind}</p>
              <h3>${entry.title}</h3>
            </div>
            <div class="timeline-meta">${formatDate(entry.occurredAt)}</div>
          </header>
          <p class="muted">${entry.creator || ""} ${entry.meta ? `• ${entry.meta}` : ""}</p>
          <p>${entry.transcript}</p>
          ${entry.url ? `<p><a href="${entry.url}" target="_blank" rel="noreferrer">Open source</a></p>` : ""}
          ${entry.topics.length ? `<div class="badge-row">${entry.topics.map((topic) => `<span class="badge">${topic}</span>`).join("")}</div>` : ""}
        </article>
      `,
    )
    .join("");
}

function renderInsight() {
  const insight = state.session?.latest_insight;
  if (!insight) {
    insightEl.className = "insight empty-state";
    insightEl.textContent =
      "Analyze a session to generate summary, verification status, suggested links, and project connections.";
    return;
  }

  insightEl.className = "insight";
  insightEl.innerHTML = `
    <article class="insight-card">
      <p class="eyebrow">Summary</p>
      <p>${insight.summary}</p>
    </article>
    <article class="insight-card">
      <p class="eyebrow">Explanation</p>
      <p>${insight.explanation}</p>
    </article>
    <article class="insight-card">
      <p class="eyebrow">Feedback</p>
      <p>${insight.feedback}</p>
    </article>
    <article class="insight-card">
      <p class="eyebrow">Connected projects</p>
      ${
        insight.connected_projects.length
          ? `<div class="badge-row">${insight.connected_projects.map((project) => `<span class="badge">${project}</span>`).join("")}</div>`
          : '<p class="muted">No project links found yet.</p>'
      }
    </article>
    <article class="insight-card">
      <p class="eyebrow">Verification queue</p>
      <div class="verification-list">
        ${
          insight.verification.length
            ? insight.verification
                .map(
                  (item) => `
                    <div class="verification-item">
                      <div class="badge-row">
                        <span class="badge status-badge status-${item.status}">${item.status.replaceAll("_", " ")}</span>
                      </div>
                      <p>${item.claim}</p>
                      <p class="muted">${item.note}</p>
                      ${item.source_url ? `<a href="${item.source_url}" target="_blank" rel="noreferrer">Open linked source</a>` : ""}
                    </div>
                  `,
                )
                .join("")
            : '<p class="muted">No claims detected yet.</p>'
        }
      </div>
    </article>
    <article class="insight-card">
      <p class="eyebrow">Study links</p>
      <div class="link-grid">
        ${
          insight.suggested_links.length
            ? insight.suggested_links
                .map(
                  (link) => `
                    <div class="link-card">
                      <h3>${link.topic}</h3>
                      <p class="muted">${link.reason}</p>
                      <a href="${link.url}" target="_blank" rel="noreferrer">Open topic source</a>
                    </div>
                  `,
                )
                .join("")
            : '<p class="muted">No follow-up links yet.</p>'
        }
      </div>
    </article>
  `;
}

async function loadProfile() {
  state.profile = await api("/profile");
  renderProfile();
}

function renderAll() {
  renderProfile();
  renderSession();
  renderInsight();
}

async function refreshSession(sessionId) {
  state.session = await api(`/sessions/${sessionId}`);
  renderAll();
}

async function createSession() {
  const payload = await api("/sessions", { method: "POST" });
  await refreshSession(payload.session_id);
  setStatus(`Created session ${payload.session_id.slice(0, 8)}.`);
}

async function analyzeSession(onlineVerification) {
  if (!state.session) {
    setStatus("Create a session first.");
    return;
  }

  state.session.latest_insight = await api(
    `/sessions/${state.session.id}/analyze?online_verification=${onlineVerification}`,
    { method: "POST" },
  );
  renderInsight();
  setStatus(onlineVerification ? "Analysis updated with source placeholders." : "Offline analysis updated.");
}

async function bootstrapDemo() {
  state.session = await api("/demo/bootstrap", { method: "POST" });
  renderAll();
  setStatus("Commute demo loaded with Spotify, YouTube, and thought events.");
}

async function handleListeningSubmit(event) {
  event.preventDefault();
  if (!state.session) {
    setStatus("Create a session first.");
    return;
  }

  const form = new FormData(event.currentTarget);
  const payload = {
    platform: form.get("platform"),
    title: form.get("title"),
    creator: form.get("creator") || null,
    content_url: form.get("content_url") || null,
    transcript_chunk: form.get("transcript_chunk"),
    topics: parseTags(form.get("topics") || ""),
  };

  state.session = await api(`/sessions/${state.session.id}/events/listening`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  event.currentTarget.reset();
  renderAll();
  setStatus("Listening event appended.");
}

async function handleThoughtSubmit(event) {
  event.preventDefault();
  if (!state.session) {
    setStatus("Create a session first.");
    return;
  }

  const form = new FormData(event.currentTarget);
  const payload = {
    transcript_chunk: form.get("transcript_chunk"),
    confidence: Number(form.get("confidence")),
  };

  state.session = await api(`/sessions/${state.session.id}/events/thought`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  event.currentTarget.reset();
  confidenceInput.value = "0.75";
  confidenceValue.textContent = "0.75";
  renderAll();
  setStatus("Thought event appended.");
}

async function appendProfileList(field, rawValue) {
  if (!state.profile) {
    return;
  }
  const nextValues = [...state.profile[field], rawValue];
  state.profile = await api("/profile", {
    method: "PATCH",
    body: JSON.stringify({ [field]: nextValues }),
  });
  renderProfile();
}

async function handleQuestionSubmit(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const value = String(form.get("question")).trim();
  if (!value) {
    return;
  }
  await appendProfileList("questions", value);
  event.currentTarget.reset();
  setStatus("Research question saved.");
}

async function handleInterestSubmit(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const value = String(form.get("interest")).trim();
  if (!value) {
    return;
  }
  await appendProfileList("interests", value);
  event.currentTarget.reset();
  setStatus("Interest saved.");
}

async function handleProjectSubmit(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {
    id: form.get("project_id"),
    name: form.get("project_name"),
    description: form.get("project_description"),
    tags: parseTags(form.get("project_tags") || ""),
  };

  await api("/profile/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  await loadProfile();
  event.currentTarget.reset();
  setStatus("Project added to profile.");
}

function bindEvents() {
  document.querySelector("#bootstrap-demo").addEventListener("click", () => {
    bootstrapDemo().catch(handleError);
  });
  document.querySelector("#create-session").addEventListener("click", () => {
    createSession().catch(handleError);
  });
  document.querySelector("#analyze-offline").addEventListener("click", () => {
    analyzeSession(false).catch(handleError);
  });
  document.querySelector("#analyze-online").addEventListener("click", () => {
    analyzeSession(true).catch(handleError);
  });
  document.querySelector("#listening-form").addEventListener("submit", (event) => {
    handleListeningSubmit(event).catch(handleError);
  });
  document.querySelector("#thought-form").addEventListener("submit", (event) => {
    handleThoughtSubmit(event).catch(handleError);
  });
  document.querySelector("#question-form").addEventListener("submit", (event) => {
    handleQuestionSubmit(event).catch(handleError);
  });
  document.querySelector("#interest-form").addEventListener("submit", (event) => {
    handleInterestSubmit(event).catch(handleError);
  });
  document.querySelector("#project-form").addEventListener("submit", (event) => {
    handleProjectSubmit(event).catch(handleError);
  });
}

function handleError(error) {
  setStatus(`Error: ${error.message}`);
}

async function init() {
  bindEvents();
  await loadProfile();
  renderAll();
  setStatus("Profile loaded. Create a session or load the commute demo.");
}

init().catch(handleError);
