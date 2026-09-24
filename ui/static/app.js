const els = {
  input: document.getElementById("navigationInput"),
  run: document.getElementById("runButton"),
  clear: document.getElementById("clearButton"),
  compareModel: document.getElementById("compareModel"),
  adapterSelect: document.getElementById("adapterSelect"),
  generateAudio: document.getElementById("generateAudio"),
  apiStatus: document.getElementById("apiStatus"),
  error: document.getElementById("errorBanner"),
  runMeta: document.getElementById("runMeta"),
  original: document.getElementById("originalText"),
  normalized: document.getElementById("normalizedText"),
  ruleEntity: document.getElementById("ruleEntity"),
  ruleKannada: document.getElementById("ruleKannada"),
  ruleSpoken: document.getElementById("ruleSpoken"),
  ruleRepresentation: document.getElementById("ruleRepresentation"),
  modelEmpty: document.getElementById("modelEmpty"),
  modelOutput: document.getElementById("modelOutput"),
  modelError: document.getElementById("modelError"),
  modelChip: document.getElementById("modelChip"),
  modelEntity: document.getElementById("modelEntity"),
  modelKannada: document.getElementById("modelKannada"),
  modelSpoken: document.getElementById("modelSpoken"),
  modelRepresentation: document.getElementById("modelRepresentation"),
  nativeEntity: document.getElementById("nativeEntity"),
  nativeKannada: document.getElementById("nativeKannada"),
  sampleList: document.getElementById("sampleList"),
  baseModel: document.getElementById("baseModel"),
  adapterStatus: document.getElementById("adapterStatus"),
  registeredAdapterCount: document.getElementById("registeredAdapterCount"),
  adapterRegistryList: document.getElementById("adapterRegistryList"),
  entityCount: document.getElementById("entityCount"),
  verifiedCount: document.getElementById("verifiedCount"),
  pronunciationCount: document.getElementById("pronunciationCount"),
  ttsStatusChip: document.getElementById("ttsStatusChip"),
  audioStatusText: document.getElementById("audioStatusText"),
  rawAudio: document.getElementById("rawAudio"),
  normalizedAudio: document.getElementById("normalizedAudio"),
  nativeAudio: document.getElementById("nativeAudio"),
  runHistory: document.getElementById("runHistory"),
  refreshRuns: document.getElementById("refreshRuns"),
  experimentBackend: document.getElementById("experimentBackend"),
  experimentSuite: document.getElementById("experimentSuite"),
  experimentLimit: document.getElementById("experimentLimit"),
  runExperiment: document.getElementById("runExperiment"),
  experimentStatusChip: document.getElementById("experimentStatusChip"),
  metricEntityExact: document.getElementById("metricEntityExact"),
  metricSpokenExact: document.getElementById("metricSpokenExact"),
  metricCer: document.getElementById("metricCer"),
  metricElapsed: document.getElementById("metricElapsed"),
  candidateSelect: document.getElementById("candidateSelect"),
  candidateEnglish: document.getElementById("candidateEnglish"),
  candidateKannada: document.getElementById("candidateKannada"),
  candidateSourceName: document.getElementById("candidateSourceName"),
  candidateSourceUrl: document.getElementById("candidateSourceUrl"),
  candidateNotes: document.getElementById("candidateNotes"),
  saveCandidate: document.getElementById("saveCandidate"),
  markReviewed: document.getElementById("markReviewed"),
  rejectCandidate: document.getElementById("rejectCandidate"),
  annotationStats: document.getElementById("annotationStats"),
  experimentSuiteLabel: document.getElementById("experimentSuiteLabel"),
  errorTable: document.getElementById("errorTable"),
  readinessList: document.getElementById("readinessList"),
  failureSummary: document.getElementById("failureSummary"),
  exportImprovement: document.getElementById("exportImprovement"),
  exportStatus: document.getElementById("exportStatus"),
};

function setText(el, value, fallback = "—") {
  el.textContent = value || fallback;
}

