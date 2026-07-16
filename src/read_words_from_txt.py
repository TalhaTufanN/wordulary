import re

# Yaygın kelime türü kısaltmaları. Ders kitabı listeleri kelimeleri
# "distinguish v." / "litter n." / "dive v., n." seklinde isaretler.
#
# Bu isaret ceviriden once kelimeden ayrilir - ama ATILMAZ: DeepL'e tek basina
# gonderilen bir kelimenin anlami belirsizdir (litter -> "litre", run ->
# "çalıştır"), ve tur bilgisi elimizdeki tek anlam-ayrim sinyalidir.
# Nasil kullanildigi icin bkz. translate_words.py.
WORD_TYPE_PATTERN = re.compile(
    r'\s+(?:(?:adj|adv|n|v|prep|conj|pron|interj|art|num|aux|det|int|modal|part|phr|phr\.v|phrasal)\.?\s*,?\s*)+$',
    re.IGNORECASE,
)

# translate_words'un baglam kurabildigi turler. Digerleri (prep, conj, ...)
# ayristirilir ama baglam icin kullanilmaz - o kelimeler zaten nadiren
# cok anlamlidir.
_CONTEXT_POS = {"v", "n", "adj", "adv"}


def read_words_from_txt(file_path):
    """TXT dosyasindan (kelime, tur) ciftleri okur.

    tur: 'v' | 'n' | 'adj' | 'adv' ya da isaret yoksa/taninmiyorsa None.
    Cok turlu girdilerde ("dive v., n.") ilk tur alinir - ders kitabi
    listelerinde ilk sirada gelen genellikle baskin anlamdir.
    """
    entries = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            match = WORD_TYPE_PATTERN.search(line)
            word = WORD_TYPE_PATTERN.sub("", line).strip()
            if not word:
                continue

            entries.append((word, _first_pos(match.group(0)) if match else None))

    return entries


def _first_pos(marker):
    """'  v., n.' -> 'v'  |  ' phr.v.' -> None (baglam kurulamayan tur)"""
    first = marker.strip().split(",")[0].strip().rstrip(".").lower()
    return first if first in _CONTEXT_POS else None
