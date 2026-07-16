import random
import tkinter as tk
from tkinter import filedialog
from src.read_words_from_txt import read_words_from_txt
from src.translate_words import TranslationError, translate_words
from src.create_word_list_pdf import create_word_list_pdf
from src.generate_choices import generate_choices
from src.create_quiz_pdf import create_pdf

def main():
    # Dosya seçme penceresi aç
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    
    file_path = filedialog.askopenfilename(
        title="TXT Dosyası Seçin",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    # Kullanıcı dosya seçmediyse (iptal butonuna bastıysa) çık
    if not file_path:
        print("Dosya seçilmedi. İşlem iptal edildi.")
        return
    
    print(f"Seçilen dosya: {file_path}")
    print(f"Txt dosyası okunuyor...")
    words = read_words_from_txt(file_path)
    print(f"Txt dosyası okundu...")
    if len(words) < 50:
        print("En az 50 kelime içeren bir dosya ekleyin.")
        return
    print(f"Kelimeler çevriliyor...")
    try:
        translations = translate_words(words)
    except TranslationError as e:
        print(f"Çeviri yapılamadı: {e}")
        return
    print(f"Kelimeler çevrildi...")
    # Kelimeler ve anlamlar için PDF oluştur
    create_word_list_pdf(translations)
    test_words = random.sample(list(translations.keys()), 50)  # 50 kelime seç
    questions = {word: generate_choices(translations[word], list(translations.values())) for word in test_words}
    create_pdf(questions)
if __name__ == "__main__":
    main()