function setApiStatus(ok) {
  els.apiStatus.classList.remove("status-loading", "status-ok", "status-error");
  els.apiStatus.classList.add(ok ? "status-ok" : "status-error");
  els.apiStatus.innerHTML = `
    <span class="status-dot"></span>
    ${ok ? "API online" : "API unavailable"}
  `;
}

function showError(message) {
  els.error.textContent = message;
  els.error.classList.remove("hidden");
}

function clearError() {
  els.error.classList.add("hidden");
  els.error.textContent = "";
}

function renderRule(rule) {
  setText(els.ruleEntity, rule.detected_entity);
  setText(els.ruleKannada, rule.entity_kannada);
  setText(els.ruleSpoken, rule.spoken_form || rule.pronunciation_form);
  setText(els.ruleRepresentation, rule.pronunciation_representation);

  setText(els.nativeEntity, rule.detected_entity);
  setText(els.nativeKannada, rule.spoken_form || rule.entity_kannada);
}

function renderModel(model, error, wasRequested) {
  els.modelError.classList.add("hidden");
  els.modelOutput.classList.add("hidden");
  els.modelEmpty.classList.remove("hidden");

  if (!wasRequested) {
    els.modelChip.textContent = "Not run";
    els.modelChip.classList.add("engine-chip-muted");
    els.modelEmpty.innerHTML =
      'Enable <strong>Compare model</strong> in the side panel to run the configured base model or adapter.';
    return;
  }

  if (error) {
    els.modelChip.textContent = "Unavailable";
    els.modelChip.classList.add("engine-chip-muted");
    els.modelEmpty.classList.add("hidden");
    els.modelError.textContent = error;
    els.modelError.classList.remove("hidden");
    return;
  }

  if (!model) {
    els.modelChip.textContent = "No output";
    els.modelChip.classList.add("engine-chip-muted");
    return;
  }

  els.modelChip.textContent =
    model.source === "adapter-model" ? "Adapter" : "Base model";
  els.modelChip.classList.remove("engine-chip-muted");
  els.modelEmpty.classList.add("hidden");
  els.modelOutput.classList.remove("hidden");

  setText(els.modelEntity, model.detected_entity);
  setText(els.modelKannada, model.entity_kannada);
  setText(els.modelSpoken, model.spoken_form || model.pronunciation_form);
  setText(els.modelRepresentation, model.pronunciation_representation);
}

function clearAudioElement(audio) {
  audio.removeAttribute("src");
  audio.load();
}

function setAudioElement(audio, url) {
  if (url) {
    audio.src = url;
    audio.load();
  } else {
    clearAudioElement(audio);
  }
}

function renderAudio(audio, wasRequested) {
  setAudioElement(els.rawAudio, audio?.raw_audio_url);
  setAudioElement(els.normalizedAudio, audio?.normalized_audio_url);
  setAudioElement(els.nativeAudio, audio?.native_audio_url);

  if (!wasRequested) {
    els.audioStatusText.textContent =
      "Enable Generate audio to synthesize comparison clips.";
    return;
  }

  if (!audio) {
    els.audioStatusText.textContent = "No audio response.";
    return;
  }

  const messages = {
    ready: "All comparison clips generated.",
    partial: "Some clips generated; one or more failed.",
    failed: "Audio generation failed.",
    unavailable: "TTS is not configured or unavailable.",
    "not-requested": "Audio was not requested.",
  };

  const suffix =
    audio.errors?.length ? ` ${audio.errors.join(" · ")}` : "";

  els.audioStatusText.textContent =
    (messages[audio.status] || audio.status) + suffix;
}

