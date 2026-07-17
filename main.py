import tkinter as tk
from tkinter import filedialog
from src.extract_words import extract_entries
from src.translate_words import TranslationError, translate_words
from src.create_word_list_pdf import create_word_list_pdf
from src.generate_choices import generate_choices
from src.create_quiz_pdf import create_pdf

MIN_WORDS = 4  # coktan secmeli icin: 1 dogru + 3 celdirici


def _dedupe(entries):
    """Tekrarlari at (buyuk/kucuk harf duyarsiz), sirayi koru."""
    seen, result = set(), []
    for word, pos in entries:
        key = word.strip().casefold()
        if key and key not in seen:
            seen.add(key)
            result.append((word, pos))
    return result

def main():
    # Dosya seçme penceresi aç
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    
    file_path = filedialog.askopenfilename(
        title="Kelime Listesi Seçin",
        filetypes=[("Desteklenen", "*.txt *.pdf *.docx"), ("All files", "*.*")]
    )

    # Kullanıcı dosya seçmediyse (iptal butonuna bastıysa) çık
    if not file_path:
        print("Dosya seçilmedi. İşlem iptal edildi.")
        return

    print(f"Seçilen dosya: {file_path}")
    print(f"Dosya okunuyor...")
    entries = _dedupe(extract_entries(file_path))
    print(f"Dosya okundu...")
    if len(entries) < MIN_WORDS:
        print(f"En az {MIN_WORDS} farklı kelime içeren bir dosya ekleyin.")
        return
    print(f"Kelimeler çevriliyor...")
    try:
        translations = translate_words(entries)
    except TranslationError as e:
        print(f"Çeviri yapılamadı: {e}")
        return
    print(f"Kelimeler çevrildi...")
    # Kelimeler ve anlamlar için PDF oluştur
    create_word_list_pdf(translations)
    # Quiz her kelime için bir soru
    all_meanings = list(translations.values())
    questions = {word: generate_choices(meaning, all_meanings) for word, meaning in translations.items()}
    create_pdf(questions)
if __name__ == "__main__":
    main()
