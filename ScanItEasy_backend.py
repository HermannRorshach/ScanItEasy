import logging
import os
import platform
import sys

import pymupdf
from docx2pdf import convert

# Отключение вывода всех необработанных исключений в консоль
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Настройка логирования
logger = logging.getLogger()

# Проверка, если обработчики уже добавлены
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)

    # Создаем обработчик для записи в файл с кодировкой 'utf-8'
    file_handler = logging.FileHandler('app.log', mode='a', encoding='utf-8')
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

# # Обработка необработанных исключений
# def handle_exception(exc_type, exc_value, exc_tb):
#     pass  # Пропускаем исключения, не выводим их

# sys.excepthook = handle_exception


class Converter:
    def __init__(self, docx_file: str = None, pdf_file: str = None):
        """
        Initialize the Converter class with optional DOCX and PDF file paths.

        Parameters:
        docx_file (str): Path to the DOCX file.
        pdf_file (str): Path to the output PDF file.
        """
        self.docx_file = docx_file
        self.pdf_file = pdf_file
        self.temp_images = []  # Для хранения путей к временным изображениям
        self.images_to_delete = []

    def docx_to_pdf(self, pages_to_keep: list = None) -> None:
        """
        Convert a DOCX file to PDF and save only the specified pages.

        Parameters:
        pages_to_keep (list or str): List of pages to retain in the PDF,
                                      or 'all' to keep all pages.

        Raises:
        FileNotFoundError: If the DOCX file doesn't exist.
        RuntimeError: If the conversion fails or the output PDF isn't created.
        """
        logging.info(
            f"Начало преобразования DOCX в PDF: {self.docx_file} -> "
            f"{self.pdf_file}")
        logging.info(f'pages_to_keep = {pages_to_keep}')
        if not os.path.exists(self.docx_file):
            logging.error(f"Файл {self.docx_file} не существует.")
            raise FileNotFoundError(f"Файл {self.docx_file} не найден.")

        try:
            # Преобразуем DOCX в PDF
            convert(self.docx_file, self.pdf_file)
            logging.info(f"Преобразование завершено: {self.pdf_file}")
        except Exception as e:
            logging.error(f"Ошибка вызова функции convert: {e}")
            raise

        if not os.path.exists(self.pdf_file):
            logging.error(
                f"Преобразование не удалось, файл {self.pdf_file} не создан.")
            raise RuntimeError("Ошибка преобразования DOCX в PDF.")

        # Если страницы для сохранения не указаны, не изменяем файл
        if pages_to_keep and pages_to_keep != "all":
            logging.info("совершаем выборочное сохранение страниц в pdf")
            # Открываем преобразованный PDF
            pdf_document = pymupdf.open(self.pdf_file)
            pdf_writer = pymupdf.open()

            # Добавляем только указанные страницы
            for page_num in pages_to_keep:
                logging.info(f'Вставляем страницу номер {page_num}')
                # Проверяем, что страница существует
                if page_num < len(pdf_document):
                    # Вставляем страницу в новый PDF
                    pdf_writer.insert_pdf(
                        pdf_document, from_page=page_num, to_page=page_num)

            # Сохраняем новый PDF с выбранными страницами
            pdf_document.close()
            os.remove(self.pdf_file)
            pdf_writer.save(self.pdf_file)
            pdf_writer.close()

            logging.info(
                f"Оставлены только указанные страницы. "
                f"Итоговый файл: {self.pdf_file}")
        else:
            logging.info(
                "Не указаны страницы для удаления. Все страницы сохранены.")

    def pdf_to_png(self, dpi: int = 300, grayscale: bool = True,
                   pages_to_convert: list = None) -> list:
        """
        Convert pages of a PDF file to PNG images at the specified resolution.

        Parameters:
        dpi (int): Resolution for the PNG images (default is 300).
        grayscale (bool): If True, convert the images to grayscale.
                        Default is True.
        pages_to_convert (list or str): List of pages to convert, or 'all' for
                                        all pages.

        Returns:
        list: List of file paths for the generated PNG images.
        """
        logging.info(f"pages_to_convert = {pages_to_convert}")
        doc = pymupdf.open(self.pdf_file)
        if not pages_to_convert or pages_to_convert == "all":
            pages_to_convert = range(doc.page_count)

        for page_num in pages_to_convert:
            # Проверяем, что страница существует
            if page_num < doc.page_count:
                page = doc.load_page(page_num)
                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(dpi / 72, dpi / 72))
                pix_bw = pix  # Цветное изображение без изменений

                # Преобразование в чёрно-белый или цветной формат в
                # зависимости от параметра
                if grayscale:
                    pix_bw = pymupdf.Pixmap(pymupdf.csGRAY, pix)

                img_name = (fr"{self.pdf_file.replace(".pdf", "")}_"
                            fr"page_{page_num}.png")
                pix_bw.save(img_name)
                self.temp_images.append(img_name)

        doc.close()
        return self.temp_images

    def pngs_to_pdf(self, output_pdf: str, png_files: list) -> None:
        """
        Create a PDF from a list of PNG files, adjusting the orientation and
        centering images.

        Parameters:
        output_pdf (str): Path where the resulting PDF will be saved.
        png_files (list): List of PNG file paths to include in the PDF.

        Raises:
        RuntimeError: If the PDF cannot be created from the PNG files.
        """

        # Ширина и высота страницы A4 в пунктах
        a4_width, a4_height = 595, 842
        doc = pymupdf.open()

        for png_file in png_files:
            img = pymupdf.open(png_file)
            rect = img[0].rect

            # Проверка ориентации изображения
            is_landscape = rect.width > rect.height

            # Устанавливаем ориентацию страницы в зависимости от изображения
            page_width, page_height = (
                a4_height, a4_width) if is_landscape else (
                    a4_width, a4_height)

            # Масштабирование изображения
            scale = min(page_width / rect.width, page_height / rect.height)
            new_width, new_height = rect.width * scale, rect.height * scale

            # Вычисление отступов для центрирования изображения
            x_offset = (page_width - new_width) / 2
            y_offset = (page_height - new_height) / 2

            # Создаём страницу и вставляем изображение с учётом отступов
            pdf_page = doc.new_page(width=page_width, height=page_height)
            pdf_page.insert_image(
                pymupdf.Rect(x_offset, y_offset, x_offset + new_width,
                             y_offset + new_height), filename=png_file)

        doc.save(output_pdf)
        doc.close()

    def clean_temp_files(self) -> None:
        """
        Deletes temporary image files and other temporary resources.

        Removes image files listed in `temp_images` and `images_to_delete` and
        clears the lists. Also removes "temp.pdf" and "last_page.pdf" if they
        exist.
        """
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
    def resource_path(relative_path: str) -> str:
        """
        Gets the absolute path to a resource, working in both dev and bundled
        modes.

        Parameters:
        relative_path (str): The relative path to the resource.

        Returns:
        str: The absolute path to the resource.
        """
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        logger.debug(f"Базовый путь: {base_path}")
        full_path = os.path.join(base_path, relative_path)
        logger.debug(f"Полный путь к ресурсу: {full_path}")
        return full_path

    def add_image_to_pdf(
        self, output_path: str, first_page_image: str, other_pages_image: str,
        color: str = "red", translator_sign: str = None
    ) -> None:
        """
        Adds images to a PDF file.

        Parameters:
        output_path (str): Path to save the modified PDF.
        first_page_image (str): Image to insert on the first page.
        other_pages_image (str): Image to insert on the other pages.
        color (str): Color of the images (default is 'red').
        translator_sign (str): Path to an image to insert on the last page.
        """
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
        # print('first_img_width =', first_img_width, 'first_img_height =',
        # first_img_height)

        # Вставляем изображение в левый верхний угол первой страницы
        # с его реальными размерами
        first_page.insert_image(pymupdf.Rect(
            0, 0, first_img_width, first_img_height),
            filename=first_page_image)

        # Вставляем изображение на последующие страницы
        for page_num in range(1, doc.page_count):
            page = doc.load_page(page_num)
            # other_img = pymupdf.open(other_pages_image)
            # other_img_width = other_img[0].rect.width
            # other_img_height = other_img[0].rect.height
            other_img_width = 91.5
            other_img_height = 136.8

            if color == "blue":
                other_img_width = 110
                other_img_height = 110

            # Вставляем изображение в левый верхний угол с его
            # реальными размерами
            page.insert_image(
                pymupdf.Rect(
                    0, 0, other_img_width, other_img_height
                    ), filename=other_pages_image)

        # print('other_img_width =', other_img_width,
        # 'other_img_height =', other_img_height)
        # Вставляем изображения на последнюю страницу
        if translator_sign:
            translator_sign_page = doc.load_page(doc.page_count - 1)
            translator_sign_img = pymupdf.open(translator_sign)

            translator_sign_img_width = translator_sign_img[0].rect.width
            translator_sign_img_height = translator_sign_img[0].rect.height
            translator_sign_img_width = 645
            translator_sign_img_height = 120

            # print(
            # 'translator_sign_img_width =',
            # translator_sign_img_width,
            # 'translator_sign_img_height =',
            # translator_sign_img_height)
            # print('translator_sign_page.rect.width =',
            # translator_sign_page.rect.width,
            # 'translator_sign_page.rect.height =',
            # translator_sign_page.rect.height)

            # Вставляем изображение для последующих страниц в левый
            # верхний угол
            translator_sign_page.insert_image(
                pymupdf.Rect(
                    0,
                    translator_sign_page.rect.height
                    - translator_sign_img_height, translator_sign_img_width,
                    translator_sign_page.rect.height
                    ), filename=translator_sign)

        doc.save(output_path, incremental=True, encryption=0)
        doc.close()

    def merge_pdf(self, first_file: str, second_file: str,
                  output_path: str, remove: bool = False) -> None:
        """
        Merges two PDF files into one.

        Parameters:
        first_file (str): Path to the first PDF file.
        second_file (str): Path to the second PDF file.
        output_path (str): Path where the merged PDF will be saved.
        remove (bool): If True, deletes the second file after merging
        (default is False).

        Raises:
        Exception: If there is an error during the merging process.
        """
        logging.info(
            f"Начало объединения PDF файлов: {first_file} и {second_file} -> "
            f"{output_path}")

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
    def compress_pdf(input_pdf: str, output_pdf: str,
                     compress_level: int = 2) -> None:
        """
        Compresses a PDF file.

        Parameters:
        input_pdf (str): Path to the input PDF file.
        output_pdf (str): Path where the compressed PDF will be saved.
        compress_level (int): Compression level (default is 2).

        Raises:
        Exception: If there is an error during the compression process.
        """
        logging.info(
            f"Начало сжатия PDF файла: {input_pdf} -> {output_pdf}, "
            f"уровень сжатия: {compress_level}")
        try:
            from subprocess import CalledProcessError

            from pdf_compressor import compress
            compress(input_pdf, output_pdf, compress_level)
            logging.info(f"Сжатие завершено: {output_pdf}")
        except (CalledProcessError, FileNotFoundError):
            import pikepdf

            # Если ошибка, используем pikepdf
            logging.info("Используем pikepdf для сжатия.")
            with pikepdf.open(input_pdf) as pdf:
                pdf.save(output_pdf, compress_streams=True)
                logging.info(
                    f"Сжатие с помощью pikepdf завершено: {output_pdf}")
        except Exception as e:
            logging.error(f"Ошибка при сжатии PDF файла: {e}.")


