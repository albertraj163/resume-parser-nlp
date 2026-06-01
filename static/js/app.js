(() => {
  const resumeText = document.getElementById("resumeText");
  const fileInput = document.getElementById("fileInput");
  const uploadZone = document.getElementById("uploadZone");
  const parseBtn = document.getElementById("parseBtn");
  const clearBtn = document.getElementById("clearBtn");
  const loadSample = document.getElementById("loadSample");
  const statusPill = document.getElementById("statusPill");
  const emptyState = document.getElementById("emptyState");
  const results = document.getElementById("results");
  const errorState = document.getElementById("errorState");
  const errorMessage = document.getElementById("errorMessage");
  const serverUrl = document.getElementById("serverUrl");

  serverUrl.textContent = window.location.origin;

  function setLoading(loading) {
    parseBtn.disabled = loading;
    parseBtn.querySelector(".btn__label").hidden = loading;
    parseBtn.querySelector(".btn__spinner").hidden = !loading;
    statusPill.textContent = loading ? "Parsing…" : "Ready";
    statusPill.className = "status-pill" + (loading ? " loading" : "");
  }

  function showError(msg) {
    emptyState.hidden = true;
    results.hidden = true;
    errorState.hidden = false;
    errorMessage.textContent = msg;
    statusPill.textContent = "Error";
    statusPill.className = "status-pill error";
  }

  function showResults(data) {
    emptyState.hidden = true;
    errorState.hidden = true;
    results.hidden = false;
    statusPill.textContent = "Parsed";
    statusPill.className = "status-pill success";

    document.getElementById("resName").textContent = data.name || "—";
    document.getElementById("resEmail").textContent = data.email || "—";
    document.getElementById("resPhone").textContent = data.phone || "—";

    renderTags("resSkills", data.skills);
    renderList("resExperience", data.experience);
    renderList("resEducation", data.education);
    renderEntities("resEntities", data.entities);
    document.getElementById("resRaw").textContent = data.raw_text || "";
  }

  function renderTags(id, items) {
    const el = document.getElementById(id);
    el.innerHTML = "";
    if (!items || !items.length) {
      el.innerHTML = '<span class="tag tag--empty">None detected</span>';
      return;
    }
    items.forEach((item) => {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = item;
      el.appendChild(span);
    });
  }

  function renderList(id, items) {
    const el = document.getElementById(id);
    el.innerHTML = "";
    if (!items || !items.length) {
      const li = document.createElement("li");
      li.textContent = "None detected";
      li.style.color = "var(--text-muted)";
      el.appendChild(li);
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      el.appendChild(li);
    });
  }

  function renderEntities(id, entities) {
    const el = document.getElementById(id);
    el.innerHTML = "";
    if (!entities || !entities.length) {
      el.innerHTML = '<span class="tag tag--empty">No entities found</span>';
      return;
    }
    entities.forEach(({ text, label }) => {
      const span = document.createElement("span");
      span.className = "entity";
      span.innerHTML = `${text}<span class="entity__label">${label}</span>`;
      el.appendChild(span);
    });
  }

  async function parseResume() {
    const text = resumeText.value.trim();
    const file = fileInput.files[0];

    if (!text && !file) {
      showError("Please paste resume text or upload a file.");
      return;
    }

    setLoading(true);
    errorState.hidden = true;

    const formData = new FormData();
    if (text) formData.append("text", text);
    if (file) formData.append("file", file);

    try {
      const res = await fetch("/api/parse", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Parse request failed.");
      showResults(data);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadSampleResume() {
    setLoading(true);
    try {
      const res = await fetch("/api/sample");
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Could not load sample.");
      resumeText.value = data.text;
      fileInput.value = "";
      showResults(data.result);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }

  uploadZone.addEventListener("click", () => fileInput.click());

  uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadZone.classList.add("dragover");
  });

  uploadZone.addEventListener("dragleave", () => {
    uploadZone.classList.remove("dragover");
  });

  uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadZone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file) {
      fileInput.files = e.dataTransfer.files;
      resumeText.value = "";
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) resumeText.value = "";
  });

  parseBtn.addEventListener("click", parseResume);
  loadSample.addEventListener("click", loadSampleResume);

  clearBtn.addEventListener("click", () => {
    resumeText.value = "";
    fileInput.value = "";
    emptyState.hidden = false;
    results.hidden = true;
    errorState.hidden = true;
    statusPill.textContent = "Ready";
    statusPill.className = "status-pill";
  });
})();
