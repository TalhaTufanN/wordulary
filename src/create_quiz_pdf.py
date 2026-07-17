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

    left_margin = 10             # Sol sütun başlangıç noktası
    right_margin = 105           # Sağ sütun başlangıç noktası
    cell_width = 90              # Sütunlar arası mesafe 95mm - 5mm boşluk bırakır
    y_offset = 20                # Sayfa üst boşluğu
    line_height = 3              # Satır yüksekliği
    question_block = line_height * 3  # Soru + şıklar + boşluk
    questions_per_page = 50      # Sayfa başına 50 soru (25 sol + 25 sağ)
    questions_per_column = 25

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    # Otomatik sayfa kırılması kapalı: yerleşim set_xy ile elle yönetiliyor,
    # sayfalama aşağıda açıkça yapılıyor.
    pdf.set_auto_page_break(auto=False)

    pdf.add_font("Body", "", REGULAR, uni=True)
    pdf.add_font("BodyBold", "", BOLD, uni=True)

    items = list(questions.items())

    # Font boyutunu en uzun satıra göre seç. Şıklar yan yana dizildiği için
    # en kritik satırlar bunlar - dört uzun çeviri kolayca 90mm'yi aşar ve
    # sağdaki sütunun üzerine taşar. (fit_font_size aktif fontu ölçüyor.)
    pdf.add_page()  # get_string_width bir sayfa gerektiriyor
    pdf.set_font("Body", size=8)
    lines = [f"{i}) {q}" for i, (q, _) in enumerate(items, 1)]
    lines += ["   ".join(f"{chr(65 + j)}) {c}" for j, c in enumerate(ch)) for _, ch in items]
    body_size = fit_font_size(pdf, lines, cell_width, start_size=8)

    for i, (question, choices) in enumerate(items):
        position_in_page = i % questions_per_page

        # Her 50 soruda bir yeni sayfa ve başlık.
        if position_in_page == 0:
            if i > 0:
                pdf.add_page()
            pdf.set_font("BodyBold", size=10)
            pdf.set_xy(10, 5)
            pdf.cell(190, 10, "Vocabulary Quiz", ln=True, align="C")
            pdf.set_font("Body", size=body_size)

        # Sol sütun (0-24) veya sağ sütun (25-49)
        if position_in_page < questions_per_column:
            x_position = left_margin
            row = position_in_page
        else:
            x_position = right_margin
            row = position_in_page - questions_per_column
        y = y_offset + row * question_block

        pdf.set_xy(x_position, y)
        pdf.cell(90, line_height, f"{i + 1}) {question}", ln=True)

        choice_str = "   ".join(f"{chr(65 + j)}) {choice}" for j, choice in enumerate(choices))
        pdf.set_xy(x_position, y + line_height)
        pdf.cell(90, line_height, choice_str, ln=True)

    pdf.output(os.path.abspath(file_path))

    print(f"Test PDF olarak oluşturuldu: {file_path}")
    return file_path