def merge_multiple_pdfs(files: list, pages: list, output_path: str) -> None:
    """
    Merges multiple PDF files with selected pages from each file.

    Parameters:
    files (list): List of PDF file paths to merge.
    pages (list): List of pages to include from each PDF file.
                    Empty strings mean all pages will be included.
    output_path (str): Path to save the merged PDF file.

    Returns:
    None
    """
    logging.info(
        f'files = {files}, pages = {pages}, output_path = {output_path}')

    # Создаем новый PDF для записи
    pdf_writer = pymupdf.open()
    logging.info('Открыли новый файл для записи')

    for i, pdf_file in enumerate(files):
        pdf_document = pymupdf.open(pdf_file)
        logging.info(f'Открываем pdf из параметров {pdf_file}')

        if not pages[i]:  # Строка пуста, значит добавляем все страницы
            pages[i] = list(range(pdf_document.page_count))
        logging.info(f'Список страниц файла {pdf_file} {pages[i]}')

        # Получаем страницы для текущего файла
        for page_num in pages[i]:
            # Добавляем страницу в новый документ
            pdf_writer.insert_pdf(
                pdf_document, from_page=page_num, to_page=page_num)

        pdf_document.close()

    # Сохраняем результат в output_path
    pdf_writer.save(output_path)
    pdf_writer.close()


