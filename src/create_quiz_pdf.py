import os
from datetime import datetime
from fpdf import FPDF

from src.fonts import BOLD, REGULAR, fit_font_size

# Quiz PDF oluşturma
def create_pdf(questions, file_name=None, output_dir=None):
    # Klasör oluştur. Yol mutlak - sürecin nereden başlatıldığına bağlı olmamalı.
    if output_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "quizzes")
    os.makedirs(output_dir, exist_ok=True)

    # Benzersiz dosya adı oluştur
    if file_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"quiz_{timestamp}.pdf"

    file_path = os.path.join(output_dir, file_name)
    
    
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    pdf.add_font("Body", "", REGULAR, uni=True)
    pdf.add_font("BodyBold", "", BOLD, uni=True)
    pdf.set_font("BodyBold", size=10)  # Başlık için biraz daha büyük font
    
    # Başlık Ekleme
    pdf.set_xy(10, 5)
    pdf.cell(190, 10, "Vocabulary Quiz", ln=True, align="C")
    pdf.set_font("Body", size=8)  # Sorular için tekrar küçük fonta geç

    left_margin = 10      # Sol sütun başlangıç noktası
    right_margin = 105    # Sağ sütun başlangıç noktası
    cell_width = 90       # Sütunlar arası mesafe 95mm - 5mm boşluk bırakır
    y_offset = 20         # Sayfa üst boşluğu
    line_height = 3       # Satır yüksekliği

    question_per_column = len(questions) // 2

    # Font boyutunu en uzun satıra göre seç. Şıklar yan yana dizildiği için
    # en kritik satırlar bunlar - dört uzun çeviri kolayca 90mm'yi aşar ve
    # sağdaki sütunun üzerine taşar.
    lines = [f"{i}) {q}" for i, q in enumerate(questions, 1)]
    lines += [
        "   ".join(f"{chr(65 + j)}) {c}" for j, c in enumerate(choices))
        for choices in questions.values()
    ]
    pdf.set_font_size(fit_font_size(pdf, lines, cell_width, start_size=8))

    for i, (question, choices) in enumerate(questions.items(), 1):
        x_position = left_margin if i <= question_per_column else right_margin
        if i == question_per_column + 1:
            y_offset = 20  # Sağ sütuna geçtiğinde baştan başla
        
        pdf.set_xy(x_position, y_offset)
        pdf.cell(90, line_height, f"{i}) {question}", ln=True)

        # Şıkları yan yana ekle
        choice_str = "   ".join([f"{chr(65+j)}) {choice}" for j, choice in enumerate(choices)])
        pdf.set_xy(x_position, y_offset + line_height)
        pdf.cell(90, line_height, choice_str, ln=True)

        y_offset += line_height * 3  # Sorular arasında boşluk

    # PDF'i kaydet
    pdf.output(os.path.abspath(file_path))
    
    print(f"Test PDF olarak oluşturuldu: {file_path}")
    return file_path

