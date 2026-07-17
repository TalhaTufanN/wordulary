import os
import random
import re
import tempfile
import uuid

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.create_quiz_pdf import create_pdf
from src.create_word_list_pdf import create_word_list_pdf
from src.generate_choices import generate_choices
from src.read_words_from_txt import read_words_from_txt
from src.translate_words import TranslationError, translate_words

app = FastAPI(title="Wordulary UI", description="Modern UI for the Wordulary Application")

# Uretilen PDF'lerin yazildigi dizinler. Mutlak yol - surecin nereden
# baslatildigina bagli olmamali.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIRS = {
    "words": os.path.abspath(os.environ.get("WORDULARY_WORDS_DIR", os.path.join(BASE_DIR, "words"))),
    "quizzes": os.path.abspath(os.environ.get("WORDULARY_QUIZZES_DIR", os.path.join(BASE_DIR, "quizzes"))),
}

# Uretilen dosya adlari icin izin verilen tek desen. Yol ayraci, '..' ve
# surucu harfi iceren hicbir sey buradan gecemez.
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9_-]+\.pdf$")

MAX_UPLOAD_BYTES = 1 * 1024 * 1024  # 1 MB
# Coktan secmeli bir soru icin en az 4 benzersiz kelime gerekir: 1 dogru cevap
# + 3 celdirici. Liste bundan uzun olsun yeter - 50 zorunlu degil.
MIN_WORDS = 4
MAX_WORDS = 1000  # Patolojik bir dosya bir worker'i mesgul etmesin.

# BYOK (bring your own key): herkese acik kurulumda her kullanici kendi DeepL
# anahtarini getirir. Boylece kota, maliyet ve kotuye kullanim yuzeyi ortadan
# kalkar - hesap, rate limit veya bot korumasi gerekmez.
#
# Kapaliyken (varsayilan) sunucu .env'deki anahtara duser; self-host ve lokal
# gelistirme boylece hic degismeden calisir.
REQUIRE_USER_KEY = os.environ.get("WORDULARY_REQUIRE_USER_KEY", "").lower() in ("1", "true", "yes")

os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    """Frontend'in anahtar alanini gosterip gostermeyecegini belirler."""
    return {"require_user_key": REQUIRE_USER_KEY}


@app.get("/", response_class=HTMLResponse)
async def get_index():
    return _render_html("index.html")


@app.get("/privacy/", response_class=HTMLResponse)
@app.get("/privacy", response_class=HTMLResponse)
async def get_privacy():
    return _render_html("privacy.html")


def _render_html(name):
    """HTML'i döndürür, /static/ referanslarına dosya değişince değişen bir
    versiyon parametresi ekler.

    Cloudflare statik .js/.css dosyalarini 4 saat cache'ler ama HTML sayfalarini
    (DYNAMIC) cache'lemez. Yani HTML her zaman taze gelir; ona gomulu linke dosya
    mtime'ini eklersek, bir asset degistiginde URL degisir ve Cloudflare taze
    kopyayi ceker. Deploy sonrasi elle cache temizleme gerekmez.
    """
    html = open(os.path.join(BASE_DIR, "static", name), encoding="utf-8").read()

    def versioned(match):
        asset = match.group(1)
        try:
            mtime = int(os.path.getmtime(os.path.join(BASE_DIR, "static", asset)))
        except OSError:
            return match.group(0)
        return f"/static/{asset}?v={mtime}"

    html = re.sub(r"/static/([A-Za-z0-9_.-]+)", versioned, html)
    return HTMLResponse(html)