def parse_and_adjust_indices(user_input: str) -> list:
    """
    Parses user input for page numbers or ranges and adjusts the indices.

    Parameters:
    user_input (str): A comma-separated string of page numbers or ranges.

    Returns:
    list: A list of adjusted page indices (zero-based).
    """
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


def docx_modes(settings: dict) -> str:
    """
    Handles DOCX to PDF conversion, adding decorations, and optional
    compression.

    Parameters:
    settings (dict): Dictionary containing settings like color, pages,
    paths, etc.

    Returns:
    str: Path to the final output PDF file.
    """
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

        need_sign_translator = settings.get("need_sign_translator")
        convert_to_pdf_mode = settings.get("mode") == "convert_to_pdf_mode"
        docx_file_path = settings.get("docx_path")
        last_page = settings.get("last_page_path")
        is_compression_needed = settings.get("is_compression_needed")

        if not docx_file_path:
            logging.error("Не указан путь к DOCX файлу")
            return None

        if pages not in ("all", ""):
            pages = parse_and_adjust_indices(pages)
            logging.debug(f"После парсинга страницы: {pages}")

        output_path = "Temp.pdf"
        final_output_path = docx_file_path.replace("docx", "pdf")
        if not is_compression_needed:
            output_path = final_output_path
        logging.info(f"Конечный файл будет сохранен как: {final_output_path}")
        settings["progress"] = 5
        converter = Converter(docx_file_path, output_path)
        logging.info("Начинаем преобразование DOCX в PDF")
        converter.docx_to_pdf(pages_to_keep=pages)
        if convert_to_pdf_mode:
            settings["progress"] = 60
        if not convert_to_pdf_mode:
            settings["progress"] = 35

            logging.info("Преобразуем PDF в черно-белый")
            temp_images = converter.pdf_to_png()
            settings["progress"] = 50

            converter.pngs_to_pdf(output_path, temp_images)
            logging.info("Сгенерирован временный PDF")
            settings["progress"] = 65

            args = [*[converter.resource_path(
                relative_path=file) for file in decorations_set]]
            args.append(color)

            if need_sign_translator:
                args.append(
                    converter.resource_path(
                        "doc_decorations/Подпись переводчика.png"))

            logging.info("Добавляем изображения на страницы PDF")
            converter.add_image_to_pdf(output_path, *args)

            if last_page:
                logging.info(f"Обрабатываем последнюю страницу: {last_page}")
                remove = False
                if not last_page.endswith(".pdf"):
                    converter.pngs_to_pdf("last_page.pdf", [last_page])
                    last_page = "last_page.pdf"
                    remove = True
                converter.merge_pdf(output_path, last_page, output_path,
                                    remove=remove)
            settings["progress"] = 80
        if is_compression_needed:
            converter.compress_pdf(
                input_pdf=output_path, output_pdf=final_output_path)
            logging.info("Сжатие завершено")
        settings["progress"] = 100

    except Exception as error:
        logging.error(f"При выполнении программы возникла ошибка: {error}")
    finally:
        converter.clean_temp_files()
        logging.info("Временные файлы удалены")
        return final_output_path