async function runComparison() {
  const text = els.input.value.trim();

  if (!text) {
    showError("Enter a navigation instruction first.");
    return;
  }

  clearError();
  els.run.disabled = true;
  els.runMeta.textContent = "Running…";

  try {
    const response = await fetch("/demo/compare", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        text,
        include_model: els.compareModel.checked,
        include_audio: els.generateAudio.checked,
        adapter_id: els.adapterSelect.value || null,
      }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "Comparison request failed.");
    }

    setText(els.original, payload.original_text);
    setText(els.normalized, payload.normalized_text);
    renderRule(payload.rule);
    renderModel(payload.model, payload.model_error, els.compareModel.checked);
    renderAudio(payload.audio, els.generateAudio.checked);

    const timings = payload.timings_ms || {};
    const parts = [`${timings.total ?? "?"} ms`];
    if (payload.run_id) parts.push(payload.run_id);
    els.runMeta.textContent = parts.join(" · ");

    await loadRuns();
  } catch (error) {
    showError(error.message || String(error));
    els.runMeta.textContent = "Failed";
  } finally {
    els.run.disabled = false;
  }
}

async function loadHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error();
    setApiStatus(true);
  } catch {
    setApiStatus(false);
  }
}

async function loadSamples() {
  try {
    const response = await fetch("/demo/samples");
    const payload = await response.json();
    els.sampleList.innerHTML = "";

    payload.samples.forEach((sample) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "sample-button";
      button.innerHTML = `
        <strong>${sample.label}</strong>
        <span>${sample.difficulty}</span>
      `;
      button.addEventListener("click", () => {
        document.querySelectorAll(".sample-button").forEach(
          x => x.classList.remove("active")
        );
        button.classList.add("active");
        els.input.value = sample.text;
        runComparison();
      });
      els.sampleList.appendChild(button);
    });
  } catch {
    els.sampleList.innerHTML =
      '<span class="muted-meta">Samples unavailable</span>';
  }
}

async function loadModelStatus() {
  try {
    const response = await fetch("/model/status");
    const payload = await response.json();

    setText(els.baseModel, payload.model_name, "Not configured");
    setText(
      els.adapterStatus,
      payload.active_adapter?.adapter_id,
      "No active adapter"
    );
    els.registeredAdapterCount.textContent =
      payload.registered_adapters ?? 0;
  } catch {
    setText(els.baseModel, null);
    setText(els.adapterStatus, null);
    els.registeredAdapterCount.textContent = "—";
  }
}

async function loadTTSStatus() {
  try {
    const response = await fetch("/tts/status");
    const payload = await response.json();

    if (payload.available) {
      els.ttsStatusChip.textContent = payload.provider || "TTS ready";
      els.ttsStatusChip.classList.remove("engine-chip-muted");
    } else {
      els.ttsStatusChip.textContent = "TTS off";
      els.ttsStatusChip.classList.add("engine-chip-muted");
    }
  } catch {
    els.ttsStatusChip.textContent = "TTS error";
    els.ttsStatusChip.classList.add("engine-chip-muted");
  }
}

async function loadDatasetStatus() {
  try {
    const response = await fetch("/dataset/status");
    const payload = await response.json();
    els.entityCount.textContent = payload.entities ?? 0;
    els.verifiedCount.textContent = payload.verified ?? 0;
    els.pronunciationCount.textContent =
      payload.pronunciation_verified ?? 0;
  } catch {
    els.entityCount.textContent = "—";
    els.verifiedCount.textContent = "—";
    els.pronunciationCount.textContent = "—";
  }
}

async function loadRuns() {
  try {
    const response = await fetch("/demo/runs?limit=6");
    const payload = await response.json();
    const runs = payload.runs || [];

    if (!runs.length) {
      els.runHistory.innerHTML =
        '<span class="muted-meta">No runs yet</span>';
      return;
    }

    els.runHistory.innerHTML = "";

    runs.forEach((run) => {
      const item = document.createElement("div");
      item.className = "run-item";

      const text = run.original_text || "Untitled run";
      const total = run.timings_ms?.total;

      item.innerHTML = `
        <strong>${escapeHtml(text)}</strong>
        <span>${run.run_id}${total != null ? ` · ${total} ms` : ""}</span>
      `;

      item.addEventListener("click", () => {
        els.input.value = text;
        runComparison();
      });

      els.runHistory.appendChild(item);
    });
  } catch {
    els.runHistory.innerHTML =
      '<span class="muted-meta">History unavailable</span>';
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

els.run.addEventListener("click", runComparison);

els.clear.addEventListener("click", () => {
  els.input.value = "";
  els.input.focus();
});

els.refreshRuns.addEventListener("click", loadRuns);

els.input.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    runComparison();
  }
});

