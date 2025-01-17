import datetime
import os
import sys
from time import sleep

import pymupdf
from docx2pdf import convert

from pdf_compressor import compress


class Converter:
    def __init__(self, docx_file, pdf_file):
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
            img_name = fr"page_{page_num}.png"
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


    def clean_temp_files(self):
        """Удаление временных изображений."""
        for img in self.temp_images:
            if os.path.exists(img):
                os.remove(img)
        self.temp_images.clear()
        if os.path.exists("temp.pdf"):
            os.remove("temp.pdf")
        if os.path.exists("last_page.pdf"):
            os.remove("last_page.pdf")

    @staticmethod
    def resource_path(relative_path):
        """Получение абсолютного пути к ресурсу, работает как в dev, так и в bundled режиме."""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def add_image_to_pdf(
        self, output_path, first_page_image,
        other_pages_image, mode=0, translator_sign=None):
        """Добавление изображений на страницы PDF."""
        doc = pymupdf.open(self.pdf_file)

        # Вставляем изображение на первую страницу
        first_img = pymupdf.open(first_page_image)
        first_page = doc.load_page(0)

        # Получаем реальные размеры изображения
        first_img_width = 83.3
        first_img_height = 44.88

        if mode:
            first_img_width = first_img[0].rect.width
            first_img_height = first_img[0].rect.height
        # print('first_img_width =', first_img_width, 'first_img_height =', first_img_height)

        # Вставляем изображение в левый верхний угол первой страницы с его реальными размерами
        first_page.insert_image(pymupdf.Rect(0, 0, first_img_width, first_img_height), filename=first_page_image)

        # Вставляем изображение на последующие страницы
        for page_num in range(1, doc.page_count):
            page = doc.load_page(page_num)
            other_img = pymupdf.open(other_pages_image)

            # other_img_width = other_img[0].rect.width
            # other_img_height = other_img[0].rect.height
            other_img_width = 91.5
            other_img_height = 136.8

            if mode:
                other_img_width = 110
                other_img_height = 110

            # Вставляем изображение в левый верхний угол с его реальными размерами
            page.insert_image(pymupdf.Rect(0, 0, other_img_width, other_img_height), filename=other_pages_image)

        # print('other_img_width =', other_img_width, 'other_img_height =', other_img_height)
        # Вставляем изображения на последнюю страницу
        if translator_sign:
            translator_sign_page = doc.load_page(doc.page_count - 1)
            translator_sign_img = pymupdf.open(translator_sign)

            translator_sign_img_width = translator_sign_img[0].rect.width
            translator_sign_img_height = translator_sign_img[0].rect.height
            translator_sign_img_width = 645
            translator_sign_img_height = 120

            # print('translator_sign_img_width =', translator_sign_img_width, 'translator_sign_img_height =', translator_sign_img_height)
            # print('translator_sign_page.rect.width =', translator_sign_page.rect.width, 'translator_sign_page.rect.height =', translator_sign_page.rect.height)

            # Вставляем изображение для последующих страниц в левый верхний угол
            translator_sign_page.insert_image(pymupdf.Rect(0, translator_sign_page.rect.height - translator_sign_img_height, translator_sign_img_width, translator_sign_page.rect.height), filename=translator_sign)

        doc.save(output_path, incremental=True, encryption=0)  # Сохраняем изменения
        doc.close()

    def merge_pdf(self, first_file, second_file, output_path):
        pdf_writer = pymupdf.open()
        for pdf in [first_file, second_file]:
            pdf_document = pymupdf.open(pdf)
            pdf_writer.insert_pdf(pdf_document)
            pdf_document.close()
        pdf_writer.save(output_path)
        pdf_writer.close()
        os.remove(second_file)

    @staticmethod
    def compress_pdf(input_pdf, output_pdf, compress_level=2):
        compress(input_pdf, output_pdf)


def find_file_path(files, extensions, mode):
    option = len(extensions) > 1
    if not files:
        print(
            f"В папке с исполняемым файлом нет файла с "
            f"расширени{('ем', 'ями')[option]} {', '.join(extensions)}")
        input("Поместите файл с нужным расширением в папку с программой, нажмите любую клавишу, а затем Enter, чтобы продолжить\n")
        return
    elif len(files) > 1:
        message = ('Введите номер, соответствующий названию файла, который надо отсканировать',
                   'Выберите файл, который содержит последнюю страницу скана')[mode]
        print("В папке с исполняемым файлом более, чем один файл "
              f"в формат{('е', 'ах')[option]} {', '.join(extensions)}\n"
              f"{message}")
        [print(f"{number} - {file}") for number, file in enumerate(files, 1)]
        answer = input()
        file_path = files[int(answer) - 1]
    elif len(files) == 1:
        file_path = files[0]
    return file_path


def parse_and_adjust_indices(user_input):
    result = []

    for part in user_input.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start - 1, end))
        else:
            result.append(int(part) - 1)

    result.sort()
    return result


