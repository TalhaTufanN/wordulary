import os
from datetime import datetime
from fpdf import FPDF

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
    
    # Font dosya yolları
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path_arial = os.path.join(base_dir, "arial.ttf")
    font_path_arial_bold = os.path.join(base_dir, "arialbd.ttf")
    
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    # Arial Font ekle
    pdf.add_font("Arial", "", font_path_arial, uni=True)
    pdf.add_font("ArialBold", "", font_path_arial_bold, uni=True)
    pdf.set_font("ArialBold", size=10)  # Başlık için biraz daha büyük font
    
    # Başlık Ekleme
    pdf.set_xy(10, 5)
    pdf.cell(190, 10, "Vocabulary Quiz", ln=True, align="C")  
    pdf.set_font("Arial", size=8)  # Sorular için tekrar küçük fonta geç
    
    left_margin = 10      # Sol sütun başlangıç noktası
    right_margin = 105    # Sağ sütun başlangıç noktası
    y_offset = 20         # Sayfa üst boşluğu
    line_height = 3       # Satır yüksekliği
    column_switch = 25    # Sol sütun sınırı
    
    question_per_column = len(questions) // 2

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

