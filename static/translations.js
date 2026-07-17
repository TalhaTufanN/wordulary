const translations = {
  tr: {
    // Header
    heroTitle: "Wordulary",
    heroDesc:
      "İngilizce kelime listenizi, Türkçe çevirili kelime kartlarına ve çoktan seçmeli teste anında dönüştürün.",

    // API key
    keyLabel: "DeepL API Anahtarınız",
    keyHint:
      'Çeviri için kendi DeepL anahtarınızı kullanırsınız. <a href="https://www.deepl.com/pro-api" target="_blank" rel="noopener">Ücretsiz anahtar alın</a> — ayda 500.000 karakter, binlerce kelime listesine yeter.',
    keyPlaceholder: "Örn: 12345678-abcd-...:fx",
    keyRemember: "Bu cihazda hatırla",
    keyPrivacy:
      "Anahtarınız yalnızca bu isteğin çevirisi için kullanılır. Sunucumuzda saklanmaz, kaydedilmez, loglanmaz.",
    keyForget: "Kayıtlı anahtarı sil",
    keyForgotten: "Anahtar bu cihazdan silindi.",

    // Upload
    uploadTitle: ".txt dosyanızı yükleyin",
    uploadDesc: "Dosyanızı buraya sürükleyin veya seçmek için tıklayın.",
    uploadBtn: "Dosya Seç",
    uploadRules:
      "Her satırda bir İngilizce kelime. Kelime türü işaretleri (<code>v.</code>, <code>n.</code>, <code>adj.</code>) çeviriyi belirgin şekilde iyileştirir.",

    // States
    loadingTitle: "Kelimeleriniz işleniyor...",
    loadingDesc: "DeepL çeviriyi yaparken bir saniye...",
    successTitle: "Hazır!",
    successDesc: "Kelime listeniz ve testiniz indirilmeye hazır.",
    downloadWords: "Kelime Listesini İndir",
    downloadQuiz: "Testi İndir",
    resetBtn: "Yeni Bir Tane Oluştur",
    errorTitle: "Bir şeyler ters gitti",
    errorDesc: "Dosyanız işlenemedi.",
    retryBtn: "Tekrar Dene",

    // Client-side errors
    errNotTxt: "Lütfen geçerli bir .txt dosyası yükleyin.",
    errNoKey: "Devam etmek için DeepL API anahtarınızı girin.",
    errNetwork: "Ağ hatası. Bağlantınızı kontrol edip tekrar deneyin.",
    errGeneric: "Dosya işlenirken bir hata oluştu.",

    // Footer
    footerPrivacy: "Gizlilik",
    footerSource: "Kaynak Kodu",
  },

  en: {
    heroTitle: "Wordulary",
    heroDesc:
      "Turn your English word list into a Turkish vocabulary handout and a multiple-choice quiz, instantly.",

    keyLabel: "Your DeepL API Key",
    keyHint:
      'Translation runs on your own DeepL key. <a href="https://www.deepl.com/pro-api" target="_blank" rel="noopener">Get a free one</a> — 500,000 characters a month covers thousands of word lists.',
    keyPlaceholder: "e.g. 12345678-abcd-...:fx",
    keyRemember: "Remember on this device",
    keyPrivacy:
      "Your key is used only to translate this request. We never store, save, or log it.",
    keyForget: "Forget saved key",
    keyForgotten: "Key removed from this device.",

    uploadTitle: "Upload your .txt file",
    uploadDesc: "Drag & drop your text file here, or click to browse.",
    uploadBtn: "Browse Files",
    uploadRules:
      "One English word per line. Part-of-speech markers (<code>v.</code>, <code>n.</code>, <code>adj.</code>) noticeably improve translation quality.",

    loadingTitle: "Processing your vocabulary...",
    loadingDesc: "One moment while DeepL translates your words...",
    successTitle: "Generation complete!",
    successDesc: "Your vocabulary list and quiz are ready for download.",
    downloadWords: "Download Word List",
    downloadQuiz: "Download Quiz",
    resetBtn: "Create Another",
    errorTitle: "Something went wrong",
    errorDesc: "We couldn't process your file.",
    retryBtn: "Try Again",

    errNotTxt: "Please upload a valid .txt file.",
    errNoKey: "Enter your DeepL API key to continue.",
    errNetwork: "Network error. Check your connection and try again.",
    errGeneric: "An error occurred while processing the file.",

    footerPrivacy: "Privacy",
    footerSource: "Source",
  },
};

// Expose to window
window.appTranslations = translations;