Promise.all([
  loadHealth(),
  loadSamples(),
  loadModelStatus(),
  loadTTSStatus(),
  loadDatasetStatus(),
  loadRuns(),
]).then(() => runComparison());


let candidateRows = [];
let currentExperimentId = null;

function pct(value) {
  if (value == null) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

async function runExperiment() {
  els.runExperiment.disabled = true;
  els.experimentStatusChip.textContent = "Running";
  els.experimentStatusChip.classList.remove("engine-chip-muted");

  try {
    const response = await fetch("/experiments/evaluate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        backend: els.experimentBackend.value,
        suite_id: els.experimentSuite.value,
        limit: Number(els.experimentLimit.value || 10),
      }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "Experiment failed");
    }

    const summary = payload.summary || {};
    els.metricEntityExact.textContent = pct(summary.entity_exact_match);
    els.metricSpokenExact.textContent = pct(summary.spoken_form_exact_match);
    els.metricCer.textContent =
      summary.mean_character_error_rate == null
        ? "—"
        : Number(summary.mean_character_error_rate).toFixed(3);
    els.metricElapsed.textContent =
      summary.elapsed_ms == null ? "—" : `${summary.elapsed_ms} ms`;

    els.experimentStatusChip.textContent = payload.experiment_id;
    currentExperimentId = payload.experiment_id;
    els.exportImprovement.disabled = false;
    els.experimentSuiteLabel.textContent = payload.suite_label || payload.suite_id || "—";
    renderFailureSummary(payload.summary?.failure_counts || {});
    renderExperimentErrors(payload.results || []);
  } catch (error) {
    showError(error.message || String(error));
    els.experimentStatusChip.textContent = "Failed";
    els.experimentStatusChip.classList.add("engine-chip-muted");
  } finally {
    els.runExperiment.disabled = false;
  }
}

function populateCandidateForm(row) {
  if (!row) {
    els.candidateEnglish.value = "";
    els.candidateKannada.value = "";
    els.candidateSourceName.value = "";
    els.candidateSourceUrl.value = "";
    els.candidateNotes.value = "";
    return;
  }

  els.candidateEnglish.value = row.english_name || "";
  els.candidateKannada.value = row.kannada_name || "";
  els.candidateSourceName.value = row.source_name || "";
  els.candidateSourceUrl.value = row.source_url || "";
  els.candidateNotes.value = row.notes || "";
}

async function loadCandidates() {
  try {
    const response = await fetch("/annotations/candidates?limit=500");
    const payload = await response.json();

    candidateRows = payload.candidates || [];

    els.candidateSelect.innerHTML = "";
    candidateRows.forEach((row) => {
      const option = document.createElement("option");
      option.value = row.candidate_id;
      option.textContent = `${row.english_name} · ${row.annotation_status}`;
      els.candidateSelect.appendChild(option);
    });

    const stats = payload.stats || {};
    els.annotationStats.textContent =
      `${stats.reviewed || 0} reviewed · ${stats.candidate || 0} pending`;

    populateCandidateForm(candidateRows[0]);
  } catch {
    els.annotationStats.textContent = "Annotation queue unavailable";
  }
}

async function saveCandidate(statusOverride = null) {
  const candidateId = els.candidateSelect.value;
  if (!candidateId) return;

  const body = {
    kannada_name: els.candidateKannada.value,
    source_name: els.candidateSourceName.value,
    source_url: els.candidateSourceUrl.value,
    notes: els.candidateNotes.value,
  };

  if (statusOverride) {
    body.annotation_status = statusOverride;
  }

  try {
    const response = await fetch(
      `/annotations/candidates/${encodeURIComponent(candidateId)}`,
      {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body),
      }
    );

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "Unable to save candidate");
    }

    await loadCandidates();
    const next = candidateRows.find((row) => row.candidate_id === candidateId);
    if (next) {
      els.candidateSelect.value = candidateId;
      populateCandidateForm(next);
    }
  } catch (error) {
    showError(error.message || String(error));
  }
}