def pdf_modes(settings: dict) -> str:
    """
    Handles operations on a PDF, such as grayscale conversion and compression.

    Parameters:
    settings (dict): Dictionary containing settings like pages, mode,
    and paths.

    Returns:
    str: Path to the final output PDF file after processing.
    """
    settings["progress"] = 20
    try:
        pages = settings.get("pages", "all")
        output_path = settings.get("pdf_path")
        converter = Converter(pdf_file=output_path)
        final_output_path = output_path.replace(".pdf", "_compressed.pdf")
        if pages not in ("all", ""):
            pages = parse_and_adjust_indices(pages)
            logging.debug(f"После парсинга страницы: {pages}")
            logging.debug(f"Страницы для обработки: {pages}")
        mode = settings.get("mode")
        is_compression_needed = settings.get("is_compression_needed")
        if not mode == "compress_mode":
            if mode == "grayscale_mode":
                output_path = "Temp.pdf"
                final_output_path = settings.get("pdf_path").replace(
                    ".pdf", "_grayscale.pdf")
                if not is_compression_needed:
                    output_path = final_output_path

            grayscale = mode == "grayscale_mode"
            logging.info("Преобразуем PDF в черно-белый")
            temp_images = converter.pdf_to_png(
                grayscale=grayscale, pages_to_convert=pages)
            settings["progress"] = 50
            if mode == "convert_to_png_mode":
                settings["progress"] = 100
                return None
            converter.pngs_to_pdf(output_path, temp_images)
            logging.info("Сгенерирован временный PDF")
            settings["progress"] = 80
        if is_compression_needed:
            converter.compress_pdf(
                input_pdf=output_path, output_pdf=final_output_path)
            logging.info("Сжатие завершено")
        settings["progress"] = 100
    except Exception as error:
        logging.error(f"При выполнении программы возникла ошибка: {error}")
    finally:
        if mode == "grayscale_mode":
            converter.clean_temp_files()
            logging.info("Временные файлы удалены")
        if mode not in ("grayscale_mode", "compress_mode"):
            final_output_path = None
        return final_output_path


