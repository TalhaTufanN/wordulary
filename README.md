<div align="center">

# TestMaker

**Turn a plain word list into a printable vocabulary sheet and a ready-to-use quiz — in one drop.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![DeepL](https://img.shields.io/badge/DeepL-API-0F2B46?logo=deepl&logoColor=white)](https://www.deepl.com/pro-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<img src="assets/HomeScreen.png" alt="TestMaker interface" width="720">

</div>

---

## What it does

English teachers spend hours doing the same three things: translating a vocabulary list, formatting it into a handout, and writing a quiz from it. TestMaker collapses all three into a single file drop.

Give it a `.txt` file with one English word per line. It returns two print-ready PDFs:

| Output | What you get |
| --- | --- |
| **Vocabulary List** | A two-column A4 handout pairing each English word with its Turkish translation, 50 words per page. |
| **Quiz** | A 50-question multiple-choice test. Questions are sampled at random from your list, and the three distractors for each question are drawn from the other translations — so the wrong answers are always plausible. |

Word-type abbreviations (`v.`, `n.`, `adj.`, `phr.v.`, and friends) are stripped automatically before translation, so you can paste a list straight out of a coursebook or the Oxford 5000 without cleaning it up first.

## How it works

```
 .txt upload  ─▶  parse & clean  ─▶  DeepL (EN→TR)  ─▶  ┬─▶  Vocabulary List PDF
                                                        └─▶  Quiz PDF (+ distractors)
```

- **Backend** — [FastAPI](https://fastapi.tiangolo.com/), serving both the API and the static frontend from one process.
- **Translation** — the official [DeepL Python client](https://github.com/DeepLcom/deepl-python), chosen over machine-translation alternatives because vocabulary-level accuracy is the whole product.
- **PDF generation** — [FPDF](https://pyfpdf.github.io/fpdf2/) with a manual two-column layout, tuned to fit exactly 50 items per page.
- **Frontend** — vanilla HTML/CSS/JS. No build step, no framework, no `node_modules`. A glassmorphic card over an animated gradient mesh.

### Project layout

```
TestMaker/
├── app.py                       # FastAPI app — routes, upload handling, static mount
├── main.py                      # Legacy Tkinter desktop entry point (superseded by app.py)
├── src/
│   ├── read_words_from_txt.py   # Parse .txt, strip word-type abbreviations
│   ├── translate_words.py       # DeepL client + retry/backoff
│   ├── create_word_list_pdf.py  # Two-column vocabulary handout
│   ├── generate_choices.py      # Pick 3 plausible distractors per question
│   └── create_quiz_pdf.py       # Two-column quiz sheet
├── static/                      # index.html, style.css, script.js
├── example_txt_files/           # Sample word lists to try
└── sources/                     # Reference material (Oxford 5000 by CEFR level)
```

## Getting started

### Requirements

- Python 3.10 or newer
- A DeepL API key — the [free tier](https://www.deepl.com/pro-api) covers 500,000 characters per month, which is thousands of word lists

### Setup

```bash
git clone https://github.com/TalhaTufanN/english-turkish-vocab-quiz.git
cd english-turkish-vocab-quiz
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
DEEPL_API_KEY="your_key_here"
```

> `.env` is git-ignored. Never commit your key.

### Run it

The startup scripts create a virtual environment, install dependencies, launch the server, and open your browser:

```bash
# Windows
start.bat

# macOS / Linux
chmod +x start.sh && ./start.sh
```

Or start the server yourself:

```bash
python -m uvicorn app:app --reload
```

Then open **<http://localhost:8000>**.

### Using it

1. Prepare a `.txt` file with one English word per line. **At least 50 words** — that's the quiz length.
2. Drop it onto the upload zone.
3. Wait for DeepL to translate. Longer lists take longer; the translator paces its requests to stay inside DeepL's rate limits.
4. Download both PDFs.

No word list handy? Try any of the files in [`example_txt_files/`](example_txt_files/).

## API

The frontend is a thin client over two endpoints. Both are documented interactively at `/docs` while the server is running.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/process` | Accepts a `.txt` upload, returns download URLs for both PDFs. |
| `GET` | `/api/download/{filename}?type=words\|quizzes` | Serves a generated PDF. |

## Roadmap

TestMaker is being prepared for a public deployment at `testmaker.gwrlabs.com`. Getting there means changing how a few things work:

- **Bring your own key** — the hosted version will ask each user for their own DeepL key, used for that request and never stored. The self-hosted `.env` flow stays exactly as it is.
- **Batch translation** — DeepL accepts a list of texts per call, so a 500-word list becomes a handful of requests instead of 500 sequential ones.
- **Hardened file handling** — sanitized filenames, upload size limits, and short-lived download tokens.
- **Bundled open fonts** — replacing the licensed Arial files with an open-licensed family.
- **Turkish interface** — TR/EN localization, matching the rest of the GWR Labs ecosystem.

## License

[MIT](LICENSE) © Talha Tufan

---

<div align="center">
<sub>Built by <a href="https://gwrlabs.com">GWR Labs</a></sub>
</div>
