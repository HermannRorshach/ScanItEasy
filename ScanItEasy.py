import datetime
import logging
import os
import sys

import pymupdf
from docx2pdf import convert

from pdf_compressor import compress

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')


# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,  # Уровень логов (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщения
)


class Converter:
    def __init__(self, docx_file, pdf_file):
        self.docx_file = docx_file
        self.pdf_file = pdf_file
        # self.image_file = image_file
        self.temp_images = []  # Для хранения путей к временным изображениям
        self.images_to_delete = []

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
        for img in self.images_to_delete:
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
        other_pages_image, color="red", translator_sign=None):
        """Добавление изображений на страницы PDF."""
        doc = pymupdf.open(self.pdf_file)

        # Вставляем изображение на первую страницу
        first_img = pymupdf.open(first_page_image)
        first_page = doc.load_page(0)

        # Получаем реальные размеры изображения
        first_img_width = 83.3
        first_img_height = 44.88

        if color == "blue":
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

            if color == "blue":
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

    def merge_pdf(self, first_file, second_file, output_path, remove=False):
        """Объединение двух PDF файлов."""
        logging.info(f"Начало объединения PDF файлов: {first_file} и {second_file} -> {output_path}")

        try:
            pdf_writer = pymupdf.open()
            for pdf in [first_file, second_file]:
                logging.info(f"Добавление страниц из файла: {pdf}")
                pdf_document = pymupdf.open(pdf)
                pdf_writer.insert_pdf(pdf_document)
                pdf_document.close()
            pdf_writer.save(output_path)
            logging.info(f"Объединение завершено: {output_path}")
            pdf_writer.close()

            # Удаление второго файла
            logging.info(f"Удаление временного файла: {second_file}")
            if remove:
                os.remove(second_file)
        except Exception as e:
            logging.error(f"Ошибка при объединении PDF файлов: {e}")
            raise

    @staticmethod
    def compress_pdf(input_pdf, output_pdf, compress_level=2):
        """Сжатие PDF файла."""
        logging.info(f"Начало сжатия PDF файла: {input_pdf} -> {output_pdf}, уровень сжатия: {compress_level}")

        try:
            compress(input_pdf, output_pdf, compress_level)
            logging.info(f"Сжатие завершено: {output_pdf}")
        except Exception as e:
            logging.error(f"Ошибка при сжатии PDF файла: {e}")
            raise



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


