document.addEventListener("DOMContentLoaded", () => {
  // localStorage anahtari: kullanicinin DeepL anahtari YALNIZCA kendi
  // cihazinda, kendi istegiyle saklanir. Sunucuya sadece istek basligiyla
  // gider ve orada hicbir yere yazilmaz.
  const KEY_STORAGE = "wordulary_deepl_key";
  const LANG_STORAGE = "gwr_lang";

  const uploadZone = document.getElementById("upload-zone");
  const uploadRules = document.querySelector(".upload-rules");
  const fileInput = document.getElementById("file-input");
  const browseBtn = document.getElementById("browse-btn");

  const keySection = document.getElementById("key-section");
  const keyInput = document.getElementById("api-key");
  const keyRemember = document.getElementById("key-remember");
  const keyForget = document.getElementById("key-forget");

  const quizCountSection = document.getElementById("quiz-count-section");
  const countOptions = document.getElementById("count-options");
  const countCustom = document.getElementById("count-custom");

  const loadingState = document.getElementById("loading-state");
  const successState = document.getElementById("success-state");
  const errorState = document.getElementById("error-state");

  const downloadWordsBtn = document.getElementById("download-words");
  const downloadQuizBtn = document.getElementById("download-quiz");
  const resetBtn = document.getElementById("reset-btn");
  const retryBtn = document.getElementById("retry-btn");
  const errorMessage = document.getElementById("error-message");
  const langBtn = document.getElementById("lang-btn");

  let requireUserKey = false;

  // ── i18n ────────────────────────────────────────────────────────────────
  function t(key) {
    const lang = localStorage.getItem(LANG_STORAGE) || "tr";
    return (window.appTranslations?.[lang] ?? {})[key] ?? key;
  }

  function setLanguage(lang) {
    if (!window.appTranslations?.[lang]) return;
    localStorage.setItem(LANG_STORAGE, lang);
    document.documentElement.lang = lang;
    langBtn.textContent = lang === "tr" ? "TR" : "EN";

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const value = window.appTranslations[lang][el.dataset.i18n];
      if (value) el.innerHTML = value;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const value = window.appTranslations[lang][el.dataset.i18nPlaceholder];
      if (value) el.placeholder = value;
    });
  }

  setLanguage(localStorage.getItem(LANG_STORAGE) || "tr");
  langBtn.addEventListener("click", () => {
    setLanguage((localStorage.getItem(LANG_STORAGE) || "tr") === "tr" ? "en" : "tr");
  });

  // ── API anahtari ────────────────────────────────────────────────────────
  // Sunucu BYOK modunda mi? Degilse (self-host) alan hic gosterilmez.
  fetch("/api/config")
    .then((r) => r.json())
    .then((cfg) => {
      requireUserKey = Boolean(cfg.require_user_key);
      if (requireUserKey) {
        keySection.classList.remove("hidden");
        const saved = localStorage.getItem(KEY_STORAGE);
        if (saved) {
          keyInput.value = saved;
          keyForget.classList.remove("hidden");
        }
      }
    })
    .catch(() => {
      /* config alinamazsa alan gizli kalir; sunucu yine de 401 doner. */
    });

  keyForget.addEventListener("click", () => {
    localStorage.removeItem(KEY_STORAGE);
    keyInput.value = "";
    keyForget.classList.add("hidden");
    keyRemember.checked = false;
    showError(t("keyForgotten"));
  });

  function currentKey() {
    return keyInput.value.trim();
  }

  function persistKey() {
    if (keyRemember.checked && currentKey()) {
      localStorage.setItem(KEY_STORAGE, currentKey());
      keyForget.classList.remove("hidden");
    } else {
      localStorage.removeItem(KEY_STORAGE);
      keyForget.classList.add("hidden");
    }
  }

  // ── Quiz soru sayisi secici ───────────────────────────────────────────────
  // Secili deger "all" | "10" | "20" ... veya "custom" (o zaman input'tan okunur).
  let selectedCount = "all";

  countOptions.addEventListener("click", (e) => {
    const btn = e.target.closest(".count-btn");
    if (!btn) return;
    countOptions.querySelectorAll(".count-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    selectedCount = btn.dataset.count;
    countCustom.classList.toggle("hidden", selectedCount !== "custom");
    if (selectedCount === "custom") countCustom.focus();
  });

  function currentQuestionCount() {
    if (selectedCount !== "custom") return selectedCount;
    const n = parseInt(countCustom.value, 10);
    return Number.isFinite(n) && n > 0 ? String(n) : "all";
  }

  // ── Dosya secme / surukleme ─────────────────────────────────────────────
  browseBtn.addEventListener("click", () => fileInput.click());
  uploadZone.addEventListener("click", (e) => {
    if (e.target !== browseBtn) fileInput.click();
  });

  ["dragenter", "dragover", "dragleave", "drop"].forEach((name) => {
    uploadZone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
    });
  });
  ["dragenter", "dragover"].forEach((name) => {
    uploadZone.addEventListener(name, () => uploadZone.classList.add("dragover"));
  });
  ["dragleave", "drop"].forEach((name) => {
    uploadZone.addEventListener(name, () => uploadZone.classList.remove("dragover"));
  });

  uploadZone.addEventListener("drop", (e) => handleFiles(e.dataTransfer.files));
  fileInput.addEventListener("change", function () {
    handleFiles(this.files);
  });

  function handleFiles(files) {
    if (files.length === 0) return;
    const file = files[0];

    if (!/\.(txt|pdf|docx)$/i.test(file.name)) {
      showError(t("errNotTxt"));
      return;
    }
    if (requireUserKey && !currentKey()) {
      showError(t("errNoKey"));
      keyInput.focus();
      return;
    }
    uploadFile(file);
  }

  // ── Durum yonetimi ──────────────────────────────────────────────────────
  function showState(stateElement) {
    [uploadZone, loadingState, successState, errorState].forEach((el) =>
      el.classList.add("hidden"),
    );
    uploadRules.classList.toggle("hidden", stateElement !== uploadZone);
    quizCountSection.classList.toggle("hidden", stateElement !== uploadZone);
    keySection.classList.toggle(
      "hidden",
      !requireUserKey || stateElement !== uploadZone,
    );
    stateElement.classList.remove("hidden");
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    showState(errorState);
  }

  async function uploadFile(file) {
    persistKey();
    showState(loadingState);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("question_count", currentQuestionCount());

    // Anahtar HEADER ile gider - query string'ler sunucu ve proxy loglarina duser.
    const headers = {};
    if (currentKey()) headers["X-DeepL-Api-Key"] = currentKey();

    try {
      const response = await fetch("/api/process", {
        method: "POST",
        headers,
        body: formData,
      });
      const result = await response.json().catch(() => ({}));

      if (response.ok) {
        downloadWordsBtn.href = result.word_list_url;
        downloadQuizBtn.href = result.quiz_url;
        showState(successState);
      } else {
        showError(result.detail || t("errGeneric"));
      }
    } catch (error) {
      showError(t("errNetwork"));
      console.error(error);
    }
  }

  function resetUI() {
    fileInput.value = "";
    showState(uploadZone);
  }

  resetBtn.addEventListener("click", resetUI);
  retryBtn.addEventListener("click", resetUI);
});
