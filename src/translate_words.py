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
# birbirinden bagimsiz cevrilir (ortak baglam kullanilmaz), yani batch'lemek
# ciktiyi degistirmez - sadece 500 HTTP istegini ~10'a indirir.
BATCH_SIZE = 50

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2


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


def translate_words(words, api_key=None):
    """Ingilizce kelimeleri Turkceye cevirir; {kelime: ceviri} dondurur.

    api_key verilmezse DEEPL_API_KEY ortam degiskenine duser (self-host / lokal
    gelistirme icin). Anahtar istek basina verilebilsin diye Translator burada
    kuruluyor - modul seviyesinde tutulmuyor.
    """
    if not words:
        return {}

    translator = deepl.Translator(_resolve_api_key(api_key))
    translations = {}
    total = len(words)

    for start in range(0, total, BATCH_SIZE):
        batch = words[start : start + BATCH_SIZE]
        results = _translate_batch(translator, batch)
        for word, translated in zip(batch, results):
            translations[word] = translated
        print(f"  {min(start + BATCH_SIZE, total)}/{total} kelime çevrildi...")

    return translations


def _translate_batch(translator, batch):
    """Tek bir batch'i cevirir. Kalici hatalarda TranslationError firlatir."""
    for attempt in range(MAX_RETRIES):
        try:
            results = translator.translate_text(batch, target_lang="TR")
            return [r.text for r in results]

        # Anahtar hatalari retry'lanmaz - beklemek sonucu degistirmez ve
        # kullanicinin duzeltebilecegi somut bir durumdur.
        except deepl.exceptions.AuthorizationException:
            raise TranslationError(
                "DeepL API anahtari geçersiz. Anahtarınızı kontrol edin."
            )
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
