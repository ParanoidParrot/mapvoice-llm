const $ = (id) => document.getElementById(id);
const els = {
  error: $("globalError"),
  apiStatus: $("apiStatus"),
  heroPack: $("heroPack"),
  heroModel: $("heroModel"),
  developmentMap: $("developmentMap"),
  packStatusBadge: $("packStatusBadge"),
  packId: $("packId"),
  packCity: $("packCity"),
  packLanguage: $("packLanguage"),
  packLanguageCode: $("packLanguageCode"),
  packEntityFile: $("packEntityFile"),
  packCandidateFile: $("packCandidateFile"),
  consoleEntityCount: $("consoleEntityCount"),
  consoleCandidateCount: $("consoleCandidateCount"),
  consoleVerifiedCount: $("consoleVerifiedCount"),
  consolePronunciationCount: $("consolePronunciationCount"),
  runtimePython: $("runtimePython"),
  dependencyBadge: $("dependencyBadge"),
  dependencyCount: $("dependencyCount"),
  dependencyList: $("dependencyList"),
  trainingRunCount: $("trainingRunCount"),
  checkpointCount: $("checkpointCount"),
  adapterCount: $("adapterCount"),
  experimentCount: $("experimentCount"),
  trainingRunList: $("trainingRunList"),
  consoleAdapterList: $("consoleAdapterList"),
  readinessList: $("readinessList"),
  strictTrainingBadge: $("strictTrainingBadge"),
  hfExportCount: $("hfExportCount"),
  improvementCount: $("improvementCount"),
  consoleTtsStatus: $("consoleTtsStatus"),
  regionalPackGrid: $("regionalPackGrid"),
  refreshConsole: $("refreshConsole"),

  input: $("navigationInput"),
  run: $("runButton"),
  clear: $("clearButton"),
  runMeta: $("runMeta"),
  original: $("originalText"),
  normalized: $("normalizedText"),
  ruleEntity: $("ruleEntity"),
  ruleKannada: $("ruleKannada"),
  ruleSpoken: $("ruleSpoken"),
  ruleRepresentation: $("ruleRepresentation"),
  modelChip: $("modelChip"),
  modelEmpty: $("modelEmpty"),
  modelError: $("modelError"),
  modelOutput: $("modelOutput"),
  modelEntity: $("modelEntity"),
  modelKannada: $("modelKannada"),
  modelSpoken: $("modelSpoken"),
  modelRepresentation: $("modelRepresentation"),
  nativeEntity: $("nativeEntity"),
  nativeKannada: $("nativeKannada"),
  nativeLanguageBadge: $("nativeLanguageBadge"),
  rawAudio: $("rawAudio"),
  normalizedAudio: $("normalizedAudio"),
  nativeAudio: $("nativeAudio"),
  audioStatusText: $("audioStatusText"),
  adapterSelect: $("adapterSelect"),
  compareModel: $("compareModel"),
  generateAudio: $("generateAudio"),
  baseModel: $("baseModel"),
  adapterStatus: $("adapterStatus"),
  ttsStatusChip: $("ttsStatusChip"),
  ttsModel: $("ttsModel"),
  ttsNativeLanguage: $("ttsNativeLanguage"),
  ttsReason: $("ttsReason"),
  sampleList: $("sampleList"),
  runHistory: $("runHistory"),
  refreshRuns: $("refreshRuns"),

  entityCount: $("entityCount"),
  verifiedCount: $("verifiedCount"),
  pronunciationCount: $("pronunciationCount"),
  candidateSelect: $("candidateSelect"),
  candidateEnglish: $("candidateEnglish"),
  candidateKannada: $("candidateKannada"),
  nativeNameLabel: $("nativeNameLabel"),
  candidateSourceName: $("candidateSourceName"),
  candidateSourceUrl: $("candidateSourceUrl"),
  candidateNotes: $("candidateNotes"),
  saveCandidate: $("saveCandidate"),
  markReviewed: $("markReviewed"),
  rejectCandidate: $("rejectCandidate"),
  annotationStats: $("annotationStats"),

  experimentBackend: $("experimentBackend"),
  experimentSuite: $("experimentSuite"),
  experimentLimit: $("experimentLimit"),
  runExperiment: $("runExperiment"),
  experimentStatusChip: $("experimentStatusChip"),
  metricEntityExact: $("metricEntityExact"),
  metricSpokenExact: $("metricSpokenExact"),
  metricCer: $("metricCer"),
  metricElapsed: $("metricElapsed"),
  experimentSuiteLabel: $("experimentSuiteLabel"),
  failureSummary: $("failureSummary"),
  errorTable: $("errorTable"),
  exportImprovement: $("exportImprovement"),
  exportStatus: $("exportStatus"),

  trainingPackSelect: $("trainingPackSelect"),
  trainingProfileSelect: $("trainingProfileSelect"),
  trainingVersion: $("trainingVersion"),
  generateTrainingPlan: $("generateTrainingPlan"),
  trainingPlanBadge: $("trainingPlanBadge"),
  trainingPlanDetails: $("trainingPlanDetails"),
  planAdapterId: $("planAdapterId"),
  planModel: $("planModel"),
  planQuantization: $("planQuantization"),
  planEpochs: $("planEpochs"),
  trainingCommand: $("trainingCommand"),
  trainingWarnings: $("trainingWarnings"),
  copyTrainingCommand: $("copyTrainingCommand"),
  buildPackDatasetButton: $("buildPackDatasetButton"),
  packDatasetBuildStatus: $("packDatasetBuildStatus"),
  trainingHistoryCount: $("trainingHistoryCount"),
  trainingHistoryTable: $("trainingHistoryTable"),
  trainingCheckpointCount: $("trainingCheckpointCount"),
  trainingAdapterCount: $("trainingAdapterCount"),
  packDatasetState: $("packDatasetState"),

  refreshExperimentHistory: $("refreshExperimentHistory"),
  firstExperimentSelect: $("firstExperimentSelect"),
  secondExperimentSelect: $("secondExperimentSelect"),
  compareExperiments: $("compareExperiments"),
  experimentComparison: $("experimentComparison"),
  deltaEntityExact: $("deltaEntityExact"),
  deltaSpokenExact: $("deltaSpokenExact"),
  deltaCer: $("deltaCer"),
  deltaRuntime: $("deltaRuntime"),
};

