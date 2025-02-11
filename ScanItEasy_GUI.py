import logging
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from ScanItEasy_backend import parse_and_adjust_indices, work_process

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


def resource_path(relative_path: str) -> str:
    """
        Gets the absolute path to a resource, working in both dev and bundled
        modes.

        Parameters:
        relative_path (str): The relative path to the resource.

        Returns:
        str: The absolute path to the resource.
        """
    try:
        # Если программа запущена как exe, то _MEIPASS указывает на путь
        # к распакованным ресурсам
        base_path = sys._MEIPASS
    except Exception:
        # Если это обычный скрипт, используем текущую директорию
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Оставляем наследование от CTk, чтобы быть окном
class GraphicalEditor(ctk.CTkToplevel):
    # Добавляем master как аргумент конструктора
    def __init__(self, master: tk.Tk | None = None) -> None:
        """
        Initializes the graphical editor window with a dark theme, default
        color, and specified master window.

        Args:
            master: The parent window, default is None for standalone window.
        """
        super().__init__(master)  # Передаем master в CTk
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('green')
        self.title("ScanItEasy")
        window_position_horizontal = 400
        window_position_vertical = 10
        self.geometry(
            f'{700}x{600}+{window_position_horizontal}'
            f'+{window_position_vertical}')
        self.blocks = {}  # Используем словарь для хранения блоков
        self.block_id = -1  # Начальный индекс-ключ для блока
        self.flag = True

        self.configure_grid()
        self.create_widgets()

        # Обработчик закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_grid(self) -> None:
        """
        Configures the grid layout of the window with specific row and column
        configurations.
        """
        self.grid_columnconfigure(0, weight=1)  # Столбец 0 растягивается
        # Верхняя строка не будет растягиваться
        self.grid_rowconfigure(0, weight=0)
        # Верхняя строка не будет растягиваться
        self.grid_rowconfigure(1, weight=0)
        # Нижняя строка будет растягиваться
        self.grid_rowconfigure(2, weight=1)

    def on_close(self) -> None:
        """
        Closes the graphical editor window and the parent window if it exists.
        """
        # Закрываем основное окно, когда закрывается это окно
        if self.master:
            self.master.destroy()
        self.destroy()  # Закрываем это окно

    def create_widgets(self) -> None:
        """
        Creates all the widgets (buttons, labels, checkboxes, etc.)
        in the window.
        """
        # Кнопка "Назад"
        light_image = tk.PhotoImage(file=resource_path("light.png"))
        dark_image = tk.PhotoImage(file=resource_path("dark.png"))

        def on_hover(event):
            back_button.config(image=dark_image)

        def on_leave(event):
            back_button.config(image=light_image)

        back_button = tk.Button(
            self, image=light_image, text="Назад",
            font=("Arial", 14, "normal"),
            fg="white", padx=10, pady=10, bg=self["bg"],
            activebackground=self["bg"],
            borderwidth=0, command=self.on_back_button_click, compound="left",
            relief="flat"
        )

        back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")

        back_button.bind("<Enter>", on_hover)
        back_button.bind("<Leave>", on_leave)

        # Заголовок
        header_label = ctk.CTkLabel(
            self, text="Объединить два или более pdf-файлов",
            font=("Arial", 17, "bold"))
        header_label.grid(row=1, column=0)

        self.is_compression_needed = ctk.BooleanVar(value=True)
        is_compression_needed_checkbox = ctk.CTkCheckBox(
            self, text="Сжать итоговый pdf",
            variable=self.is_compression_needed)
        is_compression_needed_checkbox.grid(
            row=1001, column=0, padx=padx, pady=5, sticky="w")
        is_compression_needed_checkbox.configure(
            command=lambda: logging.debug(
                f"Compression needed: {self.is_compression_needed.get()}"))

        # Кнопка добавления блока
        add_block_button = ctk.CTkButton(
            self, text="Добавить файл", command=self.add_block
        )
        add_block_button.grid(row=1002, column=0, pady=5, padx=70, sticky="ew")

        # Кнопка "Объединить"
        merge_button = ctk.CTkButton(
            self, text="Объединить", width=250, fg_color="red",
            hover_color="#8B0000", command=self.merge
        )
        merge_button.grid(row=1003, column=0, pady=5, padx=70, sticky="ew")

        # Фрейм для блоков
        self.blocks_frame = ctk.CTkScrollableFrame(self)
        self.blocks_frame.grid(
            row=2, column=0, sticky="nsew", padx=50, pady=10)

        # Привязываем обработчик события клика по окну для проверки всех полей
        self.bind("<Button-1>", self.on_click)

    def on_back_button_click(self) -> None:
        """
        Closes the current window and restores the parent window.
        """
        # Скрываем текущее окно (GraphicalEditor) при нажатии кнопки "Назад"
        self.destroy()

        # Восстанавливаем родительское окно (ModesWindow) и делаем его активным
        self.master.deiconify()

    def on_click(self, event: tk.Event) -> None:
        """
        Validates input fields when the user clicks anywhere in the window.

        Args:
            event: The click event that triggered the function.
        """
        for index, block in self.blocks.items():
            entry_widget = block["pages_entry"]
            pages_entry_error_label = block["pages_entry_error_label"]
            self.validate_entry(entry_widget, pages_entry_error_label)

    def check_block(self) -> bool:
        """
        Checks if a block is properly filled with a file and its pages.

        Returns:
            bool: True if block is valid, False otherwise.
        """
        if (self.blocks and self.blocks[self.block_id]["file_label"].cget(
                "text") != "Файл не выбран"):
            return True
        for block_id in self.blocks.keys():
            if (self.blocks and self.blocks[block_id]["file_label"].cget(
                    "text") == "Файл не выбран"):
                self.blocks[block_id]["file_label"].grid_remove()
                self.blocks[block_id]["file_path_empty_error_label"].grid(
                    row=0, column=1, sticky="w", padx=10, pady=0)
        return False

    def add_block(self) -> None:
        """
        Adds a new block for file selection and page input in the window.
        """
        # Сначала проверяем все поля ввода
        if not self.check_all_entries_valid():
            return

        if self.flag or self.check_block():
            self.flag = False
            self.block_id += 1  # Генерация уникального ID для блока
            block_id = self.block_id

            # Создание фрейма для нового блока
            block_frame = ctk.CTkFrame(self.blocks_frame)
            block_frame.grid(
                row=self.block_id, column=0, pady=5, padx=5, sticky="ew")
            block_frame.grid_columnconfigure(1, weight=1)

            # Метка для отображения имени файла
            file_label = ctk.CTkLabel(block_frame, text="Файл не выбран")
            file_label.grid(row=0, column=1, padx=10, sticky="w")

            # Кнопка выбора файла
            select_button = ctk.CTkButton(
                block_frame, text="Выбрать файл",
                command=lambda: self.select_file(block_id)
            )
            select_button.grid(row=0, column=0, padx=10, sticky="w")

            # Кнопка удаления блока
            delete_button = ctk.CTkButton(
                block_frame,
                text="X",  # Текст кнопки
                font=("Arial", 17, "bold"),  # Шрифт: Arial, размер 14, жирный
                fg_color=block_frame["bg"],  # Цвет фона кнопки
                text_color="white",  # Цвет текста
                hover_color="red",  # Цвет при наведении
                width=30,  # Ширина кнопки
                height=30,  # Высота кнопки
                command=lambda: self.delete_block(block_id)
                )
            delete_button.grid(row=0, column=2, padx=10, sticky="e")

            # Лейбл для ошибок
            file_path_empty_error_label = ctk.CTkLabel(
                block_frame, text="Выберите файл", text_color="red",
                font=("Arial", 12))

            pages_entry = ctk.CTkEntry(
                block_frame,
                placeholder_text=("Введите номера страниц через запятую "
                                  "и/или диапазон через дефис"),
                fg_color="lightgray",                # Цвет фона
                placeholder_text_color="Gray",
                text_color="black",                  # Цвет текста
                width=430,                           # Ширина поля
                corner_radius=10,                    # Скругленные углы
                font=("Arial", 12),                   # Шрифт текста
                )
            pages_entry.grid(
                row=2, column=0, sticky="w", columnspan=3, pady=5, padx=10)

            # Лейбл для сообщения-инструкции
            entry_label = ctk.CTkLabel(
                block_frame,
                text="Если нужны все страницы, оставьте поле пустым",
                font=("Arial", 12, "italic"), text_color="#2FA572",
                justify='center')
            entry_label.grid(
                row=3, column=0, columnspan=3, sticky="w", pady=0, padx=10)

            # Лейбл для ошибок
            pages_entry_error_label = ctk.CTkLabel(
                block_frame, text="", text_color="red", font=("Arial", 10))
            pages_entry_error_label.grid(
                row=4, column=0, columnspan=3, sticky="w", padx=10)

            pages_entry.bind(
                "<FocusOut>", lambda event, entry=pages_entry,
                label=pages_entry_error_label: self.validate_entry(
                    entry, label))
            pages_entry.bind(
                "<ButtonRelease-1>", lambda event,
                entry=pages_entry,
                label=pages_entry_error_label: self.validate_entry(
                    entry, label))

            # Изначальная подсветка поля на зелёный
            pages_entry.configure(fg_color="#DEFCD4")

            # Сохранение блока в словаре
            self.blocks[self.block_id] = {
                "frame": block_frame,
                "file_path": "",
                "file_label": file_label,
                "file_path_empty_error_label": file_path_empty_error_label,
                "pages_entry": pages_entry,
                "pages_entry_error_label": pages_entry_error_label
            }

            # Логирование: создаём новый блок
            logging.debug(f"Создан новый блок с block_id={self.block_id}")

        else:
            return

    def validate_entry(
            self, entry_widget: ctk.CTkEntry,
            pages_entry_error_label: ctk.CTkLabel) -> None:
        """
        Validates the input in the pages entry field and shows an error message
        if needed.

        Args:
            entry_widget: The entry widget containing the input to validate.
            pages_entry_error_label: The label where error messages are
            displayed.
        """
        entered_text = entry_widget.get()

        # Проверка данных
        if self.validate_input_pages(entered_text):
            # Зеленый цвет при корректном вводе
            entry_widget.configure(fg_color="#DEFCD4")
            pages_entry_error_label.configure(text="")  # Очищаем ошибку
        else:
            # Красный цвет при ошибке
            entry_widget.configure(fg_color="lightcoral")
            pages_entry_error_label.configure(
                text=("Введите номера страниц через запятую и/или диапазон "
                      "через дефис"))  # Сообщение об ошибке

    def check_all_entries_valid(self) -> bool:
        """
        Checks if all blocks have valid input for pages.

        Returns:
            bool: True if all entries are valid, False otherwise.
        """
        for index, block in self.blocks.items():
            entry_widget = block["pages_entry"]
            entered_text = entry_widget.get()
            pages_entry_error_label = block["pages_entry_error_label"]
            if not self.validate_input_pages(entered_text):
                # Красный цвет при ошибке
                entry_widget.configure(fg_color="lightcoral")
                pages_entry_error_label.configure(
                    text=("Введите номера страниц через запятую и/или "
                          "диапазон через дефис"))
                return False
        return True

    def validate_input_pages(self, text: str) -> bool:
        """
        Validates the page input format (numbers or ranges of pages).

        Args:
            text: The string containing the page numbers or ranges.

        Returns:
            bool: True if the input is valid, False otherwise.
        """
        if not text:
            return True
        parts = [part.strip() for part in text.split(",")]

        for part in parts:
            if "-" in part:
                range_parts = part.split("-")
                if len(range_parts) != 2:
                    return False
                try:
                    start = int(range_parts[0].strip())
                    end = int(range_parts[1].strip())
                    if start >= end:
                        return False
                except ValueError:
                    return False
            else:
                try:
                    int(part)
                except ValueError:
                    return False
        return True

    def select_file(self, block_id: int) -> None:
        """
        Opens a file dialog to select a PDF file and updates the block with
        the selected file.

        Args:
            block_id: The ID of the block being updated with the selected file.
        """
        file_path = filedialog.askopenfilename(
            title="Выберите файл", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            file_name = os.path.basename(file_path)

            # Если длина имени файла больше 50 символов, обрезаем его
            if len(file_name) > 50:
                # 25 символов с начала и 20 символов с конца
                file_name = file_name[:25] + " . . . " + file_name[-20:]

            # Записываем file_path в словарь
            self.blocks[block_id]["file_path"] = file_path

            # Обновляем метку с именем файла
            self.blocks[block_id]["file_label"].configure(text=file_name)
            self.blocks[block_id]
            ["file_label"].grid(row=0, column=1, padx=10, sticky="w")

            # Убираем лейбл с ошибкой
            self.blocks[block_id]
            ["file_path_empty_error_label"].grid_remove()

    def delete_block(self, block_id: int) -> None:
        """
        Deletes a block with the specified block ID.

        Args:
            block_id: The ID of the block to be deleted.
        """
        if block_id in self.blocks:
            block = self.blocks.pop(block_id)
            file_label_text = block["file_label"].cget("text")
            pages_text = block["pages_entry"].get()

            # Логирование: удаляем блок
            logging.debug(
                f"Удален блок с block_id={block_id}, "
                f"file_label =' {file_label_text}', "
                f"pages_entry='{pages_text}'")

            block["frame"].destroy()

            # Логирование: текущее состояние блоков
            logging.debug("После удаления блоков:")
            for b_id, b_data in self.blocks.items():
                file_label = b_data["file_label"].cget("text")
                pages_text = b_data["pages_entry"].get()
                logging.debug(
                    f"  block_id={b_id}, file_label='{file_label}', "
                    f"pages_entry='{pages_text}'")

            if not self.blocks:
                self.flag = True

    def merge(self) -> None:
        """
        Merges the selected PDF files with the specified page ranges and
        compression option.
        """
        self.check_block()
        if not self.check_all_entries_valid():
            return
        data = {
            block_id: {
                "file_path": block["file_path"],
                "pages_entry": block["pages_entry"].get()
            }
            for block_id, block in self.blocks.items() if block["file_path"]
        }
        if len(data) < 2:
            return
        user_input_data = {}
        user_input_data["mode"] = "merge_pdf"

        files = []
        pages = []

        for block in data.values():
            files.append(block["file_path"])
            if block["pages_entry"]:
                pages.append(parse_and_adjust_indices(block["pages_entry"]))
            else:
                pages.append('')

        user_input_data["parameters"] = (files, pages, "merged_output.pdf")
        user_input_data["is_compression_needed"] = (
            self.is_compression_needed.get())
        logging.debug(
            f"self.is_compression_needed.get() = "
            f"{self.is_compression_needed.get()}")

        # Запускаем задачу в отдельном потоке
        task_thread = threading.Thread(
            target=work_process, args=(user_input_data,))
        task_thread.start()
        # Запускаем процесс обновления прогресса в основном потоке
        logging.debug(f"user_input_data = {user_input_data}")


# Глобальная переменная для окна
win = None
# Глобальная переменная для экземпляра класса ModesWindow
obj = None
# Глобальная переменная режима работы программы
current_mode = "modes"

padx = 70

# Инициализируем словари с данными глобально
elements = mode_settings = user_input = None

# Глобальные переменные для виджетов
mode_var = btn_file_last_page = convert_to_png = None
mode_label = default_mode = custom_mode = additionally_label = None
convert_to_pdf = merge_pdf = grayscale_mode = compress_mode = None
invalid_last_page_label = dark_image = light_image = header_label = None
btn_file_docx = docx_label = invalid_docx_label = back_button = None
progress_label = progress_bar = conditions_message_label = 3
btn_to_work = color_var = color_label = red = blue = None
pages_label = text_help_label = pages = invalid_pages_label = None
signature_var = signature_label = signature_yes = signature_no = None
is_compression_needed = is_compression_needed_checkbox = None
btn_file_pdf = pdf_label = invalid_pdf_label = last_page_label = None


class ModesWindow(ctk.CTkFrame):
    def __init__(self, master: tk.Tk) -> None:
        """
        Initializes the ModesWindow, which is a frame in the main application.

        Args:
            master: The parent window (main application window).
        """
        super().__init__(master)
        self.app = master  # Сохраняем ссылку на родительское окно
        global win, obj
        win = self.app
        obj = self

        # Устанавливаем размеры и позицию окна
        self.window_width = 400
        self.window_height = 350
        self.window_position_horizontal = 400
        self.window_position_vertical = 10
        self.master.geometry(
            f'{self.window_width}x{self.window_height}'
            f'+{self.window_position_horizontal}'
            f'+{self.window_position_vertical}')
        self.master.minsize(300, 300)
        self.master.title("ScanItEasy")
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('green')

        create_widgets()
        # Добавляем кнопку для объединения PDF


def create_widgets() -> None:
    """
    Creates all the widgets for the ModesWindow, such as labels, buttons,
    and radio buttons, and sets up their layout.
    """
    global elements, mode_label, default_mode, custom_mode, additionally_label
    global convert_to_pdf, last_page_label, dark_image, light_image, pages
    global grayscale_mode, compress_mode, convert_to_png, back_button
    global header_label, btn_file_docx, docx_label, invalid_docx_label
    global progress_label, progress_bar, conditions_message_label, btn_to_work
    global color_var, color_label, red, blue, pages_label, text_help_label
    global invalid_pages_label, signature_var, signature_label, signature_yes
    global signature_no, pdf_label, invalid_pdf_label, user_input, merge_pdf
    global is_compression_needed, is_compression_needed_checkbox, btn_file_pdf
    global mode_var, color_var, signature_var, is_compression_needed
    global win, mode_settings, invalid_last_page_label, btn_file_last_page
    # Переменные
    mode_var = ctk.StringVar(value="modes")
    color_var = ctk.StringVar(value="red")
    signature_var = ctk.IntVar(value=0)
    is_compression_needed = ctk.BooleanVar(value=True)

    # Визуальные элементы
    mode_label = ctk.CTkLabel(win, text="Выберите опцию")
    mode_label.grid(row=0, column=0, padx=70, pady=15, sticky="w")

    # имы
    default_mode = ctk.CTkRadioButton(
        win, text="Режим по умолчанию", variable=mode_var,
        value="default_mode",
        command=lambda: update_elements(mode_var.get()))
    default_mode.grid(row=1, column=0, padx=70, pady=5, sticky="w")

    custom_mode = ctk.CTkRadioButton(
        win, text="Пользовательский режим с настройками",
        variable=mode_var, value="custom_mode",
        command=lambda: update_elements(mode_var.get()))
    custom_mode.grid(row=2, column=0, padx=70, pady=5, sticky="w")

    additionally_label = ctk.CTkLabel(
        win, text="Дополнительно:", font=("Arial", 12, "italic"),
        justify='center')
    additionally_label.grid(row=3)

    convert_to_pdf = ctk.CTkRadioButton(
        win, text="Конвертировать docx в pdf", variable=mode_var,
        value="convert_to_pdf_mode",
        command=lambda: update_elements(mode_var.get()))
    convert_to_pdf.grid(row=4, column=0, padx=70, pady=5, sticky="w")

    merge_pdf = ctk.CTkRadioButton(
        win, text="Объединить два или несколько pdf", variable=mode_var,
        value="merge_pdf_mode",
        command=lambda: on_merge_pdf_button_click(obj))
    merge_pdf.grid(row=5, column=0, padx=70, pady=5, sticky="w")

    grayscale_mode = ctk.CTkRadioButton(
        win, text="Сделать pdf чёрно-белым", variable=mode_var,
        value="grayscale_mode",
        command=lambda: update_elements(mode_var.get()))
    grayscale_mode.grid(row=6, column=0, padx=70, pady=5, sticky="w")

    compress_mode = ctk.CTkRadioButton(
        win, text="Сжать pdf", variable=mode_var, value="compress_mode",
        command=lambda: update_elements(mode_var.get()))
    compress_mode.grid(row=7, column=0, padx=70, pady=5, sticky="w")

    convert_to_png = ctk.CTkRadioButton(
        win, text="Конвертировать pdf в png", variable=mode_var,
        value="convert_to_png_mode",
        command=lambda: update_elements(mode_var.get()))
    convert_to_png.grid(row=8, column=0, padx=70, pady=5, sticky="w")

    # пка Назад
    light_image = tk.PhotoImage(file=resource_path("light.png"))
    dark_image = tk.PhotoImage(file=resource_path("dark.png"))

    back_button = tk.Button(
        win,
        image=light_image,
        text="Назад",
        font=("Arial", 14, "normal"),
        fg="white",
        padx=10,
        pady=10,
        bg=win["bg"],  # Цвет фона кнопки подстраивается под фон окна
        activebackground=win["bg"],  # Цвет фона кнопки при наведении
        borderwidth=0,  # Убираем рамку
        command=lambda: update_elements("modes"),
        compound="left",
        relief="flat"
    )

    def on_hover(event: tk.Event) -> None:
        "Changes the back button image to the dark version on hover."
        back_button.config(image=dark_image)

    def on_leave(event: tk.Event) -> None:
        "Resets the back button image to the light version when hover ends."
        back_button.config(image=light_image)

    # кции для обработки кнопки назад
    back_button.bind("<Enter>", on_hover)
    back_button.bind("<Leave>", on_leave)

    # им по умолчанию
    header_label = ctk.CTkLabel(win, text="Режим по умолчанию")

    btn_file_docx = ctk.CTkButton(
        win, text="Выберите файл для сканирования",
        command=lambda: update_file_label(
            docx_label, ["docx"], invalid_docx_label))

    docx_label = ctk.CTkLabel(win, text=None)

    invalid_docx_label = ctk.CTkLabel(
        win, text="Файл должен быть формата docx", text_color="red", padx=20)

    # ьзовательский режим с настройками
    color_label = ctk.CTkLabel(
        win, text="Выберите цвет ленточки")

    red = ctk.CTkRadioButton(
        win, text="Красный", variable=color_var, value="red",
        command=lambda: logging.debug("Цвет ленты: красный"))

    blue = ctk.CTkRadioButton(
        win, text="Синий", variable=color_var, value="blue",
        command=lambda: logging.debug("Цвет ленты: Синий"))

    pages_label = ctk.CTkLabel(win, text="Выберите страницы")

    text_help_label = ctk.CTkLabel(
        win,
        text="Если нужны все страницы, оставьте поле пустым",
        font=("Arial", 12, "italic"), text_color="green", justify='center')

    pages = ctk.CTkEntry(
        win,
        placeholder_text=("Введите номера страниц через "
                          "запятую и/или диапазон страниц "
                          "через дефис"),
        fg_color="lightgray",                # Цвет фона
        placeholder_text_color="Gray",
        text_color="black",                  # Цвет текста
        width=470,                           # Ширина поля
        corner_radius=10,                    # Скругленные углы
        font=("Arial", 12),                   # Шрифт текста
    )

    invalid_pages_label = ctk.CTkLabel(
        win,
        text=("Введите номера страниц через запятую и/или диапазон "
              "страниц через дефис"),
        text_color="red", padx=20)

    # signature_label = ctk.CTkLabel(
    # win, text="Нужна ли подпись переводчика?")

    # signature_yes = ctk.CTkRadioButton(
    # win, text="Да", variable=signature_var, value=1,
    # command=lambda: logging.debug("Подпись переводчика нужна"))

    # signature_no = ctk.CTkRadioButton(
    # win, text="Нет", variable=signature_var, value=0,
    # command=lambda: logging.debug("Подпись переводчика не нужна"))

    # Режим конвертации из docx в pdf
    is_compression_needed_checkbox = ctk.CTkCheckBox(
        win, text="Сжать итоговый pdf", variable=is_compression_needed)

    # пка для выбора файла pdf
    btn_file_pdf = ctk.CTkButton(
        win, text="Выберите pdf-файл",
        command=lambda: update_file_label(
            pdf_label, ["pdf"], invalid_pdf_label))

    last_page_label = ctk.CTkLabel(win, text=None)
    logging.debug(f"last_page_label = {last_page_label}")
    btn_file_last_page = ctk.CTkButton(
        win, text="Выберите файл для последней части документа",
        command=lambda: update_file_label(
            last_page_label, ["pdf", "jpeg", "jpg", "png"],
            invalid_last_page_label))

    pdf_label = ctk.CTkLabel(win, text=None)

    invalid_pdf_label = ctk.CTkLabel(
        win, text="Файл должен быть формата pdf", text_color="red", padx=20)

    invalid_last_page_label = ctk.CTkLabel(
        win, text="Файл должен быть формата pdf, jpeg, jpg или png",
        text_color="red", padx=20)

    btn_to_work = ctk.CTkButton(win, fg_color="red",  # Основной цвет кнопки
                                hover_color="#8B0000",
                                text="Сканировать", command=lambda: work())
    conditions_message_label = ctk.CTkLabel(
        win,
        text="Для запуска сканирования нужно выбрать файл в формате docx",
        text_color="red", padx=20)
    progress_label = ctk.CTkLabel(win, text="0%")
    progress_bar = ctk.CTkProgressBar(win, width=300, height=25)

    # Привязка события для проверки при клике на любое место
    win.bind("<Button-1>", on_click)  # Привязка на клик по окну
    pages.bind("<FocusOut>", on_validate)

    elements = {
        "modes": {
            mode_label: ('mode_label.grid(row=0, column=0, padx=padx, '
                         'pady=15, sticky="w")'),
            default_mode: ('default_mode.grid(row=1, column=0, padx=padx, '
                           'pady=5, sticky="w")'),
            custom_mode: ('custom_mode.grid(row=2, column=0, padx=padx, '
                          'pady=5, sticky="w")'),
            additionally_label: 'additionally_label.grid(row=3)',
            convert_to_pdf: ('convert_to_pdf.grid(row=4, column=0, padx=padx, '
                             'pady=5, sticky="w")'),
            merge_pdf: ('merge_pdf.grid(row=5, column=0, padx=padx, pady=5, '
                        'sticky="w")'),
            grayscale_mode: ('grayscale_mode.grid(row=6, column=0, padx=padx, '
                             'pady=5, sticky="w")'),
            compress_mode: ('compress_mode.grid(row=7, column=0, padx=padx, '
                            'pady=5, sticky="w")'),
            convert_to_png: ('convert_to_png.grid(row=8, column=0, padx=padx, '
                             'pady=5, sticky="w")')
        },
        "default_mode": {
            back_button: (
                'back_button.grid(row=0, column=0, padx=35, '
                'pady=5, sticky="w")'
            ),
            header_label: (
                'header_label.grid(row=1, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            btn_file_docx: (
                'btn_file_docx.grid(row=2, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            btn_file_last_page: (
                'btn_file_last_page.grid(row=4, column=0, '
                'padx=padx, pady=5, sticky="w")'
            ),
            btn_to_work: (
                'btn_to_work.grid(row=8, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            "start_settings": [
                'color_var.set("red")', 'signature_var.set(0)',
                'docx_label.configure(text=None)',
                'last_page_label.configure(text=None)'
            ],
            "additional_elements": {
                "error_messages": {
                    invalid_docx_label: (
                        'invalid_docx_label.grid(row=3, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    invalid_last_page_label: (
                        'invalid_last_page_label.grid(row=5, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    )
                },
                "next_step_elements": {
                    docx_label: (
                        'docx_label.grid(row=3, column=0, padx=padx, '
                        'pady=5, sticky="w")'
                    ),
                    last_page_label: (
                        'last_page_label.grid(row=5, column=0, '
                        'padx=padx, pady=5, sticky="w")'
                    ),
                    progress_label: (
                        'progress_label.grid(row=6, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    progress_bar: (
                        'progress_bar.grid(row=7, column=0, pady=5, '
                        'padx=padx, sticky="w")'
                    ),
                    conditions_message_label: (
                        'conditions_message_label.grid(row=6, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    )
                }
            },
            "work_conditions": (docx_label,)
        },
        "custom_mode": {
            back_button: (
                'back_button.grid(row=0, column=0, padx=35, '
                'pady=5, sticky="w")'
            ),
            header_label: (
                'header_label.grid(row=1, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            btn_file_docx: (
                'btn_file_docx.grid(row=2, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            pages_label: (
                'pages_label.grid(row=4, column=0, padx=padx, '
                'pady=0, sticky="w")'
            ),
            text_help_label: (
                'text_help_label.grid(row=5, column=0, padx=padx, '
                'pady=0, sticky="w")'
            ),
            pages: (
                'pages.grid(row=6, column=0, padx=padx, pady=5, '
                'sticky="w")'
            ),
            btn_file_last_page: (
                'btn_file_last_page.grid(row=8, column=0, '
                'padx=padx, pady=(20, 5), sticky="w")'
            ),
            color_label: (
                'color_label.grid(row=10, column=0, padx=padx, '
                'pady=10, sticky="w")'
            ),
            red: (
                'red.grid(row=11, column=0, padx=padx, pady=5, '
                'sticky="w")'
            ),
            blue: (
                'blue.grid(row=12, column=0, padx=padx, '
                'pady=(5, 15), sticky="w")'
            ),
            btn_to_work: (
                'btn_to_work.grid(row=18, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            "start_settings": [
                'color_var.set("red")', 'signature_var.set(0)',
                'docx_label.configure(text=None)',
                'last_page_label.configure(text=None)',
                'pages.delete(0, "end")'
            ],
            "additional_elements": {
                "error_messages": {
                    invalid_docx_label: (
                        'invalid_docx_label.grid(row=3, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    invalid_last_page_label: (
                        'invalid_last_page_label.grid(row=9, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    invalid_pages_label: (
                        'invalid_pages_label.grid(row=7, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    )
                },
                "next_step_elements": {
                    docx_label: (
                        'docx_label.grid(row=3, column=0, padx=padx, '
                        'pady=5, sticky="w")'
                    ),
                    last_page_label: (
                        'last_page_label.grid(row=9, column=0, '
                        'padx=padx, pady=5, sticky="w")'
                    ),
                    progress_label: (
                        'progress_label.grid(row=16, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    progress_bar: (
                        'progress_bar.grid(row=17, column=0, pady=5, '
                        'padx=padx, sticky="w")'
                    ),
                    conditions_message_label: (
                        'conditions_message_label.grid(row=16, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    )
                }
            },
            "work_conditions": (docx_label,),
            "inhibitors": {
                invalid_docx_label: (
                    'Для запуска сканирования нужно выбрать файл в '
                    'формате docx'
                ),
                invalid_pages_label: (
                    'Введите номера страниц через запятую и/или '
                    'диапазон страниц через дефис'
                )
            }
        },
        "convert_to_pdf_mode": {
            back_button: (
                'back_button.grid(row=0, column=0, padx=35, '
                'pady=5, sticky="w")'
            ),
            header_label: (
                'header_label.grid(row=1, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            btn_file_docx: (
                'btn_file_docx.grid(row=2, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            pages_label: (
                'pages_label.grid(row=4, column=0, padx=padx, '
                'pady=0, sticky="w")'
            ),
            text_help_label: (
                'text_help_label.grid(row=5, column=0, padx=padx, '
                'pady=0, sticky="w")'
            ),
            pages: (
                'pages.grid(row=6, column=0, padx=padx, pady=5, '
                'sticky="w")'
            ),
            is_compression_needed_checkbox: (
                'is_compression_needed_checkbox.grid(row=8, column=0, '
                'padx=padx, pady=5, sticky="w")'
            ),
            btn_to_work: (
                'btn_to_work.grid(row=18, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            "start_settings": [
                'docx_label.configure(text=None)',
                'is_compression_needed.set(True)',
                'pages.delete(0, "end")'
            ],
            "additional_elements": {
                "error_messages": {
                    invalid_docx_label: (
                        'invalid_docx_label.grid(row=3, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    invalid_pages_label: (
                        'invalid_pages_label.grid(row=7, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    )
                },
                "next_step_elements": {
                    docx_label: (
                        'docx_label.grid(row=3, column=0, padx=padx, '
                        'pady=5, sticky="w")'
                    ),
                    progress_label: (
                        'progress_label.grid(row=9, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    progress_bar: (
                        'progress_bar.grid(row=10, column=0, pady=5, '
                        'padx=padx, sticky="w")'
                    ),
                    conditions_message_label: (
                        'conditions_message_label.grid(row=16, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    )
                }
            },
            "work_conditions": (docx_label,),
            "inhibitors": {
                invalid_docx_label: (
                    'Для конвертации нужно выбрать файл в формате docx'
                ),
                invalid_pages_label: (
                    'Введите номера страниц через запятую и/или '
                    'диапазон страниц через дефис'
                )
            }
        },
        "grayscale_mode": {
            back_button: (
                'back_button.grid(row=0, column=0, padx=35, '
                'pady=5, sticky="w")'
            ),
            header_label: (
                'header_label.grid(row=1, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            btn_file_pdf: (
                'btn_file_pdf.grid(row=2, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            pages_label: (
                'pages_label.grid(row=4, column=0, padx=padx, '
                'pady=0, sticky="w")'
            ),
            text_help_label: (
                'text_help_label.grid(row=5, column=0, padx=padx, '
                'pady=0, sticky="w")'
            ),
            pages: (
                'pages.grid(row=6, column=0, padx=padx, pady=5, '
                'sticky="w")'
            ),
            is_compression_needed_checkbox: (
                'is_compression_needed_checkbox.grid(row=8, column=0, '
                'padx=padx, pady=5, sticky="w")'
            ),
            btn_to_work: (
                'btn_to_work.grid(row=18, column=0, padx=padx, '
                'pady=5, sticky="w")'
            ),
            "start_settings": [
                'docx_label.configure(text=None)',
                'is_compression_needed.set(True)',
                'pages.delete(0, "end")'
            ],
            "additional_elements": {
                "error_messages": {
                    invalid_pdf_label: (
                        'invalid_pdf_label.grid(row=3, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    invalid_pages_label: (
                        'invalid_pages_label.grid(row=7, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    )
                },
                "next_step_elements": {
                    pdf_label: (
                        'pdf_label.grid(row=3, column=0, padx=padx, '
                        'pady=5, sticky="w")'
                    ),
                    progress_label: (
                        'progress_label.grid(row=9, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    ),
                    progress_bar: (
                        'progress_bar.grid(row=10, column=0, pady=5, '
                        'padx=padx, sticky="w")'
                    ),
                    conditions_message_label: (
                        'conditions_message_label.grid(row=16, column=0, '
                        'pady=5, padx=padx, sticky="w")'
                    )
                }
            },
            "work_conditions": (pdf_label,),
            "inhibitors": {
                invalid_pdf_label: (
                    'Для конвертации нужно выбрать файл в формате pdf'
                ),
                invalid_pages_label: (
                    'Введите номера страниц через запятую и/или '
                    'диапазон страниц через дефис'
                )
            }
        },
        "compress_mode": {
            back_button: ('back_button.grid(row=0, column=0, padx=35, '
                          'pady=5, sticky="w")'),
            header_label: ('header_label.grid(row=1, column=0, padx=padx, '
                           'pady=5, sticky="w")'),
            btn_file_pdf: ('btn_file_pdf.grid(row=2, column=0, padx=padx, '
                           'pady=5, sticky="w")'),
            btn_to_work: ('btn_to_work.grid(row=18, column=0, padx=padx, '
                          'pady=5, sticky="w")'),
            "start_settings": ['pdf_label.configure(text=None)',
                               'is_compression_needed.set(True)'],
            "additional_elements": {
                "error_messages": {
                    invalid_pdf_label: (
                        'invalid_pdf_label.grid(row=3, column=0, '
                        'pady=5, padx=padx, sticky="w")')
                },
                "next_step_elements": {
                    pdf_label: ('pdf_label.grid(row=3, column=0, padx=padx, '
                                'pady=5, sticky="w")'),
                    progress_label: ('progress_label.grid(row=9, column=0, '
                                     'pady=5, padx=padx, sticky="w")'),
                    progress_bar: (
                        'progress_bar.grid(row=10, column=0, pady=5, '
                        'padx=padx, sticky="w")'),
                    conditions_message_label: (
                        'conditions_message_label.grid(row=16, '
                        'column=0, pady=5, padx=padx, '
                        'sticky="w")')
                }
            },
            "work_conditions": (pdf_label,),
            "inhibitors": {
                invalid_pdf_label: ('Для конвертации нужно выбрать файл в '
                                    'формате pdf')
            }
        },
        "convert_to_png_mode": {
            back_button: ('back_button.grid(row=0, column=0, padx=35, '
                          'pady=5, sticky="w")'),
            header_label: ('header_label.grid(row=1, column=0, padx=padx, '
                           'pady=5, sticky="w")'),
            btn_file_pdf: ('btn_file_pdf.grid(row=2, column=0, padx=padx, '
                           'pady=5, sticky="w")'),
            btn_to_work: ('btn_to_work.grid(row=18, column=0, padx=padx, '
                          'pady=5, sticky="w")'),
            "additional_elements": {
                "error_messages": {
                    invalid_pdf_label: ('invalid_pdf_label.grid(row=3, '
                                        'column=0, pady=5, padx=padx, '
                                        'sticky="w")'),
                },
                "next_step_elements": {
                    pdf_label: ('pdf_label.grid(row=3, column=0, padx=padx, '
                                'pady=5, sticky="w")'),
                    progress_label: ('progress_label.grid(row=9, column=0, '
                                     'pady=5, padx=padx, sticky="w")'),
                    progress_bar: ('progress_bar.grid(row=10, column=0, '
                                   'pady=5, padx=padx, sticky="w")'),
                    conditions_message_label: (
                        'conditions_message_label.'
                        'grid(row=16, column=0, pady=5, padx=padx, '
                        'sticky="w")')
                }
            },
            "work_conditions": (pdf_label,),
            "inhibitors": {
                invalid_pdf_label: ("Для конвертации нужно выбрать файл в "
                                    "формате pdf")}
        },
    }

    mode_settings = {
        "default_mode": {
            header_label: "Режим по умолчанию",
            btn_file_docx: "Выберите файл для сканирования",
            btn_file_last_page: "Выберите файл для последней части документа",
            btn_to_work: "Сканировать",
            conditions_message_label: ("Для изменения нужно выбрать файл "
                                       "в формате docx"),
            progress_label: "0%",
        },
        "custom_mode": {
            header_label: "Пользовательский режим с настройками",
            btn_file_docx: "Выберите файл для сканирования",
            btn_file_last_page: "Выберите файл для последней части документа",
            btn_to_work: "Сканировать",
            conditions_message_label: ("Для изменения нужно выбрать файл "
                                       "в формате docx"),
            progress_label: "0%",
        },
        "convert_to_pdf_mode": {
            header_label: "Конвертация docx в pdf",
            btn_file_docx: "Выберите файл для конвертации в pdf",
            btn_to_work: "Конвертировать",
            conditions_message_label: ("Для изменения нужно выбрать файл "
                                       "в формате docx"),
            progress_label: "0%",
        },
        "grayscale_mode": {
            header_label: "Сделать pdf чёрно-белым",
            btn_file_pdf: "Выберите pdf-файл",
            btn_to_work: "Изменить",
            conditions_message_label: ("Для изменения нужно выбрать файл "
                                       "в формате pdf"),
            progress_label: "0%",
        },
        "compress_mode": {
            header_label: "Сжать pdf",
            btn_file_pdf: "Выберите pdf-файл",
            btn_to_work: "Сжать",
            conditions_message_label: ("Для сжатия нужно выбрать файл в "
                                       "формате pdf"),
            progress_label: "0%",
        },
        "convert_to_png_mode": {
            header_label: "Конвертировать pdf в png",
            btn_file_pdf: "Выберите pdf-файл",
            btn_to_work: "Конвертировать",
            conditions_message_label: ("Для конвертации нужно выбрать файл "
                                       "в формате pdf"),
            progress_label: "0%",
        }
    }

    user_input = {
        "default_mode": {
            "docx_path": 'docx_label.cget("text")',
            "last_page_path": 'last_page_label.cget("text")',
            "color": 'color_var.get()',
            "need_sign_translator": '0',
            "is_compression_needed": '1',
        },
        "custom_mode": {
            "docx_path": 'docx_label.cget("text")',
            "last_page_path": 'last_page_label.cget("text")',
            "color": 'color_var.get()',
            # "need_sign_translator": 'signature_var.get()',
            "need_sign_translator": '0',
            "pages": 'pages.get()',
            "is_compression_needed": '1',
        },
        "convert_to_pdf_mode": {
            "docx_path": 'docx_label.cget("text")',
            "pages": 'pages.get()',
            "is_compression_needed": 'is_compression_needed.get()',
        },
        "grayscale_mode": {
            "pdf_path": 'pdf_label.cget("text")',
            "is_compression_needed": 'is_compression_needed.get()',
            "pages": 'pages.get()',
        },
        "compress_mode": {
            "pdf_path": 'pdf_label.cget("text")',
            "is_compression_needed": '1',
        },
        "convert_to_png_mode": {
            "pdf_path": 'pdf_label.cget("text")',
        },
    }


def on_merge_pdf_button_click(obj: ModesWindow) -> None:
    """
    Handles the click of the merge PDF button. Hides current window and
    opens a new window for PDF merging.

    :param obj: Instance of the current window containing a reference
                to the parent window.
    """
    # Скрываем текущее окно (ModesWindow)
    obj.app.withdraw()  # Скрываем окно
    # Создаем и открываем новое окно для объединения PDF (GraphicalEditor)
    # Передаем родительское окно
    graphical_editor_window = GraphicalEditor(master=obj.app)
    # Запускаем цикл событий для нового окна
    graphical_editor_window.mainloop()

    # Когда окно GraphicalEditor закрывается, возвращаем исходное окно
    obj.app.deiconify()  # Возвращаем исходное окно в активное состояние


def update_elements(mode: str) -> None:
    """
    Updates UI elements based on the selected mode. Hides old elements and
    adds new ones.

    :param mode: The mode to display the associated elements.
    """
    # Скрываем все элементы из предыдущего режима
    global current_mode
    current_mode = mode
    for element in win.winfo_children():
        element.grid_remove()

    # В зависимости от выбранного режима добавляем новые элементы
    for key, element in elements[mode].items():
        if not isinstance(key, str):
            logging.debug(f"Выполняем команду: {element}")
            eval(element)
    try:
        for element, text in mode_settings[current_mode].items():
            logging.debug(f"Меняем конфигурацию элемента: {element}, {text}")
            element.configure(text=text)
    except KeyError:
        pass
    if "start_settings" in elements[current_mode]:
        for setting in elements[current_mode]["start_settings"]:
            eval(setting)
    auto_resize_window()


def is_ready_to_start_work() -> bool:
    """
    Checks if all conditions are met to start the work. Returns True if
    all conditions are satisfied, otherwise False.

    :return: True if all conditions are met, otherwise False.
    """
    logging.debug("Функция is_ready_to_start_work")
    # Если не все элементы из work_conditions активны и имеют текст,
    # то появляется лейбл с сообщением о необходимых условиях.
    if not all(
        map(lambda x: (x.winfo_ismapped() and x.cget("text")),
            elements[current_mode]["work_conditions"])):
        eval(
            elements[current_mode]["additional_elements"]
            ["next_step_elements"][conditions_message_label])
        conditions_message_label.configure(
            text=mode_settings[current_mode][conditions_message_label])
        auto_resize_window()
        logging.debug("Есть лейбл о том, что не хватает файла docx")
        return False
    entered_text = pages.get()
    on_validate(entered_text)
    if invalid_pages_label.winfo_ismapped():
        eval(
            elements[current_mode]
            ["additional_elements"]["next_step_elements"]
            [conditions_message_label])
        message = elements[current_mode]["inhibitors"][invalid_pages_label]
        conditions_message_label.configure(text=message)
        auto_resize_window()
        logging.debug('Лейбл о том, что нужно ввести правильно числа')
        return False

    conditions_message_label.grid_remove()
    # eval(elements[current_mode]["additional_elements"]["next_step_elements"][conditions_message_label])
    auto_resize_window()
    logging.debug('Функция is_ready_to_start_work вернула True')
    return True


# Функция обновления прогресса в UI
def update_progress(user_input_data: dict) -> None:
    """
    Updates the progress bar and label based on the given user input data.

    :param user_input_data: A dictionary containing progress information.
    """

    # Вычисляем процент завершения
    progress = user_input_data["progress"]

    # Обновляем прогресс-бар и метку
    progress_bar.set(progress / 100)  # Прогресс в формате от 0 до 1
    progress_label.configure(text=f"{progress}%")  # Обновляем текст метки

    # Если прогресс не достиг 100%, проверяем через 1 секунду
    if progress < 100:
        # Проверяем каждые полсекунды
        win.after(500, update_progress, user_input_data)


def work() -> None:
    """
    Initiates the work process by verifying conditions and starting a
    separate thread for processing.

    :return: None
    """
    if not is_ready_to_start_work():
        return
    conditions_message_label.grid_remove()
    additional_elements = elements[current_mode]["additional_elements"]
    eval(additional_elements["next_step_elements"][progress_label])
    eval(additional_elements["next_step_elements"][progress_bar])
    progress_label.configure(text="0%")
    progress_bar.set(0)
    auto_resize_window()
    user_input_data = {"mode": current_mode}
    logging.debug(f"last_page_label: {last_page_label}, "
                  f"last_page_label.cget('text') = "
                  f"{last_page_label.cget('text')}")
    for key, value in user_input[current_mode].items():
        logging.debug(f'key = {key}, value = {value}')
        user_input_data[key] = eval(value)
    user_input_data["progress"] = 0

    logging.debug(f"user_input_data = {user_input_data}")
    # Запускаем задачу в отдельном потоке
    task_thread = threading.Thread(
        target=work_process, args=(user_input_data,))
    task_thread.start()
    # Запускаем процесс обновления прогресса в основном потоке
    update_progress(user_input_data)


def flatten_dict(nested_dict: dict) -> dict:
    """
    Flattens a nested dictionary, excluding specific keys such as
    "work_conditions", "inhibitors", and "start_settings".

    :param nested_dict: A dictionary to flatten.
    :return: A flattened dictionary.
    """
    flatten_dict = {}
    for key, value in nested_dict.items():
        if key not in ("work_conditions", "inhibitors", "start_settings"):
            if not isinstance(key, str):
                flatten_dict[key] = value
            else:
                for value_2_depth in value.values():
                    flatten_dict.update(value_2_depth)
    # logging.debug(
    # f'element = {element}' for element in flatten_dict.keys())

    return flatten_dict


def auto_resize_window() -> None:
    """
    Automatically resizes the window based on the current visible elements
    and their sizes.
    """
    win.update_idletasks()  # Обновляем все отложенные задачи

    max_width_element = max(
        [element for element in flatten_dict(
            elements[current_mode]).keys() if element.winfo_ismapped()],
        key=lambda x: x.winfo_reqwidth()
    )
    active_widgets_width = [widget.winfo_height(
        ) for widget in win.winfo_children() if widget.winfo_ismapped()]
    total_height = sum(active_widgets_width)

    # Устанавливаем предварительный размер окна
    win.geometry(
        f"{(max_width_element.winfo_reqwidth()
           + 2 * padx)}x{total_height + 14 * len(active_widgets_width)}")
    win.update()  # Обновляем окно ещё раз после изменения размера


def update_file_label(label: ctk.CTkLabel, formats: list,
                      alternative_label: ctk.CTkLabel) -> None:
    """
    Updates the label to show the selected file name, if the file's format
    matches the allowed formats.

    :param label: The label to update with the selected file name.
    :param formats: List of allowed file formats.
    :param alternative_label: An alternative label to display if no file is
                              selected or the file format is invalid.
    """
    filename = filedialog.askopenfilename()
    logging.debug(
        f"Функция update_file_label начата с параметрами: {label}, "
        f"{formats}, {alternative_label}")
    if not filename:
        label.configure(text="")
        logging.debug(
            f"Проверка значения метки в функции update_file_label: {label}, "
            f"текст: {label.cget('text')}")

    if filename.split(".")[-1] in formats:
        alternative_label.grid_remove()
        conditions_message_label.grid_remove()
        label.configure(text=filename if filename else None)
    else:
        label.grid_remove()
        label = alternative_label
    if not filename:
        conditions_message_label.grid_remove()
        label.grid_remove()
    else:
        eval(flatten_dict(elements[current_mode])[label])
    auto_resize_window()


def on_validate(param: str) -> None:
    """
    Validates the user input. Changes field color and shows error labels
    if the input is incorrect.

    :param param: The input text or event object to validate.
    """
    # Если передан объект события, получаем текст из поля
    if isinstance(param, tk.Event):
        entered_text = pages.get()  # Получаем введенный текст
    else:
        entered_text = param  # Используем переданный текст напрямую

    # Валидация текста
    if validate_input_pages(entered_text):
        logging.debug("Введенные данные корректны")
        # Зеленый цвет при корректном вводе
        pages.configure(fg_color="lightgreen")
        invalid_pages_label.grid_remove()  # Убираем лейбл об ошибке
    else:
        logging.debug("Введенные данные некорректны")
        pages.configure(fg_color="lightcoral")  # Красный цвет при ошибке
        # Показать лейбл об ошибке
        eval(flatten_dict(elements[current_mode])[invalid_pages_label])

    auto_resize_window()


def validate_input_pages(text: str) -> bool:
    """
    Validates the input for page numbers or ranges. Returns True if valid,
    otherwise False.

    :param text: The input text containing page numbers or ranges.
    :return: True if input is valid, otherwise False.
    """
    # Разбиваем строку по запятым и удаляем лишние пробелы
    if not text:
        return True
    parts = [part.strip() for part in text.split(",")]

    for part in parts:
        # Проверка на формат диапазона
        if '-' in part:
            # Разделяем на два числа
            range_parts = part.split('-')
            if len(range_parts) != 2:
                return False  # Если не два числа в диапазоне, то это ошибка
            try:
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                if start >= end:
                    return False  # Если первое число не меньше второго
            except ValueError:
                return False  # Если не числа в диапазоне
        else:
            # Проверка на простое число
            try:
                int(part)
            except ValueError:
                return False  # Если не число, то ошибка
    return True  # Если все проверки прошли


# Функция, которая будет проверять, был ли клик по полю ввода
def on_click(event: tk.Event) -> None:
    """
    Handles click events on the UI. Validates the input if clicked outside
    the pages field.

    :param event: The click event to handle.
    """
    if event.widget != pages:  # Проверяем, что клик был не по полю ввода
        on_validate(event)


if __name__ == "__main__":
    print('Поехали')
    # Создаем главное окно и запускаем цикл
    root = ctk.CTk()  # Главное окно
    root.iconbitmap(resource_path("SIE-no-scan.ico"))
    modes_window = ModesWindow(root)  # Окно с кнопкой для объединения PDF

    root.mainloop()  # Запускаем цикл событий главного окна