def work_process(settings: dict) -> None:
    """
    Main process that handles different modes of processing DOCX or PDF files.

    Parameters:
    settings (dict): Dictionary containing the mode and other parameters
    for processing.

    Returns:
    None
    """
    logging.info("Начало программы")
    logging.info(f"settings = {settings}")
    is_compression_needed = settings.get("is_compression_needed")
    if settings.get("mode") in ("default_mode", "custom_mode",
                                "convert_to_pdf_mode"):
        final_output_path = docx_modes(settings)
    elif settings.get("mode") == "merge_pdf":
        settings["progress"] = 10
        merge_multiple_pdfs(*settings.get("parameters"))
        final_output_path = "merged_output.pdf"
        if is_compression_needed:
            final_output_path = "merged_and_compressed_output.pdf"
            Converter.compress_pdf(
                input_pdf="merged_output.pdf", output_pdf=final_output_path)
            logging.info("Сжатие завершено")
            if os.path.exists("merged_output.pdf"):
                logging.info('Удаляем файл "merged_output.pdf"')
                os.remove("merged_output.pdf")
    elif settings.get("mode") in ("grayscale_mode", "convert_to_png_mode",
                                  "compress_mode"):
        final_output_path = pdf_modes(settings)

    if not final_output_path:
        return
    if os.path.exists("acrobat_path.txt"):
        logging.debug('Проверяем наличие файла acrobat_path.txt')
        with open("acrobat_path.txt", "r", encoding="utf-8") as file:
            acrobat_path, page = [row.strip() for row in file.readlines()]
            logging.debug(f"Получены пути: {acrobat_path}, {page}")
    else:
        logging.debug(
            "Файл acrobat_path.txt не найден, используем путь по умолчанию")
        acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
        page = 1

    try:
        system = platform.system()
        if system == "Windows":
            os.system(
                f'start "" "{acrobat_path}" /A "page={page}" '
                f'"{final_output_path}"'
                )
        elif system == "Darwin":  # macOS
            os.system(f'open -a "Preview" "{final_output_path}"')
        elif system == "Linux":
            os.system(f'xdg-open "{final_output_path}"')
        logging.info(
            f"Файл {final_output_path} открыт в приложении для PDF на {system}")
    except Exception as error:
        logging.error(f"Ошибка при открытии файла: {error}")

    if os.path.exists(final_output_path):
        logging.info("Итоговый файл успешно создан. Удаляем log-файл.")
        if os.path.exists('app.log'):
            logging.shutdown()
            logging.disable(logging.CRITICAL)
            os.remove('app.log')
