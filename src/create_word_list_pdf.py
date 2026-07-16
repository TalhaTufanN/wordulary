import os
from datetime import datetime
from fpdf import FPDF

# Kelimeler ve anlamlar için PDF oluşturma fonksiyonu
def create_word_list_pdf(translations, file_name=None, output_dir=None):
    # Klasör oluştur. Yol mutlak - sürecin nereden başlatıldığına bağlı olmamalı.
    if output_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "words")
    os.makedirs(output_dir, exist_ok=True)

    # Benzersiz dosya adı oluştur
    if file_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"word_list_{timestamp}.pdf"

    file_path = os.path.join(output_dir, file_name)
    
    # Font dosya yolları
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path = os.path.join(base_dir, "arial.ttf")
    
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False, margin=10)  # Otomatik sayfa kırılmasını kapat
    
    # Arial Font ekle
    pdf.add_font("Arial", "", font_path, uni=True)
    pdf.set_font("Arial", size=12)
    
    # Sol ve sağ sütun başlangıç noktaları
    left_margin = 10
    right_margin = 105  # Sağ sütun için
    y_offset = 20  # Başlangıç yüksekliği
    line_height = 8  # Her kelime ve anlam arasındaki mesafe
    words_per_page = 50  # Her sayfada 50 kelime (25 sol + 25 sağ)
    words_per_column = 25  # Her sütunda 25 kelime

    # Kelimeleri iki sütunda yazdırmak için düzen
    for i, (word, translated) in enumerate(translations.items(), 1):
        # Hangi sayfada olduğunu hesapla (0'dan başlar)
        page_number = (i - 1) // words_per_page
        # Sayfa içindeki pozisyonu hesapla (0-49)
        position_in_page = (i - 1) % words_per_page
        
        # Her 50 kelimede bir yeni sayfa ekle
        if position_in_page == 0:
            pdf.add_page()
            # Başlık Ekleme
            pdf.set_xy(10, 5)
            pdf.cell(190, 10, "Vocabulary List", ln=True, align="C")
        
        # Sol sütun (0-24) veya sağ sütun (25-49)
        if position_in_page < words_per_column:
            # Sol sütun
            x_position = left_margin
            y_position = y_offset + position_in_page * line_height
        else:
            # Sağ sütun
            x_position = right_margin
            y_position = y_offset + (position_in_page - words_per_column) * line_height
        
        pdf.set_xy(x_position, y_position)
        pdf.cell(90, line_height, f"{i}) {word} - {translated}", ln=True)

    # PDF'i kaydet
    pdf.output(os.path.abspath(file_path))
    
    print(f"Kelimeler ve anlamlar PDF olarak oluşturuldu: {file_path}")
    return file_path