# NOT: bu endpoint bilerek `def` (async degil). Icindeki ceviri ve PDF uretimi
# senkron ve I/O-bound; `async def` olsaydi event loop'u bloklar ve tek bir
# istek tum sunucuyu durdururdu. `def` olunca FastAPI bunu threadpool'da calistirir.
#
# Anahtar HEADER ile alinir, query string ile degil: query string'ler sunucu ve
# proxy loglarina duser. Bu degisken asla loglanmaz, diske yazilmaz, cache'lenmez -
# istekle gelir, istekle olur.
@app.post("/api/process")
def process_file(
    file: UploadFile = File(...),
    x_deepl_api_key: str | None = Header(default=None),
    question_count: str = Form(default="all"),
):
    user_key = (x_deepl_api_key or "").strip() or None

    if REQUIRE_USER_KEY and not user_key:
        raise HTTPException(status_code=401, detail="A DeepL API key is required.")

    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    # Yuklenen dosya adi kullaniciya ait - asla yol kurmakta kullanilmaz.
    # Sunucu tarafinda uretilen gecici bir ada yaziyoruz.
    temp_fd, temp_file_path = tempfile.mkstemp(suffix=".txt", prefix="wordulary_")
    os.close(temp_fd)

    try:
        _save_upload(file, temp_file_path)

        # (kelime, tur) ciftleri - tur bilgisi anlam ayrimi icin kullaniliyor.
        entries = read_words_from_txt(temp_file_path)

        # Tekrarlari at (buyuk/kucuk harf ve bosluk duyarsiz), ilk gorulme
        # sirasini koru. Kelime sayisi kontrolu BENZERSIZ kelimeler uzerinden
        # yapilmali: aksi halde "55 satir ama 45 benzersiz" bir dosya kontrolu
        # gecer, sonra quiz uretiminde patlardi.
        entries = _dedupe(entries)

        if len(entries) < MIN_WORDS:
            raise HTTPException(
                status_code=400,
                detail=f"The file must contain at least {MIN_WORDS} distinct words.",
            )
        if len(entries) > MAX_WORDS:
            raise HTTPException(
                status_code=400, detail=f"The file must contain at most {MAX_WORDS} words."
            )

        translations = translate_words(entries, api_key=user_key)

        word_list_name = f"word_list_{uuid.uuid4().hex}.pdf"
        quiz_name = f"quiz_{uuid.uuid4().hex}.pdf"

        # Kelime listesi PDF'i HER ZAMAN tum kelimeleri icerir - ogretmen
        # hepsini ogretir; quiz uzunlugu ayri bir tercih.
        create_word_list_pdf(translations, file_name=word_list_name, output_dir=OUTPUT_DIRS["words"])

        # Quiz soru sayisi kullanici tercihine gore. Celdiriciler yine TUM
        # cevirilerden secilir (havuz genis olsun), quiz alt kume olsa bile.
        all_meanings = list(translations.values())
        count = _parse_question_count(question_count, len(translations))
        quiz_items = list(translations.items())
        if count < len(quiz_items):
            quiz_items = random.sample(quiz_items, count)
        questions = {
            word: generate_choices(meaning, all_meanings) for word, meaning in quiz_items
        }
        create_pdf(questions, file_name=quiz_name, output_dir=OUTPUT_DIRS["quizzes"])

        return {
            "success": True,
            "word_list_url": f"/api/download/{word_list_name}?type=words",
            "quiz_url": f"/api/download/{quiz_name}?type=quizzes",
            "message": "Files processed successfully!",
        }

    except TranslationError as e:
        # Kullanicinin uzerine islem yapabilecegi hatalar (gecersiz anahtar,
        # dolu kota) oldugu gibi iletilir.
        raise HTTPException(status_code=502, detail=_scrub(str(e), user_key))
    except HTTPException:
        raise
    except Exception as e:
        # Beklenmeyen hatanin detayi disariya sizmamali - loglanir, kullaniciya
        # genel mesaj doner. Log'a giden metin de anahtardan arindirilir:
        # kullanicinin anahtari asla diske yazilmamali.
        print(f"Error processing file: {_scrub(repr(e), user_key)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the file.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def _parse_question_count(raw, available):
    """Quiz soru sayisi tercihini cozer. 'all'/bos/gecersiz -> tum kelimeler.
    Sayi ise 1 ile mevcut kelime sayisi arasina kirpilir (fazla istenirse
    kelime sayisina duser)."""
    raw = (raw or "").strip().lower()
    if raw in ("", "all", "tümü", "tumu", "hepsi"):
        return available
    try:
        n = int(raw)
    except ValueError:
        return available
    return max(1, min(n, available))


def _dedupe(entries):
    """Tekrar eden kelimeleri atar (buyuk/kucuk harf ve bosluk duyarsiz),
    ilk gorulme sirasini korur. entries: (kelime, tur) ciftleri."""
    seen = set()
    result = []
    for word, pos in entries:
        key = word.strip().casefold()
        if key and key not in seen:
            seen.add(key)
            result.append((word, pos))
    return result


def _scrub(text: str, secret: str | None) -> str:
    """Kullanicinin API anahtarini metinden temizler.

    Ucuncu parti kutuphanelerin istisna mesajlarina neyi koydugunu garanti
    edemeyiz. Bu, anahtarin log'a veya HTTP cevabina sizmamasi icin son savunma.
    """
    if secret and len(secret) >= 8 and secret in text:
        return text.replace(secret, "***")
    return text


def _save_upload(file: UploadFile, destination: str):
    """Yuklenen dosyayi boyut sinirini asmadan diske yazar."""
    written = 0
    with open(destination, "wb") as buffer:
        while chunk := file.file.read(64 * 1024):
            written += len(chunk)
            if written > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"File is too large (limit: {MAX_UPLOAD_BYTES // 1024 // 1024} MB).",
                )
            buffer.write(chunk)


@app.get("/api/download/{filename}")
async def download_file(filename: str, type: str):
    output_dir = OUTPUT_DIRS.get(type)
    if output_dir is None:
        raise HTTPException(status_code=400, detail="Invalid file type requested")

    if not SAFE_FILENAME.match(filename):
        raise HTTPException(status_code=400, detail="Invalid file name")

    file_path = os.path.abspath(os.path.join(output_dir, filename))

    # Ikinci savunma hatti: desen kontrolunu bir sekilde gecen her sey burada
    # durur. Cozulmis yol hedef dizinin disina cikamaz.
    if os.path.commonpath([file_path, output_dir]) != output_dir:
        raise HTTPException(status_code=400, detail="Invalid file name")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="application/pdf", filename=filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