let projectStatus = null;
let candidateRows = [];
let currentExperimentId = null;

function text(el, value, fallback = "—") {
  if (el) el.textContent = value ?? fallback;
}
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
function showError(message) {
  els.error.textContent = message;
  els.error.classList.remove("hidden");
}
function clearError() {
  els.error.textContent = "";
  els.error.classList.add("hidden");
}
async function getJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || `${response.status} ${response.statusText}`);
  return payload;
}
function pct(value) {
  return value == null ? "—" : `${(Number(value) * 100).toFixed(1)}%`;
}

document.querySelectorAll(".nav-tab").forEach((button) => {
  button.addEventListener("click", () => {
    const view = button.dataset.view;
    document.querySelectorAll(".nav-tab").forEach(x => x.classList.toggle("active", x === button));
    document.querySelectorAll("[data-view-panel]").forEach(panel => {
      panel.classList.toggle("active", panel.dataset.viewPanel === view);
    });
  });
});

async function loadHealth() {
  try {
    const payload = await getJson("/health");
    els.apiStatus.className = "status-chip ok";
    els.apiStatus.innerHTML = `<span class="status-dot"></span> API online · ${escapeHtml(payload.version)}`;
  } catch {
    els.apiStatus.className = "status-chip error";
    els.apiStatus.innerHTML = `<span class="status-dot"></span> API unavailable`;
  }
}

function renderDevelopmentMap(rows) {
  els.developmentMap.innerHTML = "";
  rows.forEach((row) => {
    const div = document.createElement("div");
    div.className = "stage-card";
    div.innerHTML = `
      <div class="stage-top">
        <strong>${escapeHtml(row.label)}</strong>
        <span class="stage-state ${escapeHtml(row.status)}"></span>
      </div>
      <p>${escapeHtml(row.detail)}</p>
    `;
    els.developmentMap.appendChild(div);
  });
}

function renderDependencies(rows) {
  els.dependencyList.innerHTML = "";
  rows.forEach((row) => {
    const pill = document.createElement("span");
    pill.className = `dependency-pill ${row.installed ? "ok" : "missing"}`;
    pill.textContent = `${row.name}${row.version ? ` ${row.version}` : ""}`;
    els.dependencyList.appendChild(pill);
  });
}

