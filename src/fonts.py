import os

# Paketlenmis fontlar. Arial (Microsoft lisansli) yerine DejaVu Sans kullaniyoruz -
# acik lisansli, yeniden dagitilabilir ve Turkce karakterleri tam kapsiyor.
# Bkz. fonts/LICENSE-DejaVu.txt
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(_BASE_DIR, "fonts")

REGULAR = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
BOLD = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")


def fit_font_size(pdf, texts, max_width, start_size, min_size=6):
    """En uzun satiri max_width'e sigdiran en buyuk font boyutunu dondurur.

    Iki sutunlu duzen elle ayarlanmis milimetre degerlerine dayaniyor ve
    fpdf'in cell()'i tasan metni kirpmiyor - komsu sutunun uzerine tasiyor.
    Sabit bir boyut, ceviriler beklenenden uzun geldiginde sessizce bozulur
    (Arial ile en uzun quiz satiri 90mm'lik hucrede 88.9mm idi - sinirin
    dibinde). Boyutu icerige gore secmek bunu kokten cozuyor.
    """
    if not texts:
        return start_size

    for size in range(start_size, min_size - 1, -1):
        pdf.set_font_size(size)
        if max(pdf.get_string_width(t) for t in texts) <= max_width:
            return size
    return min_size
