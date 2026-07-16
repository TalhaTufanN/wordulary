import os
import time

import deepl

try:
    from dotenv import load_dotenv

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(base_dir, ".env"))
except ImportError:
    pass

# DeepL tek istekte 50 metne kadar kabul ediyor. Listedeki her metin
# birbirinden bagimsiz cevrilir, yani batch'lemek ciktiyi degistirmez -
# sadece 500 HTTP istegini ~10'a indirir.
BATCH_SIZE = 50

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2

# Tek tek istek atilacak kelime sayisi ust siniri. Her frame istegi ~0.6sn
# suruyor ve Cloudflare 100sn'de baglantiyi kesiyor; bu sinir en kotu durumda
# ~30sn'de kalmamizi garanti eder. Asilirsa kalanlar batch sonucuyla birakilir.
MAX_FRAME_FALLBACKS = 50

# ── Baglam (context) stratejisi ───────────────────────────────────────────
# DeepL'in `context` parametresi cevrilmez ve faturalandirilmaz, ama anlami
# etkiler. Tek kelime hicbir baglam olmadan gonderilirse DeepL en yaygin
# anlami secer ve sik sik yanilir: litter -> "litre", logo -> "sonra".
#
# Olculen dogruluk (18 cok anlamli kelime, 2026-07-17):
#   ciplak 7/18 · pattern 9/18 · meta 11/18 · fewshot 11/18 · frame 14/15
#
# `context` istek basina TEK bir parametre - kelime basina degil. Bu yuzden
# kelimeyi cumleye gomen "frame" yontemi (en dogru olan) batch'lenemez:
# 500 kelime = 500 istek = ~309sn, hem Cloudflare'in 100sn sinirini asar hem
# DeepL 429 doner. Cozum: POS'a gore grupla, her grubu kendi baglami ile tek
# batch'te cevir. Grup baglami kelimeye ozel olmadigi icin batch bozulmaz.
CONTEXT_BY_POS = {
    "v": "English-Turkish vocabulary list. Verbs: arrive → varmak, decide → karar vermek, explain → açıklamak.",
    "n": "English-Turkish vocabulary list. Nouns: teacher → öğretmen, bridge → köprü, silence → sessizlik.",
    "adj": "English-Turkish vocabulary list. Adjectives: happy → mutlu, heavy → ağır, ancient → antik.",
    "adv": "English-Turkish vocabulary list. Adverbs: quickly → hızlıca, rarely → nadiren, clearly → açıkça.",
}

# Grup baglami bazen kelimeyi hic cevirmeden geri dondurur (auto -> "auto").
# Bu durumda kelimeyi dogru turde kullanan bir ornek cumleye dusuyoruz -
# en dogru yontem, ama kelime basina bir istek gerektirdigi icin sadece
# bu birkac vaka icin kullaniliyor.
FRAME_BY_POS = {
    "v": "They decided to {word} it yesterday.",
    "n": "I saw the {word} over there.",
    "adj": "It was a very {word} day.",
    "adv": "He did it very {word}.",
}


class TranslationError(Exception):
    """Kullaniciya gosterilebilecek, uzerine islem yapilabilir ceviri hatasi."""


def _resolve_api_key(api_key=None):
    key = api_key or os.getenv("DEEPL_API_KEY")
    if not key:
        raise TranslationError(
            "DeepL API anahtari bulunamadi. Ortam degiskenlerine ekleyin veya "
            "proje kokunde DEEPL_API_KEY=anahtariniz iceren bir .env dosyasi olusturun."
        )
    return key


def _normalize(entries):
    """(kelime, tur) ciftlerine cevirir. Duz string listesi de kabul edilir."""
    normalized = []
    for entry in entries:
        if isinstance(entry, (tuple, list)):
            word, pos = entry[0], entry[1]
        else:
            word, pos = entry, None
        normalized.append((word, pos if pos in CONTEXT_BY_POS else None))
    return normalized