def process_scan():
    print("\nНачало программы\n")
    doc_decorations = {
        "red": ("doc_decorations/Красная лента. Первая страница.png",
                "doc_decorations/Уголок с красной лентой.png"),
        "blue": ("doc_decorations/Синяя лента. Первая страница.png",
                 "doc_decorations/Уголок с синей лентой.png")
    }

    try:
        decorations_set = doc_decorations["red"] # цвет ленты по умолчанию красный
        pages = "all" # по умолчанию сканируются все страницы
        need_sign_translator = True # по умолчанию подпись переводчика ставится

        files_and_directories = os.listdir()
        all_files = [f for f in files_and_directories if os.path.isfile(f)]
        files = [f for f in all_files if f.endswith(".docx")]

        file_path = find_file_path(files, ["docx"], mode=0)
        if not file_path:
            return
        user_input = input("\nХотите использовать режим по умолчанию?\n"
            "1 - режим по умолчанию\n"
            "2 - гибкий режим с возможностью выбора цвета ленточки и сканируемых страниц\n")

        if user_input == "2":
            print(f"Вы выбрали режим с вводом дополнительных параметров")
            answer = input("Выберите цвет ленты\n1 - красная\n2 - синяя\n")
            decorations_set = doc_decorations[("red", "blue")[int(answer) - 1]]

            answer = input("Выберите страницы, которые нужно сканировать.\n"
                        "Введите номера и/или  диапазоны страниц, например: 1-3, 5, 7-8\n"
                        "Чтобы сканировать все страницы, введите 'все' или ничего не вводите и нажмите Enter\n")
            if not answer in ("", "все"):
                # Получаем номера страниц, которые надо сканировать
                pages = parse_and_adjust_indices(answer)

            answer = input("Нужна ли подпись переводчика?\n"
                        "1 - нужна\n2 - не нужна\n")

            need_sign_translator = not bool(int(answer) - 1)

        elif user_input == "1":
            print("Начинаем режим по умолчанию")

        else:
            print('Вы ввели неправильное число, придётся начать сначала')
            return
        files = [f for f in all_files if f.split('.')[-1] in ("png", "pdf", "jpeg", "jpg")]
        last_page = find_file_path(files, ["png", "pdf", "jpeg", "jpg"], mode=1)
        output_path = "Temp.pdf"
        final_output_path = file_path.replace("docx", "pdf")
        converter = Converter(file_path, output_path) #, "image.png")
        converter.docx_to_pdf()  # Преобразуем DOCX в PDF
        temp_images = converter.pdf_to_bw()  # Преобразуем PDF в черно-белый и получаем пути к изображениям
        if isinstance(pages, list):
            temp_images = [temp_images[index] for index in pages]

        converter.pngs_to_pdf(output_path, temp_images)
        args = [*[converter.resource_path(file) for file in decorations_set]]

        # Добавляем переменную mode для правильной настройки размеров вставляемых изображений
        args.append(decorations_set == doc_decorations["blue"])

        if need_sign_translator:
            args.append(converter.resource_path("doc_decorations/Подпись переводчика.png"))
        converter.add_image_to_pdf(output_path, *args)

        if last_page:
            if not last_page.endswith(".pdf"):
                converter.pngs_to_pdf("last_page.pdf", [last_page])
                last_page = "last_page.pdf"
            converter.merge_pdf(output_path, last_page, output_path)
        converter.compress_pdf(input_pdf=output_path, output_pdf=final_output_path)
        print("Завершили сжатие")
        converter.clean_temp_files()  # Удаляем временные изображения

        if os.path.exists("acrobat_path.txt"):
            print('Проверяем наличие файла acrobat_path.txt')
            # Открываем файл для чтения
            with open("acrobat_path.txt", "r", encoding="utf-8") as file:
                print('Открыли файл')
                acrobat_path, page = [row.strip() for row in file.readlines()]
                acrobat_path = fr"{acrobat_path}"
                print("Успешно получили:", acrobat_path, page)
        else:
            print("Запускаем открытие файла")
            acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
            page = 1
        try:
            os.system(f'start "" "{acrobat_path}" /A "page={page}" "{final_output_path}"')
        except Exception as error:
            print(error)
        return True
    except Exception as error:
        print("При выполнении программы возникла ошибка:", error)


def main():
    while True:
        answer = process_scan()
        if answer is not None:
            print("Программа завершена")
            print("\nНе забудьте продлить подписку до 31 декабря 2025 года.")
            sleep(10)
            break


if __name__ == '__main__':
    current_year = datetime.datetime.now().year
    if current_year < 2026:
        print("Ваша подписка действует до 31 декабря 2025 года.")
        main()
    else:
        print("Ваша подписка истекла 1 января 2026 года. Свяжитесь с разработчиком, чтобы продлить подписку.")