async function loadTrainingRuns() {
  try {
    const payload = await getJson("/training/runs?limit=25");
    const runs = payload.runs || [];
    els.trainingRunList.innerHTML = "";
    els.trainingHistoryTable.innerHTML = "";
    text(els.trainingHistoryCount, `${runs.length} runs`);

    if (!runs.length) {
      els.trainingRunList.innerHTML = '<span class="muted">No training runs recorded yet.</span>';
      els.trainingHistoryTable.innerHTML = '<span class="muted">No training runs recorded yet.</span>';
      return;
    }

    runs.slice(0, 5).forEach((run) => {
      const card = document.createElement("div");
      card.className = "compact-card";
      card.innerHTML = `
        <strong>${escapeHtml(run.run_id)}</strong>
        <span>${escapeHtml(run.status)} · ${escapeHtml(run.model_name || "")}</span>
        <span>${escapeHtml(run.output_dir || run.error || "")}</span>
      `;
      els.trainingRunList.appendChild(card);
    });

    runs.forEach((run) => {
      const row = document.createElement("div");
      row.className = "history-row";
      row.innerHTML = `
        <strong>${escapeHtml(run.run_id)}</strong>
        <span>${escapeHtml(run.status)}</span>
        <span>${escapeHtml(run.model_name || "")}</span>
        <span>${escapeHtml(run.adapter_id || "—")}</span>
      `;
      els.trainingHistoryTable.appendChild(row);
    });
  } catch {
    els.trainingRunList.innerHTML = '<span class="muted">Training-run history unavailable.</span>';
    els.trainingHistoryTable.innerHTML = '<span class="muted">Training-run history unavailable.</span>';
  }
}

async function loadAdapters() {
  try {
    const payload = await getJson("/adapters");
    const adapters = payload.adapters || [];
    const activeId = payload.active_adapter?.adapter_id || null;

    els.adapterSelect.innerHTML = '<option value="base">Base model</option>';
    els.consoleAdapterList.innerHTML = "";

    adapters.forEach((adapter) => {
      const option = document.createElement("option");
      option.value = adapter.adapter_id;
      option.textContent = `${adapter.adapter_id}${adapter.adapter_id === activeId ? " · active" : ""}`;
      els.adapterSelect.appendChild(option);

      const card = document.createElement("div");
      card.className = "adapter-row";
      card.innerHTML = `
        <strong>${escapeHtml(adapter.adapter_id)}</strong>
        <span>${escapeHtml(adapter.status || "candidate")} · ${escapeHtml(adapter.base_model || "")}</span>
        <span>${escapeHtml(adapter.adapter_path || "")}</span>
      `;
      if (adapter.adapter_id !== activeId) {
        const button = document.createElement("button");
        button.className = "text-button";
        button.textContent = "Promote";
        button.addEventListener("click", () => promoteAdapter(adapter.adapter_id));
        card.appendChild(button);
      }
      els.consoleAdapterList.appendChild(card);
    });

    if (!adapters.length) {
      els.consoleAdapterList.innerHTML = '<span class="muted">No adapters registered yet.</span>';
    }
    if (activeId) els.adapterSelect.value = activeId;

    text(els.adapterStatus, activeId, "No active adapter");
  } catch (error) {
    els.consoleAdapterList.innerHTML = `<span class="muted">${escapeHtml(error.message)}</span>`;
  }
}

async function promoteAdapter(adapterId) {
  clearError();
  try {
    await getJson("/adapters/promote", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({adapter_id: adapterId}),
    });
    await Promise.all([loadAdapters(), loadProjectConsole()]);
  } catch (error) {
    showError(error.message);
  }
}

