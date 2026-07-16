import os
import random
import re
import shutil
import tempfile
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.create_quiz_pdf import create_pdf
from src.create_word_list_pdf import create_word_list_pdf
from src.generate_choices import generate_choices
from src.read_words_from_txt import read_words_from_txt
from src.translate_words import TranslationError, translate_words

app = FastAPI(title="TestMaker UI", description="Modern UI for the TestMaker Application")

# Uretilen PDF'lerin yazildigi dizinler. Mutlak yol - surecin nereden
# baslatildigina bagli olmamali.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIRS = {
    "words": os.path.abspath(os.environ.get("TESTMAKER_WORDS_DIR", os.path.join(BASE_DIR, "words"))),
    "quizzes": os.path.abspath(os.environ.get("TESTMAKER_QUIZZES_DIR", os.path.join(BASE_DIR, "quizzes"))),
}

# Uretilen dosya adlari icin izin verilen tek desen. Yol ayraci, '..' ve
# surucu harfi iceren hicbir sey buradan gecemez.
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9_-]+\.pdf$")

MAX_UPLOAD_BYTES = 1 * 1024 * 1024  # 1 MB
MIN_WORDS = 50  # Quiz 50 soruluk - bundan azi ile uretilemez.
MAX_WORDS = 1000  # Patolojik bir dosya bir worker'i mesgul etmesin.

os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def get_index():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


# NOT: bu endpoint bilerek `def` (async degil). Icindeki ceviri ve PDF uretimi
# senkron ve I/O-bound; `async def` olsaydi event loop'u bloklar ve tek bir
# istek tum sunucuyu durdururdu. `def` olunca FastAPI bunu threadpool'da calistirir.
@app.post("/api/process")
def process_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    # Yuklenen dosya adi kullaniciya ait - asla yol kurmakta kullanilmaz.
    # Sunucu tarafinda uretilen gecici bir ada yaziyoruz.
    temp_fd, temp_file_path = tempfile.mkstemp(suffix=".txt", prefix="testmaker_")
    os.close(temp_fd)

    try:
        _save_upload(file, temp_file_path)

        # (kelime, tur) ciftleri - tur bilgisi anlam ayrimi icin kullaniliyor.
        entries = read_words_from_txt(temp_file_path)
        if len(entries) < MIN_WORDS:
            raise HTTPException(
                status_code=400, detail=f"The file must contain at least {MIN_WORDS} words."
            )
        if len(entries) > MAX_WORDS:
            raise HTTPException(
                status_code=400, detail=f"The file must contain at most {MAX_WORDS} words."
            )

        translations = translate_words(entries)

        word_list_name = f"word_list_{uuid.uuid4().hex}.pdf"
        quiz_name = f"quiz_{uuid.uuid4().hex}.pdf"

        create_word_list_pdf(translations, file_name=word_list_name, output_dir=OUTPUT_DIRS["words"])

        test_words = random.sample(list(translations.keys()), MIN_WORDS)
        questions = {
            word: generate_choices(translations[word], list(translations.values()))
            for word in test_words
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
        raise HTTPException(status_code=502, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        # Beklenmeyen hatanin detayi disariya sizmamali - loglanir, kullaniciya
        # genel mesaj doner.
        print(f"Error processing file: {e!r}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the file.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


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
