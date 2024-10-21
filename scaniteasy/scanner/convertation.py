import os

import pymupdf
from docx2pdf import convert


class Converter:
    def __init__(self, docx_file, pdf_file): #, image_file):
        self.docx_file = docx_file
        self.pdf_file = pdf_file
        # self.image_file = image_file
        self.temp_images = []  # Для хранения путей к временным изображениям

    def docx_to_pdf(self):
        """Преобразование DOCX в PDF."""
        convert(self.docx_file, self.pdf_file)

    def pdf_to_bw(self, dpi=300):
        """Преобразование страниц PDF в черно-белые и создание PNG-файлов с заданным разрешением."""
        doc = pymupdf.open(self.pdf_file)

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72))  # Увеличиваем разрешение
            pix_bw = pymupdf.Pixmap(pymupdf.csGRAY, pix)
            img_name = f"page_{page_num}.png"
            pix_bw.save(img_name)
            self.temp_images.append(img_name)  # Сохраняем путь к изображению

        doc.close()
        return self.temp_images

    def pngs_to_pdf(self, output_pdf, png_files):
        """Создание нового PDF-файла из существующих PNG-файлов с размером страниц A4."""
        A4_WIDTH = 595  # Ширина A4 в пунктах
        A4_HEIGHT = 842  # Высота A4 в пунктах

        doc = pymupdf.open()  # Создаем новый PDF-документ

        for png_file in png_files:
            img = pymupdf.open(png_file)  # Открываем PNG-файл
            rect = img[0].rect  # Получаем размеры изображения

            # Определяем коэффициенты масштабирования для ширины и высоты
            width_ratio = A4_WIDTH / rect.width
            height_ratio = A4_HEIGHT / rect.height
            scale = min(width_ratio, height_ratio)  # Используем минимальный коэффициент для пропорционального масштабирования

            # Вычисляем новые размеры изображения
            new_width = rect.width * scale
            new_height = rect.height * scale

            # Создаем новую страницу формата A4
            pdf_page = doc.new_page(width=A4_WIDTH, height=A4_HEIGHT)

            # Вставляем масштабированное изображение на страницу
            pdf_page.insert_image(pymupdf.Rect(0, 0, new_width, new_height), filename=png_file)

        doc.save(output_pdf)  # Сохраняем новый PDF
        doc.close()


    def clean_temp_images(self):
        """Удаление временных изображений."""
        for img in self.temp_images:
            if os.path.exists(img):
                os.remove(img)
        self.temp_images.clear()

    @staticmethod
    def compress_pdf(input_pdf, output_pdf, compress_level=2):
        # Задаем параметры сжатия для Ghostscript
        from pdf_compressor import compress
        compress(input_pdf, output_pdf)


# Пример использования:
converter = Converter("test.docx", "output.pdf") #, "image.png")
converter.docx_to_pdf()  # Преобразуем DOCX в PDF
temp_images = converter.pdf_to_bw()  # Преобразуем PDF в черно-белый и получаем пути к изображениям
print("Созданные изображения:", temp_images)
converter.pngs_to_pdf("new_output.pdf", temp_images)
# converter.add_image_to_pdf()  # Добавляем изображение на каждую страницу
converter.clean_temp_images()  # Удаляем временные изображения
converter.compress_pdf(input_pdf='new_output.pdf', output_pdf='output.pdf')