def process_scan(settings):
    logging.info("Начало программы")
    doc_decorations = {
        "red": ("doc_decorations/Красная лента. Первая страница.png",
                "doc_decorations/Уголок с красной лентой.png"),
        "blue": ("doc_decorations/Синяя лента. Первая страница.png",
                 "doc_decorations/Уголок с синей лентой.png")
    }

    try:
        color = settings.get("color", "red")
        decorations_set = doc_decorations[color]
        logging.debug(f"Выбраны украшения: {decorations_set}")

        pages = settings.get("pages", "all")
        logging.debug(f"Страницы для обработки: {pages}")

        need_sign_translator = settings.get("need_sign_translator") == "yes"
        mode = settings.get("mode") == "custom"
        docx_file_path = settings.get("docx_file_path")
        last_page = settings.get("last_page_path")

        if not docx_file_path:
            logging.error("Не указан путь к DOCX файлу")
            return

        if pages != "all":
            pages = parse_and_adjust_indices(pages)
            logging.debug(f"После парсинга страницы: {pages}")

        output_path = "Temp.pdf"
        final_output_path = docx_file_path.replace("docx", "pdf")
        logging.info(f"Конечный файл будет сохранен как: {final_output_path}")

        converter = Converter(docx_file_path, output_path)
        logging.info("Начинаем преобразование DOCX в PDF")
        converter.docx_to_pdf()

        logging.info("Преобразуем PDF в черно-белый")
        temp_images = converter.pdf_to_bw()

        if isinstance(pages, list):
            converter.images_to_delete = temp_images
            temp_images = [temp_images[index] for index in pages]
            logging.debug(f"Выбранные изображения: {temp_images}")

        converter.pngs_to_pdf(output_path, temp_images)
        logging.info("Сгенерирован временный PDF")

        args = [*[converter.resource_path(file) for file in decorations_set]]
        args.append(color)

        if need_sign_translator:
            args.append(converter.resource_path("doc_decorations/Подпись переводчика.png"))

        logging.info("Добавляем изображения на страницы PDF")
        converter.add_image_to_pdf(output_path, *args)

        if last_page:
            logging.info(f"Обрабатываем последнюю страницу: {last_page}")
            remove = False
            if not last_page.endswith(".pdf"):
                converter.pngs_to_pdf("last_page.pdf", [last_page])
                last_page = "last_page.pdf"
                remove = True
            converter.merge_pdf(output_path, last_page, output_path, remove=remove)

        converter.compress_pdf(input_pdf=output_path, output_pdf=final_output_path)
        logging.info("Сжатие завершено")


        if os.path.exists("acrobat_path.txt"):
            logging.debug('Проверяем наличие файла acrobat_path.txt')
            with open("acrobat_path.txt", "r", encoding="utf-8") as file:
                acrobat_path, page = [row.strip() for row in file.readlines()]
                logging.debug(f"Получены пути: {acrobat_path}, {page}")
        else:
            logging.debug("Файл acrobat_path.txt не найден, используем путь по умолчанию")
            acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
            page = 1

        try:
            os.system(f'start "" "{acrobat_path}" /A "page={page}" "{final_output_path}"')
            logging.info(f"Файл {final_output_path} открыт в Adobe Acrobat")
        except Exception as error:
            logging.error(f"Ошибка при открытии файла: {error}")

        if os.path.exists(final_output_path):
            logging.info("Итоговый файл успешно создан. Удаляем log-файл.")
            if os.path.exists('app.log'):
                logging.shutdown()
                logging.disable(logging.CRITICAL)
                os.remove('app.log')
            return True
    except Exception as error:
        logging.error(f"При выполнении программы возникла ошибка: {error}")
    finally:
        converter.clean_temp_files()
        logging.info("Временные файлы удалены")


import tkinter as tk
from tkinter import filedialog
from tkinter import ttk



def scan(settings):
    logging.info(f"Выбранные настройки: {settings}")

def update_mode():
    # Очистка текущего отображения
    for widget in custom_frame.winfo_children():
        widget.grid_forget()

    # Сначала показываем элементы для выбранного режима
    if mode_var.get() == "custom":
        # Добавляем элементы для пользовательского режима
        custom_frame.grid(row=6, column=0, pady=10, sticky="nsew")
        color_label.grid(row=0, column=0, sticky="w", padx=70)
        color_red.grid(row=1, column=0, sticky="w", padx=70)
        color_blue.grid(row=2, column=0, sticky="w", padx=70)
        pages_label.grid(row=3, column=0, sticky="w", padx=70)
        pages_entry.grid(row=4, column=0, sticky="w", padx=70)
        signature_label.grid(row=5, column=0, sticky="w", padx=70)
        signature_yes.grid(row=6, column=0, sticky="w", padx=70)
        signature_no.grid(row=7, column=0, sticky="w", padx=70)
    else:
        custom_frame.grid_forget()

win = tk.Tk()
ttk.Style().theme_use("classic")
win.title("Сканирование")
win.geometry("500x500")
win.resizable(False, False)

# Цветовая палитра
bg_color = "#2f2f2f"  # Темно-серый
btn_bg_color = "#003366"  # Темно-синий
btn_fg_color = "#FFFFFF"  # Белый
label_fg_color = "#B0B0B0"  # Светло-серый для текста
entry_bg_color = "#F4F4F4"  # Светлый серый для фона ввода

win.config(bg=bg_color)

# Выбор файлов
btn_file_docx = tk.Button(win, text="Выбрать файл docx", command=lambda: update_file_label(docx_label),
                          bg=btn_bg_color, fg=btn_fg_color, relief="flat")
