// Available languages dictionary
const languages = {
  "en-GB": "English",
  "es-ES": "Spanish",
  "fr-FR": "French",
  "de-DE": "German",
  "it-IT": "Italian",
  "pt-PT": "Portuguese",
  "ru-RU": "Russian",
  "ja-JP": "Japanese",
  "zh-CN": "Chinese",
  "ar-SA": "Arabic",
  "hi-IN": "Hindi"
};

// DOM Elements
const fromLangSelect = document.getElementById("fromLang");
const toLangSelect = document.getElementById("toLang");
const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");
const translateBtn = document.getElementById("translateBtn");
const swapBtn = document.getElementById("swapBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const inputSpeakBtn = document.getElementById("inputSpeakBtn");
const outputSpeakBtn = document.getElementById("outputSpeakBtn");
const charCount = document.getElementById("charCount");
const toast = document.getElementById("toast");

// 1. Populate Language Dropdowns
function populateLanguages() {
  for (let code in languages) {
    let option1 = `<option value="${code}">${languages[code]}</option>`;
    let option2 = `<option value="${code}">${languages[code]}</option>`;
    fromLangSelect.insertAdjacentHTML("beforeend", option1);
    toLangSelect.insertAdjacentHTML("beforeend", option2);
  }
  // Set default selections
  fromLangSelect.value = "en-GB";
  toLangSelect.value = "es-ES";
}

// 2. Fetch Translation from API
async function translateText() {
  const text = inputText.value.trim();
  const from = fromLangSelect.value;
  const to = toLangSelect.value;

  if (!text) {
    outputText.value = "";
    return;
  }

  outputText.placeholder = "Translating...";
  
  // MyMemory Translation API Endpoint
  const apiUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${from}|${to}`;

  try {
    const response = await fetch(apiUrl);
    const data = await response.json();
    
    if (data.responseData) {
      outputText.value = data.responseData.translatedText;
    } else {
      outputText.value = "Translation failed. Try again.";
    }
  } catch (error) {
    console.error("Error fetching translation:", error);
    outputText.value = "Error: Could not fetch translation.";
  }
}

// 3. Optional Feature: Swap Languages & Text
function swapLanguages() {
  let tempLang = fromLangSelect.value;
  fromLangSelect.value = toLangSelect.value;
  toLangSelect.value = tempLang;

  let tempText = inputText.value;
  inputText.value = outputText.value;
  outputText.value = tempText;

  updateCharCount();
}

// 4. Optional Feature: Text-to-Speech
function speakText(text, langCode) {
  if (!text) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = langCode;
  window.speechSynthesis.speak(utterance);
}

// 5. Optional Feature: Copy to Clipboard with Toast Notification
function copyToClipboard() {
  if (!outputText.value) return;
  navigator.clipboard.writeText(outputText.value).then(() => {
    toast.classList.remove("opacity-0");
    setTimeout(() => {
      toast.classList.add("opacity-0");
    }, 2000);
  });
}

// 6. Helper: Character Counter
function updateCharCount() {
  charCount.textContent = `${inputText.value.length} / 5000`;
}

// Event Listeners
document.addEventListener("DOMContentLoaded", populateLanguages);
translateBtn.addEventListener("click", translateText);

swapBtn.addEventListener("click", swapLanguages);

clearBtn.addEventListener("click", () => {
  inputText.value = "";
  outputText.value = "";
  updateCharCount();
});

inputText.addEventListener("input", updateCharCount);

copyBtn.addEventListener("click", copyToClipboard);

inputSpeakBtn.addEventListener("click", () => {
  speakText(inputText.value, fromLangSelect.value);
});

outputSpeakBtn.addEventListener("click", () => {
  speakText(outputText.value, toLangSelect.value);
});