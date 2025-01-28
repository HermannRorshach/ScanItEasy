from docx2pdf import convert
import os
import logging

import pymupdf
import os


class Converter:
    def __init__(self, docx_file, pdf_file):
        self.docx_file = docx_file
        self.pdf_file = pdf_file
        self.temp_docx_file = "temp_document.docx"  # Временный файл для выборки страниц


    def docx_to_pdf(self):
        """Преобразование DOCX в PDF."""
        logging.info(f"Начало преобразования DOCX в PDF: {self.docx_file} -> {self.pdf_file}")

        if not os.path.exists(self.docx_file):
            logging.error(f"Файл {self.docx_file} не существует.")
            raise FileNotFoundError(f"Файл {self.docx_file} не найден.")

        try:
            convert(self.docx_file, self.pdf_file)
            logging.info(f"Преобразование завершено: {self.pdf_file}")
        except Exception as e:
            logging.error(f"Ошибка вызова функции convert: {e}")
            raise

        if not os.path.exists(self.pdf_file):
            logging.error(f"Преобразование не удалось, файл {self.pdf_file} не создан.")
            raise RuntimeError("Ошибка преобразования DOCX в PDF.")



    def extract_pages_from_pdf(self, output_pdf, pages):
        input_pdf = self.pdf_file
        if not os.path.exists(self.pdf_file):
            raise FileNotFoundError(f"Файл {input_pdf} не найден.")

        # Открываем входной PDF-файл
        with pymupdf.open(input_pdf) as pdf:
            output_pdf_doc = pymupdf.open()  # Создаем новый PDF-документ

            for page_num in pages:
                try:
                    page = pdf[page_num - 1]
                    output_pdf_doc.insert_pdf(pdf, from_page=page_num - 1, to_page=page_num - 1)
                except IndexError:
                    print(f"Страница {page_num} отсутствует в {input_pdf}. Пропускаем.")

            output_pdf_doc.save(output_pdf)
            print(f"Файл сохранен: {output_pdf}")



converter = Converter("Кимия Захедиан Временный сертификат.docx", "output.pdf")
converter.docx_to_pdf()
converter.extract_pages_from_pdf("Кимия Захедиан Временный сертификат.pdf", [1, 3, 5])