btn_file_docx.grid(row=0, column=0, pady=10, padx=70, sticky="w")

docx_label = tk.Label(win, text=None, fg=label_fg_color, bg=bg_color)
docx_label.grid(row=1, column=0, pady=5, padx=70, sticky="w")

btn_file_last_page = tk.Button(win, text="Выбрать файл для последней страницы", command=lambda: update_file_label(last_page_label),
                               bg=btn_bg_color, fg=btn_fg_color, relief="flat")
btn_file_last_page.grid(row=2, column=0, pady=10, padx=70, sticky="w")

last_page_label = tk.Label(win, text=None, fg=label_fg_color, bg=bg_color)
last_page_label.grid(row=3, column=0, pady=5, padx=70, sticky="w")

# Режимы
mode_var = tk.StringVar(value="default")
mode_label = tk.Label(win, text="Выберите режим:", fg=label_fg_color, bg=bg_color)
mode_label.grid(row=4, column=0, pady=5, padx=70, sticky="w")

mode_default = tk.Radiobutton(win, text="По умолчанию", variable=mode_var, value="default", command=update_mode, bg=bg_color, fg=label_fg_color)
mode_default.grid(row=5, column=0, sticky="w", padx=70)

mode_custom = tk.Radiobutton(win, text="С пользовательскими настройками", variable=mode_var, value="custom", command=update_mode, bg=bg_color, fg=label_fg_color)
mode_custom.grid(row=6, column=0, sticky="w", padx=70)

# Настройки для пользовательского режима
custom_frame = tk.Frame(win, bg=bg_color)

# Цвет ленты
color_var = tk.StringVar(value="red")
color_label = tk.Label(custom_frame, text="Выберите цвет ленты:", fg=label_fg_color, bg=bg_color)

color_red = tk.Radiobutton(custom_frame, text="Красный", variable=color_var, value="red", bg=bg_color, fg=label_fg_color)
color_blue = tk.Radiobutton(custom_frame, text="Синий", variable=color_var, value="blue", bg=bg_color, fg=label_fg_color)

# Выбор страниц
pages_label = tk.Label(custom_frame, text="Выберите страницы:", fg=label_fg_color, bg=bg_color)
pages_entry = tk.Entry(custom_frame, bg=entry_bg_color)

# Подпись переводчика
signature_var = tk.StringVar(value="yes")
signature_label = tk.Label(custom_frame, text="Нужна ли подпись переводчика?", fg=label_fg_color, bg=bg_color)

signature_yes = tk.Radiobutton(custom_frame, text="Да", variable=signature_var, value="yes", bg=bg_color, fg=label_fg_color)
signature_no = tk.Radiobutton(custom_frame, text="Нет", variable=signature_var, value="no", bg=bg_color, fg=label_fg_color)

# Кнопка "Отсканировать"
def on_scan():
    settings = {
        "mode": mode_var.get(),
        "color": color_var.get() if mode_var.get() == "custom" else "red",
        "pages": pages_entry.get() if mode_var.get() == "custom" else "all",
        "need_sign_translator": signature_var.get() if mode_var.get() == "custom" else "yes",
        "docx_file_path": docx_label.cget("text"),
        "last_page_path": last_page_label.cget("text")
    }
    scan(settings)
    current_year = datetime.datetime.now().year
    if current_year < 2026:
        logging.info("Ваша подписка действует до 31 декабря 2025 года.")
    else:
        logging.info("Ваша подписка истекла 1 января 2026 года. Свяжитесь с разработчиком, чтобы продлить подписку.")
        return
    process_scan(settings)


btn_scan = tk.Button(win, text="Отсканировать", command=on_scan, bg=btn_bg_color, fg=btn_fg_color)
btn_scan.grid(row=7, column=0, pady=20, padx=70, sticky="w")

# Функция обновления метки с именем выбранного файла
def update_file_label(label):
    filename = filedialog.askopenfilename()
    label.config(text=filename if filename else None)


win.mainloop()