def translate_words(entries, api_key=None):
    """Ingilizce kelimeleri Turkceye cevirir; {kelime: ceviri} dondurur.

    entries: (kelime, tur) ciftleri veya duz kelime listesi. Tur bilgisi
    (v/n/adj/adv) varsa anlam ayrimi icin kullanilir; yoksa kelime baglamsiz
    cevrilir.

    api_key verilmezse DEEPL_API_KEY ortam degiskenine duser (self-host / lokal
    gelistirme icin). Anahtar istek basina verilebilsin diye Translator burada
    kuruluyor - modul seviyesinde tutulmuyor.
    """
    if not entries:
        return {}

    pairs = _normalize(entries)
    translator = deepl.Translator(_resolve_api_key(api_key))

    # Ayni baglami paylasan kelimeleri grupla - her grup kendi icinde
    # batch'lenir, yani toplam istek sayisi ~(grup sayisi x kelime/50) olur.
    groups = {}
    for word, pos in pairs:
        groups.setdefault(pos, []).append(word)

    translations = {}
    done = 0
    total = len(pairs)

    for pos, words in groups.items():
        context = CONTEXT_BY_POS.get(pos)
        for start in range(0, len(words), BATCH_SIZE):
            batch = words[start : start + BATCH_SIZE]
            for word, translated in zip(batch, _translate_batch(translator, batch, context)):
                translations[word] = translated
            done += len(batch)
            print(f"  {done}/{total} kelime çevrildi...")

    _repair_untranslated(translator, pairs, translations)
    return translations


def _repair_untranslated(translator, pairs, translations):
    """Grup baglaminin cevirmeden geri dondurdugu kelimeleri frame ile duzeltir."""
    suspects = [
        (word, pos)
        for word, pos in pairs
        if pos and translations.get(word, "").strip().lower() == word.strip().lower()
    ]
    if not suspects:
        return

    repairing = suspects[:MAX_FRAME_FALLBACKS]
    if len(suspects) > MAX_FRAME_FALLBACKS:
        # Sessizce kirpma - kullanici neyin duzeltilmedigini bilmeli.
        print(
            f"  UYARI: {len(suspects)} kelime çevrilmemiş görünüyor, "
            f"yalnızca ilk {MAX_FRAME_FALLBACKS} tanesi yeniden denenecek."
        )

    print(f"  {len(repairing)} kelime bağlam cümlesiyle yeniden çevriliyor...")
    for word, pos in repairing:
        frame = FRAME_BY_POS[pos].format(word=word)
        try:
            result = _translate_batch(translator, [word], frame)[0]
        except TranslationError:
            # Duzeltme en iyi cabadir - basarisiz olursa batch sonucu kalir.
            continue
        if result.strip().lower() != word.strip().lower():
            translations[word] = result


def _translate_batch(translator, batch, context=None):
    """Tek bir batch'i cevirir. Kalici hatalarda TranslationError firlatir."""
    kwargs = {"target_lang": "TR"}
    if context:
        kwargs["context"] = context

    for attempt in range(MAX_RETRIES):
        try:
            return [r.text for r in translator.translate_text(batch, **kwargs)]

        # Anahtar hatalari retry'lanmaz - beklemek sonucu degistirmez ve
        # kullanicinin duzeltebilecegi somut bir durumdur.
        except deepl.exceptions.AuthorizationException:
            raise TranslationError("DeepL API anahtarı geçersiz. Anahtarınızı kontrol edin.")
        except deepl.exceptions.QuotaExceededException:
            raise TranslationError(
                "DeepL API anahtarınızın karakter kotası dolmuş. "
                "Kotanız yenilenene kadar çeviri yapılamaz."
            )

        except deepl.exceptions.TooManyRequestsException:
            if attempt == MAX_RETRIES - 1:
                raise TranslationError(
                    "DeepL çok fazla istek aldığı için çeviriyi reddetti. "
                    "Lütfen biraz sonra tekrar deneyin."
                )
            wait = RETRY_BASE_DELAY * (2**attempt)
            print(f"  Çok fazla istek! {wait} saniye bekleniyor... (Deneme {attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)

        except deepl.exceptions.DeepLException as e:
            if attempt == MAX_RETRIES - 1:
                raise TranslationError(f"DeepL çeviri hatası: {e}")
            wait = RETRY_BASE_DELAY * (2**attempt)
            print(f"  Hata oluştu: {e}. {wait} saniye bekleniyor... (Deneme {attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)

    raise TranslationError("Çeviri başarısız oldu.")