async function loadReadiness() {
  try {
    const payload = await getJson("/training/readiness");
    const labels = {
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
        <strong>${escapeHtml(labels[key] || key)}</strong>
        <span class="${passed ? "readiness-pass" : "readiness-fail"}">${passed ? "PASS" : "BLOCKED"}</span>
      `;
      els.readinessList.appendChild(div);
    });

    els.strictTrainingBadge.textContent = payload.ready_for_first_strict_training ? "READY" : "NOT READY";
    els.strictTrainingBadge.className = `badge ${payload.ready_for_first_strict_training ? "good" : "bad"}`;
  } catch {
    els.readinessList.innerHTML = '<span class="muted">Readiness unavailable.</span>';
  }
}

async function loadDatasetStatus() {
  try {
    const payload = await getJson("/dataset/status");
    text(els.entityCount, payload.entities ?? 0);
    text(els.verifiedCount, payload.verified ?? 0);
    text(els.pronunciationCount, payload.pronunciation_verified ?? 0);
    text(els.consoleVerifiedCount, payload.verified ?? 0);
    text(els.consolePronunciationCount, payload.pronunciation_verified ?? 0);
  } catch {
    [els.entityCount, els.verifiedCount, els.pronunciationCount].forEach(el => text(el, "—"));
  }
}

async function loadProjectConsole() {
  clearError();
  try {
    projectStatus = await getJson("/project/status");
    const pack = projectStatus.active_pack || {};
    const artifacts = projectStatus.artifacts || {};
    const ds = artifacts.dataset || {};
    const training = artifacts.training || {};
    const models = artifacts.models || {};
    const evaluation = artifacts.evaluation || {};
    const publishing = artifacts.publishing || {};

    text(els.heroPack, `${pack.pack_id || "—"} · ${pack.city || ""} / ${pack.region_language || ""}`);
    text(els.heroModel, projectStatus.base_model);
    text(els.packId, pack.pack_id);
    text(els.packCity, pack.city);
    text(els.packLanguage, pack.region_language);
    text(els.packLanguageCode, pack.region_language_code);
    text(els.packEntityFile, pack.entity_file);
    text(els.packCandidateFile, pack.candidate_file);
    els.packStatusBadge.textContent = pack.status || "unknown";
    els.packStatusBadge.className = `badge ${pack.status === "experimental" ? "warm" : "neutral"}`;

    text(els.consoleEntityCount, ds.entity_rows ?? 0);
    text(els.consoleCandidateCount, ds.candidate_rows ?? 0);
    text(els.runtimePython, projectStatus.runtime?.python);
    text(els.dependencyCount, `${projectStatus.dependency_summary?.installed ?? 0}/${projectStatus.dependency_summary?.total ?? 0}`);
    els.dependencyBadge.textContent = projectStatus.dependency_summary?.all_installed ? "ALL INSTALLED" : "INCOMPLETE";
    els.dependencyBadge.className = `badge ${projectStatus.dependency_summary?.all_installed ? "good" : "bad"}`;
    renderDependencies(projectStatus.dependencies || []);

    text(els.trainingRunCount, training.training_runs ?? 0);
    text(els.checkpointCount, training.checkpoints ?? 0);
    text(els.adapterCount, models.registered_adapters ?? 0);
    text(els.experimentCount, evaluation.experiments ?? 0);
    text(els.hfExportCount, publishing.hf_export_bundles ?? 0);
    text(els.improvementCount, evaluation.improvement_datasets ?? 0);
    text(els.consoleTtsStatus, projectStatus.tts?.available ? `${projectStatus.tts.provider} ready` : "not configured");
    text(els.trainingCheckpointCount, training.checkpoints ?? 0);
    text(els.trainingAdapterCount, models.registered_adapters ?? 0);
    text(els.packDatasetState, training.pack_dataset_manifest_exists ? "Built" : "Not built");

    renderDevelopmentMap(projectStatus.development_map || []);
    els.nativeLanguageBadge.textContent = pack.region_language || "Native language";
    els.nativeNameLabel.textContent = `${pack.region_language || "Native-language"} name`;
  } catch (error) {
    showError(`Project console: ${error.message}`);
  }

  await Promise.all([
    loadDatasetStatus(),
    loadReadiness(),
    loadTrainingRuns(),
    loadAdapters(),
    loadRegionalPackStatus(),
  ]);
}

async function loadModelStatus() {
  try {
    const payload = await getJson("/model/status");
    text(els.baseModel, payload.model_name, "Not configured");
    text(els.adapterStatus, payload.active_adapter?.adapter_id, "No active adapter");
  } catch {
    text(els.baseModel, "—");
  }
}

async function loadTTSStatus() {
  try {
    const payload = await getJson("/tts/status");

    text(
      els.ttsStatusChip,
      payload.available
        ? `${payload.provider} ready`
        : "Unavailable"
    );
    text(els.ttsModel, payload.model);
    text(
      els.ttsNativeLanguage,
      payload.native_language_code
    );
    els.ttsReason.textContent =
      payload.available
        ? `Audio generation is enabled by default · ${payload.speaker || ""}`
        : (
            payload.reason
            || (
              !payload.sdk_installed
                ? "Install requirements-tts.txt"
                : "Configure SARVAM_API_KEY"
            )
          );

    // The user's expectation is that Run produces audio when TTS is configured.
    els.generateAudio.checked = Boolean(payload.available);
    els.generateAudio.disabled = !payload.available;
  } catch {
    text(els.ttsStatusChip, "Error");
    els.generateAudio.checked = false;
    els.generateAudio.disabled = true;
    els.ttsReason.textContent = "Unable to read TTS status.";
  }
}

async function loadSamples() {
  try {
    const payload = await getJson("/demo/samples");
    els.sampleList.innerHTML = "";
    (payload.samples || []).forEach((sample) => {
      const button = document.createElement("button");
      button.className = "sample-button";
      button.innerHTML = `<strong>${escapeHtml(sample.label)}</strong><span>${escapeHtml(sample.difficulty)}</span>`;
      button.addEventListener("click", () => {
        els.input.value = sample.text;
        runComparison();
      });
      els.sampleList.appendChild(button);
    });
  } catch {
    els.sampleList.innerHTML = '<span class="muted">Samples unavailable.</span>';
  }
}

function renderModel(model, error, requested) {
  els.modelEmpty.classList.remove("hidden");
  els.modelError.classList.add("hidden");
  els.modelOutput.classList.add("hidden");

  if (!requested) {
    els.modelChip.textContent = "Not run";
    els.modelChip.className = "badge neutral";
    return;
  }
  if (error) {
    els.modelChip.textContent = "Unavailable";
    els.modelChip.className = "badge bad";
    els.modelEmpty.classList.add("hidden");
    els.modelError.textContent = error;
    els.modelError.classList.remove("hidden");
    return;
  }
  if (!model) return;

  els.modelChip.textContent = model.source || "Model";
  els.modelChip.className = "badge good";
  els.modelEmpty.classList.add("hidden");
  els.modelOutput.classList.remove("hidden");
  text(els.modelEntity, model.detected_entity);
  text(els.modelKannada, model.entity_native || model.entity_kannada || model.native_name);
  text(els.modelSpoken, model.spoken_form || model.pronunciation_form);
  text(els.modelRepresentation, model.pronunciation_representation);
}

function setAudio(audio, url) {
  if (url) audio.src = url;
  else audio.removeAttribute("src");
  audio.load();
}

async function runComparison() {
  const value = els.input.value.trim();
  if (!value) return showError("Enter a navigation instruction.");

  clearError();
  els.run.disabled = true;
  els.runMeta.textContent = "Running…";

  try {
    const payload = await getJson("/demo/compare", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        text: value,
        include_model: els.compareModel.checked,
        include_audio: els.generateAudio.checked,
        adapter_id: els.adapterSelect.value || "base",
      }),
    });

    text(els.original, payload.original_text);
    text(els.normalized, payload.normalized_text);
    const rule = payload.rule || {};
    text(els.ruleEntity, rule.detected_entity);
    text(els.ruleKannada, rule.entity_native || rule.entity_kannada || rule.native_name);
    text(els.ruleSpoken, rule.spoken_form || rule.pronunciation_form);
    text(els.ruleRepresentation, rule.pronunciation_representation);
    text(els.nativeEntity, rule.detected_entity);
    text(els.nativeKannada, rule.spoken_form || rule.entity_native || rule.entity_kannada || rule.native_name);

    renderModel(payload.model, payload.model_error, els.compareModel.checked);

    const audio = payload.audio || {};
    setAudio(els.rawAudio, audio.raw_audio_url);
    setAudio(els.normalizedAudio, audio.normalized_audio_url);
    setAudio(els.nativeAudio, audio.native_audio_url);
    if (audio.status === "ready") {
      const generated = (audio.generated || []).join(", ");
      const cached = (audio.cache_hits || []).join(", ");
      const parts = [];
      if (generated) parts.push(`generated: ${generated}`);
      if (cached) parts.push(`cached: ${cached}`);
      els.audioStatusText.textContent =
        `Audio ready${parts.length ? " · " + parts.join(" · ") : ""}`;
    } else if (audio.status === "unavailable") {
      els.audioStatusText.textContent =
        audio.errors?.join(" · ") || "TTS is not configured.";
    } else {
      els.audioStatusText.textContent =
        audio.errors?.join(" · ") || `Audio status: ${audio.status}`;
    }

    els.runMeta.textContent = `${payload.timings_ms?.total ?? "?"} ms · ${payload.run_id || ""}`;
    await Promise.all([loadRuns(), loadProjectConsole()]);
  } catch (error) {
    showError(error.message);
    els.runMeta.textContent = "Failed";
  } finally {
    els.run.disabled = false;
  }
}

async function loadRuns() {
  try {
    const payload = await getJson("/demo/runs?limit=6");
    els.runHistory.innerHTML = "";
    const runs = payload.runs || [];
    if (!runs.length) {
      els.runHistory.innerHTML = '<span class="muted">No demo runs yet.</span>';
      return;
    }
    runs.forEach((run) => {
      const card = document.createElement("button");
      card.className = "run-item";
      card.innerHTML = `<strong>${escapeHtml(run.original_text || "Untitled")}</strong><span>${escapeHtml(run.run_id)}</span>`;
      card.addEventListener("click", () => {
        els.input.value = run.original_text || "";
        runComparison();
      });
      els.runHistory.appendChild(card);
    });
  } catch {
    els.runHistory.innerHTML = '<span class="muted">History unavailable.</span>';
  }
}

function populateCandidateForm(row) {
  text(els.annotationStats, row ? `Editing ${row.candidate_id}` : "No candidate");
  els.candidateEnglish.value = row?.latin_name || row?.english_name || "";
  els.candidateKannada.value = row?.native_name || row?.kannada_name || "";
  els.candidateSourceName.value = row?.source_name || "";
  els.candidateSourceUrl.value = row?.source_url || "";
  els.candidateNotes.value = row?.notes || "";
}

async function loadCandidates() {
  try {
    const payload = await getJson("/annotations/candidates?limit=500");
    candidateRows = payload.candidates || [];
    els.candidateSelect.innerHTML = "";

    candidateRows.forEach((row) => {
      const option = document.createElement("option");
      option.value = row.candidate_id;
      option.textContent = `${row.latin_name || row.english_name} · ${row.annotation_status}`;
      els.candidateSelect.appendChild(option);
    });

    const stats = payload.stats || {};
    els.annotationStats.textContent = `${stats.reviewed || 0} reviewed · ${stats.candidate || 0} pending`;
    populateCandidateForm(candidateRows[0]);
  } catch (error) {
    els.annotationStats.textContent = error.message;
  }
}

async function saveCandidate(statusOverride = null) {
  const id = els.candidateSelect.value;
  if (!id) return;

  clearError();
  try {
    await getJson(`/annotations/candidates/${encodeURIComponent(id)}`, {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        native_name: els.candidateKannada.value,
        source_name: els.candidateSourceName.value,
        source_url: els.candidateSourceUrl.value,
        notes: els.candidateNotes.value,
        ...(statusOverride ? {annotation_status: statusOverride} : {}),
      }),
    });
    await Promise.all([loadCandidates(), loadProjectConsole()]);
  } catch (error) {
    showError(error.message);
  }
}

async function loadEvaluationSuites() {
  try {
    const payload = await getJson("/evaluation/suites");
    els.experimentSuite.innerHTML = "";
    (payload.suites || []).forEach((suite) => {
      const option = document.createElement("option");
      option.value = suite.id;
      option.textContent = suite.label;
      els.experimentSuite.appendChild(option);
    });
  } catch {
    els.experimentSuite.innerHTML = '<option value="entity-held-out">Entity-held-out</option>';
  }
}

function renderFailureSummary(counts) {
  els.failureSummary.innerHTML = "";
  Object.entries(counts || {}).forEach(([code, count]) => {
    const chip = document.createElement("span");
    chip.className = "failure-chip";
    chip.textContent = `${code.replaceAll("_", " ")} · ${count}`;
    els.failureSummary.appendChild(chip);
  });
  if (!Object.keys(counts || {}).length) {
    els.failureSummary.innerHTML = '<span class="muted">No classified failures.</span>';
  }
}

function renderErrors(results) {
  const ranked = [...results]
    .sort((a,b) => Number(b.metrics?.character_error_rate || 0) - Number(a.metrics?.character_error_rate || 0))
    .slice(0, 10);

  els.errorTable.innerHTML = "";
  if (!ranked.length) {
    els.errorTable.innerHTML = '<span class="muted">No evaluation rows returned.</span>';
    return;
  }

  ranked.forEach((row) => {
    const target = row.target?.spoken_form || row.target?.pronunciation_form || row.target?.place_name_kn || "—";
    const prediction = row.prediction?.spoken_form || row.prediction?.pronunciation_form || row.prediction?.place_name_kn || "—";
    const tags = (row.failures || []).map(f => `<span class="failure-tag">${escapeHtml(f.label || f.code)}</span>`).join("");
    const div = document.createElement("div");
    div.className = "error-row";
    div.innerHTML = `
      <div><strong>${escapeHtml(row.text || row.example_id)}</strong><span>Target: ${escapeHtml(target)}</span><div class="chip-row">${tags}</div></div>
      <div><strong>${escapeHtml(prediction)}</strong><span>${escapeHtml(row.prediction?.place_name || row.prediction?.detected_entity || "No entity")}</span></div>
      <div class="error-score">CER ${Number(row.metrics?.character_error_rate || 0).toFixed(3)}</div>
    `;
    els.errorTable.appendChild(div);
  });
}

async function runExperiment() {
  els.runExperiment.disabled = true;
  els.experimentStatusChip.textContent = "Running";
  clearError();

  try {
    const payload = await getJson("/experiments/evaluate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        backend: els.experimentBackend.value,
        suite_id: els.experimentSuite.value,
        limit: Number(els.experimentLimit.value || 10),
      }),
    });
    currentExperimentId = payload.experiment_id;
    text(els.metricEntityExact, pct(payload.summary?.entity_exact_match));
    text(els.metricSpokenExact, pct(payload.summary?.spoken_form_exact_match));
    text(els.metricCer, payload.summary?.mean_character_error_rate?.toFixed?.(3) ?? payload.summary?.mean_character_error_rate);
    text(els.metricElapsed, `${payload.summary?.elapsed_ms ?? "—"} ms`);
    text(els.experimentSuiteLabel, payload.suite_label || payload.suite_id);
    els.experimentStatusChip.textContent = payload.experiment_id;
    els.experimentStatusChip.className = "badge good";
    els.exportImprovement.disabled = false;
    renderFailureSummary(payload.summary?.failure_counts || {});
    renderErrors(payload.results || []);
    await loadProjectConsole();
  } catch (error) {
    showError(error.message);
    els.experimentStatusChip.textContent = "Failed";
    els.experimentStatusChip.className = "badge bad";
  } finally {
    els.runExperiment.disabled = false;
  }
}

async function exportImprovement() {
  if (!currentExperimentId) return;
  try {
    const payload = await getJson("/experiments/export-improvement", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({experiment_id: currentExperimentId}),
    });
    els.exportStatus.textContent = `${payload.rows} rows → ${payload.output}`;
    await loadProjectConsole();
  } catch (error) {
    els.exportStatus.textContent = error.message;
  }
}



async function loadRegionalPackStatus() {
  try {
    const payload = await getJson("/regional-packs/status");
    const packs = payload.packs || [];

    els.regionalPackGrid.innerHTML = "";

    packs.forEach((pack) => {
      const card = document.createElement("div");
      card.className =
        `regional-pack-card${
          pack.pack_id === projectStatus?.active_pack?.pack_id
            ? " active"
            : ""
        }`;

      card.innerHTML = `
        <strong>${escapeHtml(pack.city)} · ${escapeHtml(pack.region_language)}</strong>
        <span>${escapeHtml(pack.pack_id)} · ${escapeHtml(pack.status)}</span>
        <span>${pack.entity_count} entities · ${pack.candidate_count} candidates</span>
        <span>${pack.candidate_native_names} native labels · ${pack.reviewed_candidates} reviewed</span>
        <code>python scripts/run_local.py --pack-id ${escapeHtml(pack.pack_id)}</code>
      `;

      els.regionalPackGrid.appendChild(card);
    });
  } catch (error) {
    els.regionalPackGrid.innerHTML =
      `<span class="muted">${escapeHtml(error.message)}</span>`;
  }
}

async function loadTrainingPlanner() {
  try {
    const [packsPayload, profilesPayload] = await Promise.all([
      getJson("/regional-packs"),
      getJson("/training/profiles"),
    ]);
    els.trainingPackSelect.innerHTML = "";
    (packsPayload.packs || []).forEach((pack) => {
      const option = document.createElement("option");
      option.value = pack.pack_id;
      option.textContent = `${pack.pack_id} · ${pack.city} / ${pack.region_language}`;
      els.trainingPackSelect.appendChild(option);
    });
    if (projectStatus?.active_pack?.pack_id) els.trainingPackSelect.value = projectStatus.active_pack.pack_id;
    els.trainingProfileSelect.innerHTML = "";
    (profilesPayload.profiles || []).forEach((profile) => {
      const option = document.createElement("option");
      option.value = profile.profile_id;
      option.textContent = profile.label;
      option.title = profile.description || "";
      els.trainingProfileSelect.appendChild(option);
    });
    if (profilesPayload.default_profile?.profile_id) els.trainingProfileSelect.value = profilesPayload.default_profile.profile_id;
  } catch (error) { showError(`Training planner: ${error.message}`); }
}

async function generateTrainingPlan() {
  clearError(); els.generateTrainingPlan.disabled = true; els.trainingPlanBadge.textContent = "Generating";
  try {
    const payload = await getJson("/training/plan", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pack_id:els.trainingPackSelect.value||null,profile_id:els.trainingProfileSelect.value||null,version:els.trainingVersion.value||"v1"})});
    text(els.planAdapterId,payload.adapter_id); text(els.planModel,payload.model_name); text(els.planQuantization,payload.quantization); text(els.planEpochs,payload.epochs);
    els.trainingCommand.textContent = payload.command; els.trainingWarnings.innerHTML = "";
    (payload.warnings||[]).forEach((warning)=>{const div=document.createElement("div");div.className="warning-item";div.textContent=warning;els.trainingWarnings.appendChild(div);});
    els.trainingPlanDetails.classList.remove("hidden"); els.trainingPlanBadge.textContent=payload.profile_id; els.trainingPlanBadge.className="badge good";
  } catch(error) { showError(error.message); els.trainingPlanBadge.textContent="Failed"; els.trainingPlanBadge.className="badge bad"; }
  finally { els.generateTrainingPlan.disabled=false; }
}

async function copyTrainingCommand() {
  try { await navigator.clipboard.writeText(els.trainingCommand.textContent||""); els.copyTrainingCommand.textContent="Copied"; setTimeout(()=>els.copyTrainingCommand.textContent="Copy command",1200); }
  catch { showError("Unable to copy command to clipboard."); }
}

async function buildActivePackDataset() {
  clearError(); els.buildPackDatasetButton.disabled=true; els.packDatasetBuildStatus.textContent="Building…";
  try {
    const packId=els.trainingPackSelect.value;
    const payload=await getJson(`/training/build-pack-dataset?pack_id=${encodeURIComponent(packId)}`,{method:"POST"});
    els.packDatasetBuildStatus.textContent=`${payload.total_examples} examples → ${payload.output_dir}`;
    await loadProjectConsole();
  } catch(error) { els.packDatasetBuildStatus.textContent=error.message; }
  finally { els.buildPackDatasetButton.disabled=false; }
}

async function loadExperimentHistory() {
  try {
    const payload=await getJson("/experiments?limit=100"); const experiments=payload.experiments||[];
    [els.firstExperimentSelect,els.secondExperimentSelect].forEach((select)=>{select.innerHTML="";experiments.forEach((exp)=>{const option=document.createElement("option");option.value=exp.experiment_id;option.textContent=`${exp.experiment_id} · ${exp.backend||"?"} · ${exp.suite_id||"?"}`;select.appendChild(option);});});
    if(experiments.length>1){els.firstExperimentSelect.value=experiments[1].experiment_id;els.secondExperimentSelect.value=experiments[0].experiment_id;}
  } catch { els.firstExperimentSelect.innerHTML=""; els.secondExperimentSelect.innerHTML=""; }
}

function renderDelta(el,value,lowerIsBetter=false){
  if(value==null){text(el,"—");el.className="";return;} const n=Number(value); text(el,`${n>=0?"+":""}${Math.abs(n)>=1?n.toFixed(1):n.toFixed(3)}`); const good=lowerIsBetter?n<0:n>0; const bad=lowerIsBetter?n>0:n<0; el.className=good?"delta-good":bad?"delta-bad":"";
}

async function compareSavedExperiments(){
  const first=els.firstExperimentSelect.value, second=els.secondExperimentSelect.value; if(!first||!second)return; clearError();
  try { const payload=await getJson("/experiments/compare",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({first_experiment_id:first,second_experiment_id:second})}); const d=payload.deltas_second_minus_first||{}; renderDelta(els.deltaEntityExact,d.entity_exact_match,false); renderDelta(els.deltaSpokenExact,d.spoken_form_exact_match,false); renderDelta(els.deltaCer,d.mean_character_error_rate,true); renderDelta(els.deltaRuntime,d.elapsed_ms,true); els.experimentComparison.classList.remove("hidden"); }
  catch(error){showError(error.message);}
}

els.run.addEventListener("click", runComparison);
els.clear.addEventListener("click", () => { els.input.value = ""; els.input.focus(); });
els.refreshRuns.addEventListener("click", loadRuns);
els.refreshConsole.addEventListener("click", loadProjectConsole);
els.input.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") runComparison();
});
els.candidateSelect.addEventListener("change", () => {
  populateCandidateForm(candidateRows.find(row => row.candidate_id === els.candidateSelect.value));
});
els.saveCandidate.addEventListener("click", () => saveCandidate());
els.markReviewed.addEventListener("click", () => saveCandidate("reviewed"));
els.rejectCandidate.addEventListener("click", () => saveCandidate("rejected"));
els.runExperiment.addEventListener("click", runExperiment);
els.exportImprovement.addEventListener("click", exportImprovement);
els.generateTrainingPlan.addEventListener("click", generateTrainingPlan);
els.copyTrainingCommand.addEventListener("click", copyTrainingCommand);
els.buildPackDatasetButton.addEventListener("click", buildActivePackDataset);
els.refreshExperimentHistory.addEventListener("click", loadExperimentHistory);
els.compareExperiments.addEventListener("click", compareSavedExperiments);

Promise.all([
  loadHealth(),
  loadProjectConsole(),
  loadModelStatus(),
  loadTTSStatus(),
  loadSamples(),
  loadRuns(),
  loadCandidates(),
  loadEvaluationSuites(),
  loadTrainingPlanner(),
  loadExperimentHistory(),
]).then(async () => {
  await loadTTSStatus();
  await runComparison();
});