els.runExperiment.addEventListener("click", runExperiment);

els.candidateSelect.addEventListener("change", () => {
  const row = candidateRows.find(
    (item) => item.candidate_id === els.candidateSelect.value
  );
  populateCandidateForm(row);
});

els.saveCandidate.addEventListener("click", () => saveCandidate());
els.markReviewed.addEventListener("click", () => saveCandidate("reviewed"));
els.rejectCandidate.addEventListener("click", () => saveCandidate("rejected"));

loadCandidates();


function renderExperimentErrors(results) {
  const ranked = [...results]
    .sort(
      (a, b) =>
        Number(b.metrics?.character_error_rate || 0) -
        Number(a.metrics?.character_error_rate || 0)
    )
    .slice(0, 8);

  if (!ranked.length) {
    els.errorTable.innerHTML =
      '<span class="muted-meta">No evaluation rows returned.</span>';
    return;
  }

  els.errorTable.innerHTML = "";

  ranked.forEach((row) => {
    const div = document.createElement("div");
    div.className = "error-row";

    const target =
      row.target?.spoken_form ||
      row.target?.pronunciation_form ||
      row.target?.place_name_kn ||
      "—";

    const prediction =
      row.prediction?.spoken_form ||
      row.prediction?.pronunciation_form ||
      row.prediction?.place_name_kn ||
      "—";

    const cer = Number(row.metrics?.character_error_rate || 0);

    const tags = (row.failures || [])
      .map((failure) => `<span class="failure-tag">${escapeHtml(failure.label || failure.code)}</span>`)
      .join("");

    div.innerHTML = `
      <div>
        <strong>${escapeHtml(row.text || row.input?.text || row.example_id || "—")}</strong>
        <span>Target: ${escapeHtml(target)}</span>
        <div class="failure-list">${tags}</div>
      </div>
      <div>
        <strong>${escapeHtml(prediction)}</strong>
        <span>${escapeHtml(row.prediction?.place_name || row.prediction?.detected_entity || "No entity")}</span>
      </div>
      <div class="error-score">CER ${cer.toFixed(3)}</div>
    `;

    els.errorTable.appendChild(div);
  });
}

async function loadEvaluationSuites() {
  try {
    const response = await fetch("/evaluation/suites");
    const payload = await response.json();

    els.experimentSuite.innerHTML = "";

    (payload.suites || []).forEach((suite) => {
      const option = document.createElement("option");
      option.value = suite.id;
      option.textContent = suite.label;
      option.title = suite.description || "";
      els.experimentSuite.appendChild(option);
    });
  } catch {
    els.experimentSuite.innerHTML =
      '<option value="entity-held-out">Entity-held-out</option>';
  }
}

async function loadTrainingReadiness() {
  try {
    const response = await fetch("/training/readiness");
    const payload = await response.json();

    const gateLabels = {
      minimum_50_verified_entities: "50+ verified entities",
      minimum_25_pronunciation_verified: "25+ pronunciation-verified",
      minimum_3_entity_types: "3+ verified entity types",
      no_unreviewed_promotable_candidates: "No promotable rows waiting",
    };

    els.readinessList.innerHTML = "";

    Object.entries(payload.gates || {}).forEach(([key, passed]) => {
      const div = document.createElement("div");
      div.className = "readiness-item";
      div.innerHTML = `
        <strong>${escapeHtml(gateLabels[key] || key)}</strong>
        <span class="${passed ? "readiness-pass" : "readiness-fail"}">
          ${passed ? "PASS" : "BLOCKED"}
        </span>
      `;
      els.readinessList.appendChild(div);
    });

    const summary = document.createElement("div");
    summary.className = "readiness-item";
    summary.innerHTML = `
      <strong>Strict training</strong>
      <span class="${payload.ready_for_first_strict_training ? "readiness-pass" : "readiness-fail"}">
        ${payload.ready_for_first_strict_training ? "READY" : "NOT READY"}
      </span>
    `;
    els.readinessList.appendChild(summary);
  } catch {
    els.readinessList.innerHTML =
      '<span class="muted-meta">Readiness unavailable</span>';
  }
}

