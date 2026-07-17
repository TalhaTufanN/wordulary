import random


# Şıklar oluştur (doğru cevap + en fazla 3 yanlış seçenek)
def generate_choices(correct_word, all_words, num_choices=4):
    # Yanlış havuzu BENZERSIZ olmalı: iki İngilizce kelimenin çevirisi aynı
    # olabilir (örn. "run"/"jog" -> "koşmak"); aksi halde bir şık iki kez çıkar.
    pool = list({w for w in all_words if w != correct_word})

    # Havuz 3'ten azsa (çok küçük listeler) eldeki kadarını kullan - çökme yok,
    # o soru sadece daha az şıkla çıkar.
    wrong_count = min(num_choices - 1, len(pool))
    choices = [correct_word] + random.sample(pool, wrong_count)
    random.shuffle(choices)
    return choices
