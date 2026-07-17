const translations = {
  tr: {
    // Header
    heroTitle: "Wordulary",
    heroDesc:
      "İngilizce kelime listenizi, Türkçe çevirili kelime kartlarına ve çoktan seçmeli teste anında dönüştürün.",

    // API key
    keyLabel: "DeepL API Anahtarınız",
    keyHint:
      'Çeviri için kendi DeepL anahtarınızı kullanırsınız. <a href="https://www.deepl.com/pro-api" target="_blank" rel="noopener">Ücretsiz anahtar alın</a>, ayda 500.000 karakter, binlerce kelime listesine yeter.',
    keyPlaceholder: "Örn: 12345678-abcd-...:fx",
    keyRemember: "Bu cihazda hatırla",
    keyPrivacy:
      "Anahtarınız yalnızca bu isteğin çevirisi için kullanılır. Sunucumuzda saklanmaz, kaydedilmez, loglanmaz.",
    keyForget: "Kayıtlı anahtarı sil",
    keyForgotten: "Anahtar bu cihazdan silindi.",

    // Quiz question count
    countLabel: "Quiz soru sayısı",
    countAll: "Tümü",
    countCustom: "Özel",
    countCustomPlaceholder: "Kaç soru?",

    // Upload
    uploadTitle: "Kelime listenizi yükleyin",
    uploadDesc: "Dosyanızı buraya sürükleyin veya seçmek için tıklayın.",
    uploadBtn: "Dosya Seç",
    uploadRules:
      ".txt, PDF veya Word (.docx). Her satırda bir İngilizce kelime; kelime türü işaretleri (<code>v.</code>, <code>n.</code>, <code>adj.</code>) çeviriyi belirgin şekilde iyileştirir.",

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
    errNotTxt: "Lütfen .txt, PDF veya Word (.docx) dosyası yükleyin.",
    errNoKey: "Devam etmek için DeepL API anahtarınızı girin.",
    errNetwork: "Ağ hatası. Bağlantınızı kontrol edip tekrar deneyin.",
    errGeneric: "Dosya işlenirken bir hata oluştu.",

    // How it works
    howTitle: "Nasıl çalışır?",
    how1Title: "Listeni yükle",
    how1Desc:
      "Her satırda bir İngilizce kelime olan bir .txt, PDF veya Word dosyası. Ders kitabı listesini olduğu gibi atabilirsin.",
    how2Title: "Türkçeye çevrilsin",
    how2Desc:
      "Kelime türü işaretleri (v., n., adj.) sayesinde doğru anlam seçilir. Bu yüzden çeviriler isabetli olur.",
    how3Title: "İki PDF indir",
    how3Desc:
      "Baskıya hazır bir kelime listesi ve çoktan seçmeli bir test. Uzunluğu sen seçersin.",

    // Example
    exTitle: "Örnek",
    exSub: "Küçük bir liste ne veriyor, gör:",
    exInLabel: "Yüklediğin liste",
    exWordsLabel: "Kelime listesi PDF",
    exQuizLabel: "Test PDF",
    exNote:
      'Not: bağlamsız çeviride "litter" çoğu araçta "litre" olur. Kelime türü işaretiyle Wordulary doğru anlamı seçer.',
    exDownload: "Örnek listeyi indir (.txt)",

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
      'Translation runs on your own DeepL key. <a href="https://www.deepl.com/pro-api" target="_blank" rel="noopener">Get a free one</a>, 500,000 characters a month covers thousands of word lists.',
    keyPlaceholder: "e.g. 12345678-abcd-...:fx",
    keyRemember: "Remember on this device",
    keyPrivacy:
      "Your key is used only to translate this request. We never store, save, or log it.",
    keyForget: "Forget saved key",
    keyForgotten: "Key removed from this device.",

    // Quiz question count
    countLabel: "Quiz length",
    countAll: "All",
    countCustom: "Custom",
    countCustomPlaceholder: "How many?",

    uploadTitle: "Upload your word list",
    uploadDesc: "Drag & drop your file here, or click to browse.",
    uploadBtn: "Browse Files",
    uploadRules:
      ".txt, PDF, or Word (.docx). One English word per line; part-of-speech markers (<code>v.</code>, <code>n.</code>, <code>adj.</code>) noticeably improve translation quality.",

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

    errNotTxt: "Please upload a .txt, PDF, or Word (.docx) file.",
    errNoKey: "Enter your DeepL API key to continue.",
    errNetwork: "Network error. Check your connection and try again.",
    errGeneric: "An error occurred while processing the file.",

    // How it works
    howTitle: "How it works",
    how1Title: "Upload your list",
    how1Desc:
      "A .txt, PDF, or Word file with one English word per line. Drop in a coursebook list as-is.",
    how2Title: "Get it translated",
    how2Desc:
      "Part-of-speech markers (v., n., adj.) pick the right sense, so the translations land accurately.",
    how3Title: "Download two PDFs",
    how3Desc:
      "A print-ready vocabulary list and a multiple-choice quiz. You choose the length.",

    // Example
    exTitle: "Example",
    exSub: "See what a small list gives you:",
    exInLabel: "Your list",
    exWordsLabel: "Vocabulary PDF",
    exQuizLabel: "Quiz PDF",
    exNote:
      'Note: without context, "litter" comes out as "litre" in most tools. With the part-of-speech marker, Wordulary picks the right meaning.',
    exDownload: "Download a sample list (.txt)",

    footerPrivacy: "Privacy",
    footerSource: "Source",
  },
};

// Expose to window
window.appTranslations = translations;