loadEvaluationSuites();
loadTrainingReadiness();


function renderFailureSummary(counts) {
  const entries = Object.entries(counts || {});

  if (!entries.length) {
    els.failureSummary.innerHTML =
      '<span class="muted-meta">No classified failures in this run.</span>';
    return;
  }

  els.failureSummary.innerHTML = "";

  entries.forEach(([code, count]) => {
    const chip = document.createElement("span");
    chip.className = "failure-chip";
    chip.innerHTML = `
      <span>${escapeHtml(code.replaceAll("_", " "))}</span>
      <strong>${count}</strong>
    `;
    els.failureSummary.appendChild(chip);
  });
}

async function exportImprovementDataset() {
  if (!currentExperimentId) return;

  els.exportImprovement.disabled = true;
  els.exportStatus.textContent = "Exporting…";

  try {
    const response = await fetch("/experiments/export-improvement", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        experiment_id: currentExperimentId,
      }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "Export failed");
    }

    els.exportStatus.textContent =
      `${payload.rows} rows → ${payload.output}`;
  } catch (error) {
    els.exportStatus.textContent = error.message || String(error);
  } finally {
    els.exportImprovement.disabled = false;
  }
}

els.exportImprovement.addEventListener(
  "click",
  exportImprovementDataset
);


async function loadAdapters() {
  try {
    const response = await fetch("/adapters");
    const payload = await response.json();

    const adapters = payload.adapters || [];
    const activeId = payload.active_adapter?.adapter_id || null;

    els.adapterSelect.innerHTML = "";

    const baseOption = document.createElement("option");
    baseOption.value = "base";
    baseOption.textContent = "Base model";
    els.adapterSelect.appendChild(baseOption);

    adapters.forEach((adapter) => {
      const option = document.createElement("option");
      option.value = adapter.adapter_id;
      option.textContent =
        `${adapter.adapter_id}${adapter.adapter_id === activeId ? " · active" : ""}`;
      els.adapterSelect.appendChild(option);
    });

    if (activeId) {
      els.adapterSelect.value = activeId;
    }

    if (!adapters.length) {
      els.adapterRegistryList.innerHTML =
        '<span class="muted-meta">No adapters registered</span>';
      return;
    }

    els.adapterRegistryList.innerHTML = "";

    adapters.forEach((adapter) => {
      const row = document.createElement("div");
      row.className =
        `adapter-row${adapter.adapter_id === activeId ? " active" : ""}`;

      row.innerHTML = `
        <strong>${escapeHtml(adapter.adapter_id)}</strong>
        <span>${escapeHtml(adapter.status || "candidate")} · ${escapeHtml(adapter.base_model || "")}</span>
        <span>${escapeHtml(adapter.adapter_path || "")}</span>
        ${
          adapter.adapter_id === activeId
            ? ""
            : `<button type="button">Promote</button>`
        }
      `;

      const button = row.querySelector("button");
      if (button) {
        button.addEventListener("click", () => promoteAdapter(adapter.adapter_id));
      }

      els.adapterRegistryList.appendChild(row);
    });
  } catch {
    els.adapterRegistryList.innerHTML =
      '<span class="muted-meta">Adapter registry unavailable</span>';
  }
}

async function promoteAdapter(adapterId) {
  try {
    const response = await fetch("/adapters/promote", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({adapter_id: adapterId}),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "Promotion failed");
    }

    await Promise.all([loadAdapters(), loadModelStatus()]);
  } catch (error) {
    showError(error.message || String(error));
  }
}

loadAdapters();
