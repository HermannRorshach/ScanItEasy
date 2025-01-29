import os
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import logging

class GraphicalEditor(ctk.CTk):  # Оставляем наследование от CTk, чтобы быть окном
    def __init__(self, master=None):  # Добавляем master как аргумент конструктора
        super().__init__(master)  # Передаем master в CTk
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('green')
        self.title("ScanItEasy")
        window_position_horizontal = 400
        window_position_vertical = 10
        self.geometry(
            f'{700}x{600}+{window_position_horizontal}+{window_position_vertical}')
        self.blocks = {}  # Используем словарь для хранения блоков
        self.block_id = -1  # Начальный индекс-ключ для блока
        self.flag = True

        self.configure_grid()
        self.create_widgets()

    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)  # Столбец 0 растягивается
        self.grid_rowconfigure(0, weight=0)  # Верхняя строка не будет растягиваться
        self.grid_rowconfigure(1, weight=0)  # Верхняя строка не будет растягиваться
        self.grid_rowconfigure(2, weight=1)  # Нижняя строка будет растягиваться

    def create_widgets(self):

        # Кнопка "Назад"
        # dark_image = tk.PhotoImage(file="dark.png")
        # light_image = tk.PhotoImage(file="light.png")

        # def on_hover(event):
        #     back_button.config(image=dark_image)

        # def on_leave(event):
        #     back_button.config(image=light_image)

        back_button = tk.Button(
            self, text="Назад", font=("Arial", 14, "normal"),
            fg="white", padx=10, pady=10, bg=self["bg"], activebackground=self["bg"],
            borderwidth=0, command=self.on_back_button_click, compound="left", relief="flat"
        )

        back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")

        # back_button.bind("<Enter>", on_hover)
        # back_button.bind("<Leave>", on_leave)

        # Заголовок
        header_label = ctk.CTkLabel(self, text="Объединить два или более pdf-файлов",
                                    font=("Arial", 17, "bold"))
        header_label.grid(row=1, column=0)

        self.progress_label = ctk.CTkLabel(self, text="0%", font=("Arial", 17, "bold"),)
        self.progress_bar = ctk.CTkProgressBar(self, width=400, height=25, corner_radius=8, border_width=0,
                                               bg_color=self.cget('bg'), fg_color="white")

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
        self.blocks_frame.grid(row=2, column=0, sticky="nsew", padx=50, pady=10)

        # Привязываем обработчик события клика по окну для проверки всех полей
        self.bind("<Button-1>", self.on_click)

    def on_back_button_click(self):
        # Закрываем текущее окно (GraphicalEditor) при нажатии кнопки
        self.destroy()

        root = ctk.CTk()  # Главное окно
        modes_window = ModesWindow(root)  # Окно с кнопкой для объединения PDF

        root.mainloop()  # Запускаем цикл событий главного окна


    def on_click(self, event):
        """Проверяем все поля ввода при клике в любое место окна"""
        for index, block in self.blocks.items():
            entry_widget = block["pages_entry"]
            pages_entry_error_label = block["pages_entry_error_label"]
            self.validate_entry(entry_widget, pages_entry_error_label)

    def check_block(self):
        if self.blocks and self.blocks[self.block_id]["file_label"].cget("text") != "Файл не выбран":
            return True
        for block_id in self.blocks.keys():
            if self.blocks and self.blocks[block_id]["file_label"].cget("text") == "Файл не выбран":
                self.blocks[block_id]["file_label"].grid_remove()
                self.blocks[block_id]["file_path_empty_error_label"].grid(row=0, column=1, sticky="w", padx=10, pady=0)
        return False

    def add_block(self):
        # Сначала проверяем все поля ввода
        if not self.check_all_entries_valid():
            return

        if self.flag or self.check_block():
            self.flag = False
            self.block_id += 1  # Генерация уникального ID для блока
            block_id = self.block_id

            # Создание фрейма для нового блока
            block_frame = ctk.CTkFrame(self.blocks_frame)
            block_frame.grid(row=self.block_id, column=0, pady=5, padx=5, sticky="ew")
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
            file_path_empty_error_label = ctk.CTkLabel(block_frame, text="Выберите файл", text_color="red", font=("Arial", 12))

            pages_entry = ctk.CTkEntry(block_frame,
                                       placeholder_text="Введите номера страниц через запятую и/или диапазон через дефис",   # Текст-подсказка
                                       fg_color="lightgray",                # Цвет фона
                                       placeholder_text_color="Gray",
                                       text_color="black",                  # Цвет текста
                                       width=430,                           # Ширина поля
                                       corner_radius=10,                    # Скругленные углы
                                       font=("Arial", 12),                   # Шрифт текста
                                       )
            pages_entry.grid(row=2, column=0, sticky="w", columnspan=3, pady=5, padx=10)

            # Лейбл для сообщения-инструкции
            entry_label = ctk.CTkLabel(block_frame, text="Если нужны все страницы, оставьте поле пустым", font=("Arial", 12, "italic"), text_color="#2FA572", justify='center')
            entry_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=0, padx=10)

            # Лейбл для ошибок
            pages_entry_error_label = ctk.CTkLabel(block_frame, text="", text_color="red", font=("Arial", 10))
            pages_entry_error_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=10)

            pages_entry.bind("<FocusOut>", lambda event, entry=pages_entry, label=pages_entry_error_label: self.validate_entry(entry, label))
            pages_entry.bind("<ButtonRelease-1>", lambda event, entry=pages_entry, label=pages_entry_error_label: self.validate_entry(entry, label))

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
            logging.info(f"Создан новый блок с block_id={self.block_id}")

        else:
            return

    def validate_entry(self, entry_widget, pages_entry_error_label):
        entered_text = entry_widget.get()

        # Проверка данных
        if self.validate_input_pages(entered_text):
            entry_widget.configure(fg_color="#DEFCD4")  # Зеленый цвет при корректном вводе
            pages_entry_error_label.configure(text="")  # Очищаем ошибку
        else:
            entry_widget.configure(fg_color="lightcoral")  # Красный цвет при ошибке
            pages_entry_error_label.configure(text="Введите номера страниц через запятую и/или диапазон через дефис")  # Сообщение об ошибке

    def check_all_entries_valid(self):
        for index, block in self.blocks.items():
            entry_widget = block["pages_entry"]
            entered_text = entry_widget.get()
            pages_entry_error_label = block["pages_entry_error_label"]
            if not self.validate_input_pages(entered_text):
                entry_widget.configure(fg_color="lightcoral")  # Красный цвет при ошибке
                pages_entry_error_label.configure(text="Введите номера страниц через запятую и/или диапазон через дефис")
                return False
        return True

    def validate_input_pages(self, text):
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

    def select_file(self, block_id):
        file_path = filedialog.askopenfilename(
            title="Выберите файл", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            file_name = os.path.basename(file_path)

            # Если длина имени файла больше 50 символов, обрезаем его
            if len(file_name) > 50:
                file_name = file_name[:25] + " . . . " + file_name[-20:]  # 25 символов с начала и 20 символов с конца

            # Записываем file_path в словарь
            self.blocks[block_id]["file_path"] = file_path

            # Обновляем метку с именем файла
            self.blocks[block_id]["file_label"].configure(text=file_name)
            self.blocks[block_id]["file_label"].grid(row=0, column=1, padx=10, sticky="w")

            # Убираем лейбл с ошибкой
            self.blocks[block_id]["file_path_empty_error_label"].grid_remove()


    def delete_block(self, block_id):
        if block_id in self.blocks:
            block = self.blocks.pop(block_id)
            file_label_text = block["file_label"].cget("text")
            pages_text = block["pages_entry"].get()

            # Логирование: удаляем блок
            logging.info(f"Удален блок с block_id={block_id}, file_label='{file_label_text}', pages_entry='{pages_text}'")

            block["frame"].destroy()

            # Логирование: текущее состояние блоков
            logging.info("После удаления блоков:")
            for b_id, b_data in self.blocks.items():
                file_label = b_data["file_label"].cget("text")
                pages_text = b_data["pages_entry"].get()
                logging.info(f"  block_id={b_id}, file_label='{file_label}', pages_entry='{pages_text}'")

            if not self.blocks:
                self.flag = True

    def merge(self):
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
        self.progress_label.grid(row=1000, column=0, pady=5, padx=70, sticky="w")
        self.progress_bar.grid(row=1001, column=0, pady=5, padx=70, sticky="w")
        print(data)
        return data

# Глобальная переменная для окна
win = None
# Глобальная переменная для экземпляра класса ModesWindow
obj = None
# Глобальная переменная режима работы программы
current_mode = "modes"

padx = 70

# Глобальные переменные для виджетов
mode_var = None
mode_label = None
default_mode = None
custom_mode = None
additionally_label = None
convert_to_pdf = None
merge_pdf = None
grayscale_mode = None
compress_mode = None
convert_to_png = None
back_button = None
dark_image = None
light_image = None
header_label = None
btn_file_docx = None
docx_label = None
invalid_docx_label = None
invalid_last_page_label = None
progress_label = None
progress_bar = None
conditions_message_label = None
btn_to_work = None
color_var = None # ctk.IntVar(value=0)
color_label = None
red = None
blue = None
pages_label = None
text_help_label = None
pages = None
invalid_pages_label = None
signature_var = None
signature_label = None
signature_yes = None
signature_no = None
is_compression_needed = None
is_compression_needed_checkbox = None
btn_file_pdf = None
pdf_label = None
invalid_pdf_label = None
last_page_label = None
btn_file_last_page = None


class ModesWindow(ctk.CTkFrame):
    def __init__(self, master):
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
            f'{self.window_width}x{self.window_height}+{self.window_position_horizontal}+{self.window_position_vertical}')
        self.master.minsize(300, 300)
        self.master.title("ScanItEasy")
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('green')

        create_widgets()
        # Добавляем кнопку для объединения PDF


def create_widgets():
    global win
    global mode_label, default_mode, custom_mode, additionally_label, convert_to_pdf, merge_pdf
    global grayscale_mode, compress_mode, convert_to_png, back_button, dark_image, light_image
    global header_label, btn_file_docx, docx_label, invalid_docx_label, invalid_last_page_label
    global progress_label, progress_bar, conditions_message_label, btn_to_work
    global color_var, color_label, red, blue, pages_label, text_help_label, pages
    global invalid_pages_label, signature_var, signature_label, signature_yes, signature_no
    global is_compression_needed, is_compression_needed_checkbox, btn_file_pdf, pdf_label, invalid_pdf_label
    global mode_var, color_var, signature_var, is_compression_needed, btn_file_last_page, last_page_label
    # Переменные
    mode_var = ctk.StringVar(value="modes")
    color_var = ctk.IntVar(value=0)
    signature_var = ctk.IntVar(value=1)
    is_compression_needed = ctk.BooleanVar(value=True)

    # Визуальные элементы
    mode_label = ctk.CTkLabel(win, text="Выберите опцию")
    mode_label.grid(row=0, column=0, padx=70, pady=15, sticky="w")

    # имы
    default_mode = ctk.CTkRadioButton(win, text="Режим по умолчанию", variable=mode_var, value="default_mode", command=lambda: update_elements(self.mode_var.get()))
    default_mode.grid(row=1, column=0, padx=70, pady=5, sticky="w")

    custom_mode = ctk.CTkRadioButton(win, text="Пользовательский режим с настройками", variable=mode_var, value="custom_mode", command=lambda: update_elements(self.mode_var.get()))
    custom_mode.grid(row=2, column=0, padx=70, pady=5, sticky="w")

    additionally_label = ctk.CTkLabel(win, text="Дополнительно:", font=("Arial", 12, "italic"), justify='center')
    additionally_label.grid(row=3)

    convert_to_pdf = ctk.CTkRadioButton(win, text="Конвертировать docx в pdf", variable=mode_var, value="convert_to_pdf_mode", command=lambda: update_elements(self.mode_var.get()))
    convert_to_pdf.grid(row=4, column=0, padx=70, pady=5, sticky="w")

    merge_pdf = ctk.CTkRadioButton(win, text="Объединить два или несколько pdf", variable=mode_var, value="merge_pdf_mode", command=on_merge_pdf_button_click)
    merge_pdf.grid(row=5, column=0, padx=70, pady=5, sticky="w")

    grayscale_mode = ctk.CTkRadioButton(win, text="Сделать pdf чёрно-белым", variable=mode_var, value="grayscale_mode", command=lambda: update_elements(self.mode_var.get()))
    grayscale_mode.grid(row=6, column=0, padx=70, pady=5, sticky="w")

    compress_mode = ctk.CTkRadioButton(win, text="Сжать pdf", variable=mode_var, value="compress_mode", command=lambda: update_elements(self.mode_var.get()))
    compress_mode.grid(row=7, column=0, padx=70, pady=5, sticky="w")

    convert_to_png = ctk.CTkRadioButton(win, text="Конвертировать pdf в png", variable=mode_var, value="convert_to_png_mode", command=lambda: update_elements(self.mode_var.get()))
    convert_to_png.grid(row=8, column=0, padx=70, pady=5, sticky="w")

    # пка Назад
    dark_image = tk.PhotoImage(file="dark.png")
    light_image = tk.PhotoImage(file="light.png")

    back_button = tk.Button(
        win,
        image=light_image,
        text="Назад",
        font=("Arial", 14, "normal"),
        fg="white",
        padx=10,
        pady=10,
        # bg=win["bg"],  # Цвет фона кнопки подстраивается под фон окна
        # activebackground=win["bg"],  # Цвет фона кнопки при наведении
        borderwidth=0,  # Убираем рамку
        command=lambda: update_elements("modes"),
        compound="left",
        relief="flat"
    )
    back_button.grid(row=9, column=0, padx=70, pady=5, sticky="w")

    # кции для обработки кнопки назад
    # back_button.bind("<Enter>", on_hover)
    # back_button.bind("<Leave>", on_leave)

    # им по умолчанию
    header_label = ctk.CTkLabel(win, text="Режим по умолчанию")
    header_label.grid(row=10, column=0, padx=70, pady=5, sticky="w")

    btn_file_docx = ctk.CTkButton(win, text="Выберите файл для сканирования", command=lambda: update_file_label(self.docx_label, ["docx"], self.invalid_docx_label))
    btn_file_docx.grid(row=11, column=0, padx=70, pady=5, sticky="w")

    docx_label = ctk.CTkLabel(win, text=None)
    docx_label.grid(row=12, column=0, padx=70, pady=5, sticky="w")

    invalid_docx_label = ctk.CTkLabel(win, text="Файл должен быть формата docx", text_color="red", padx=20)
    invalid_docx_label.grid(row=13, column=0, padx=70, pady=5, sticky="w")

    # ьзовательский режим с настройками
    color_label = ctk.CTkLabel(win, text="Выберите цвет ленточки")
    color_label.grid(row=14, column=0, padx=70, pady=5, sticky="w")

    red = ctk.CTkRadioButton(win, text="Красный", variable=color_var, value=0, command=lambda: print("Цвет ленты: красный"))
    red.grid(row=15, column=0, padx=70, pady=5, sticky="w")

    blue = ctk.CTkRadioButton(win, text="Синий", variable=color_var, value=1, command=lambda: print("Цвет ленты: Синий"))
    blue.grid(row=16, column=0, padx=70, pady=5, sticky="w")

    pages_label = ctk.CTkLabel(win, text="Выберите страницы")
    pages_label.grid(row=17, column=0, padx=70, pady=5, sticky="w")

    text_help_label = ctk.CTkLabel(win, text="Если нужны все страницы, оставьте поле пустым", font=("Arial", 12, "italic"), text_color="green", justify='center')
    text_help_label.grid(row=18, column=0, padx=70, pady=5, sticky="w")

    pages = ctk.CTkEntry(win, placeholder_text="Введите номера страниц через запятую и/или диапазон страниц через дефис", width=470, corner_radius=10, font=("Arial", 12))
    pages.grid(row=19, column=0, padx=70, pady=5, sticky="w")

    invalid_pages_label = ctk.CTkLabel(win, text="Введите номера страниц через запятую и/или диапазон страниц через дефис", text_color="red", padx=20)
    invalid_pages_label.grid(row=20, column=0, padx=70, pady=5, sticky="w")

    signature_label = ctk.CTkLabel(win, text="Нужна ли подпись переводчика?")
    signature_label.grid(row=21, column=0, padx=70, pady=5, sticky="w")

    signature_yes = ctk.CTkRadioButton(win, text="Да", variable=signature_var, value=1, command=lambda: print("Подпись переводчика нужна"))
    signature_yes.grid(row=22, column=0, padx=70, pady=5, sticky="w")

    signature_no = ctk.CTkRadioButton(win, text="Нет", variable=signature_var, value=0, command=lambda: print("Подпись переводчика не нужна"))
    signature_no.grid(row=23, column=0, padx=70, pady=5, sticky="w")

    # им конвертации из docx в pdf
    is_compression_needed_checkbox = ctk.CTkCheckBox(win, text="Сжать итоговый pdf", variable=is_compression_needed)
    is_compression_needed_checkbox.grid(row=24, column=0, padx=70, pady=5, sticky="w")

    # пка для выбора файла pdf
    btn_file_pdf = ctk.CTkButton(win, text="Выберите pdf-файл", command=lambda: update_file_label(pdf_label, ["pdf"], invalid_pdf_label))
    btn_file_pdf.grid(row=25, column=0, padx=70, pady=5, sticky="w")

    btn_file_last_page = ctk.CTkButton(
        win, text="Выберите файл для последней части документа",
        command=lambda: update_file_label(
            last_page_label, ["pdf", "jpeg", "jpg", "png"],
            invalid_last_page_label))
    last_page_label = ctk.CTkLabel(win, text=None)

    pdf_label = ctk.CTkLabel(win, text=None)
    pdf_label.grid(row=26, column=0, padx=70, pady=5, sticky="w")

    invalid_pdf_label = ctk.CTkLabel(win, text="Файл должен быть формата pdf", text_color="red", padx=20)
    invalid_pdf_label.grid(row=27, column=0, padx=70, pady=5, sticky="w")

    def on_hover(self, event):
        back_button.config(image=dark_image)

    def on_leave(self, event):
        back_button.config(image=light_image)

    # Привязка события для проверки при клике на любое место
    win.bind("<Button-1>", on_click)  # Привязка на клик по окну
    pages.bind("<FocusOut>", on_validate)



def on_merge_pdf_button_click(obj):
    # Закрываем текущее окно (ModesWindow) при нажатии кнопки
    obj.master.destroy()

    # Открываем окно для объединения PDF (GraphicalEditor)
    root = ctk.CTk()  # Главное окно
    graphical_editor_window = GraphicalEditor(root)  # Создаем новое окно
    graphical_editor_window.mainloop()  # Запускаем цикл событий нового окна




elements = {
    "modes": {mode_label: 'mode_label.grid(row=0, column=0, padx=padx, pady=15, sticky="w")',
              default_mode: 'default_mode.grid(row=1, column=0, padx=padx, pady=5, sticky="w")',
              custom_mode: 'custom_mode.grid(row=2, column=0, padx=padx, pady=5, sticky="w")',
              additionally_label: "additionally_label.grid(row=3)",
              convert_to_pdf: 'convert_to_pdf.grid(row=4, column=0, padx=padx, pady=5, sticky="w")',
              merge_pdf: 'merge_pdf.grid(row=5, column=0, padx=padx, pady=5, sticky="w")',
              grayscale_mode: 'grayscale_mode.grid(row=6, column=0, padx=padx, pady=5, sticky="w")',
              compress_mode: 'compress_mode.grid(row=7, column=0, padx=padx, pady=5, sticky="w")',
              convert_to_png: 'convert_to_png.grid(row=8, column=0, padx=padx, pady=5, sticky="w")'
    },
    "default_mode": {
        back_button: 'back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")',
        header_label: 'header_label.grid(row=1, column=0, padx=padx, pady=5, sticky="w")',
        btn_file_docx: 'btn_file_docx.grid(row=2, column=0, padx=padx, pady=5, sticky="w")',
        btn_file_last_page: 'btn_file_last_page.grid(row=4, column=0, padx=padx, pady=5, sticky="w")',
        btn_to_work: 'btn_to_work.grid(row=8, column=0, padx=padx, pady=5, sticky="w")',
        "additional_elements": {
            "error_messages": {
                invalid_docx_label: 'invalid_docx_label.grid(row=3, column=0, pady=5, padx=padx, sticky="w")',
                invalid_last_page_label: 'invalid_last_page_label.grid(row=5, column=0, pady=5, padx=padx, sticky="w")'
            },
            "next_step_elements": {
                docx_label: 'docx_label.grid(row=3, column=0, padx=padx, pady=5, sticky="w")',
                last_page_label: 'last_page_label.grid(row=5, column=0, padx=padx, pady=5, sticky="w")',
                progress_label: 'progress_label.grid(row=6, column=0, pady=5, padx=padx, sticky="w")',
                progress_bar: 'progress_bar.grid(row=7, column=0, pady=5, padx=padx, sticky="w")',
                conditions_message_label: 'conditions_message_label.grid(row=6, column=0, pady=5, padx=padx, sticky="w")'
            }
        },
        "work_conditions": (docx_label,)
    },
     "custom_mode": {
        back_button: 'back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")',
        header_label: 'header_label.grid(row=1, column=0, padx=padx, pady=5, sticky="w")',
        btn_file_docx: 'btn_file_docx.grid(row=2, column=0, padx=padx, pady=5, sticky="w")',
        btn_file_last_page: 'btn_file_last_page.grid(row=4, column=0, padx=padx, pady=5, sticky="w")',
        color_label: 'color_label.grid(row=6, column=0, padx=padx, pady=10, sticky="w")',
        red: 'red.grid(row=7, column=0, padx=padx, pady=5, sticky="w")',
        blue: 'blue.grid(row=8, column=0, padx=padx, pady=(5, 15), sticky="w")',
        pages_label: 'pages_label.grid(row=9, column=0, padx=padx, pady=0, sticky="w")',
        text_help_label: 'text_help_label.grid(row=10, column=0, padx=padx, pady=0, sticky="w")',
        pages: 'pages.grid(row=11, column=0, padx=padx, pady=5, sticky="w")',
        signature_label: 'signature_label.grid(row=13, column=0, padx=padx, pady=5, sticky="w")',
        signature_yes: 'signature_yes.grid(row=14, column=0, padx=padx, pady=5, sticky="w")',
        signature_no: 'signature_no.grid(row=15, column=0, padx=padx, pady=5, sticky="w")',
        btn_to_work: 'btn_to_work.grid(row=18, column=0, padx=padx, pady=5, sticky="w")',
        "additional_elements": {
            "error_messages": {
                invalid_docx_label: 'invalid_docx_label.grid(row=3, column=0, pady=5, padx=padx, sticky="w")',
                invalid_last_page_label: 'invalid_last_page_label.grid(row=5, column=0, pady=5, padx=padx, sticky="w")',
                invalid_pages_label: 'invalid_pages_label.grid(row=12, column=0, pady=5, padx=padx, sticky="w")'
            },
            "next_step_elements": {
                docx_label: 'docx_label.grid(row=3, column=0, padx=padx, pady=5, sticky="w")',
                last_page_label: 'last_page_label.grid(row=5, column=0, padx=padx, pady=5, sticky="w")',
                progress_label: 'progress_label.grid(row=16, column=0, pady=5, padx=padx, sticky="w")',
                progress_bar: 'progress_bar.grid(row=17, column=0, pady=5, padx=padx, sticky="w")',
                conditions_message_label: 'conditions_message_label.grid(row=16, column=0, pady=5, padx=padx, sticky="w")'
            }
        },
        "work_conditions": (docx_label,),
        "inhibitors": {
            invalid_docx_label: "Для запуска сканирования нужно выбрать файл в формате docx",
            invalid_pages_label: "Введите номера страниц через запятую и/или диапазон страниц через дефис"}
    },
    "convert_to_pdf_mode": {
        back_button: 'back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")',
        header_label: 'header_label.grid(row=1, column=0, padx=padx, pady=5, sticky="w")',
        btn_file_docx: 'btn_file_docx.grid(row=2, column=0, padx=padx, pady=5, sticky="w")',
        pages_label: 'pages_label.grid(row=4, column=0, padx=padx, pady=0, sticky="w")',
        text_help_label: 'text_help_label.grid(row=5, column=0, padx=padx, pady=0, sticky="w")',
        pages: 'pages.grid(row=6, column=0, padx=padx, pady=5, sticky="w")',
        is_compression_needed_checkbox: 'is_compression_needed_checkbox.grid(row=8, column=0, padx=padx, pady=5, sticky="w")',
        btn_to_work: 'btn_to_work.grid(row=18, column=0, padx=padx, pady=5, sticky="w")',
        "additional_elements": {
            "error_messages": {
                invalid_docx_label: 'invalid_docx_label.grid(row=3, column=0, pady=5, padx=padx, sticky="w")',
                invalid_pages_label: 'invalid_pages_label.grid(row=7, column=0, pady=5, padx=padx, sticky="w")'
            },
            "next_step_elements": {
                docx_label: 'docx_label.grid(row=3, column=0, padx=padx, pady=5, sticky="w")',
                progress_label: 'progress_label.grid(row=9, column=0, pady=5, padx=padx, sticky="w")',
                progress_bar: 'progress_bar.grid(row=10, column=0, pady=5, padx=padx, sticky="w")',
                conditions_message_label: 'conditions_message_label.grid(row=16, column=0, pady=5, padx=padx, sticky="w")'
            }
        },
        "work_conditions": (docx_label,),
        "inhibitors": {
            invalid_docx_label: "Для конвертации нужно выбрать файл в формате docx",
            invalid_pages_label: "Введите номера страниц через запятую и/или диапазон страниц через дефис"}
    },
     "grayscale_mode": {
        back_button: 'back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")',
        header_label: 'header_label.grid(row=1, column=0, padx=padx, pady=5, sticky="w")',
        btn_file_pdf: 'btn_file_pdf.grid(row=2, column=0, padx=padx, pady=5, sticky="w")',
        pages_label: 'pages_label.grid(row=4, column=0, padx=padx, pady=0, sticky="w")',
        text_help_label: 'text_help_label.grid(row=5, column=0, padx=padx, pady=0, sticky="w")',
        pages: 'pages.grid(row=6, column=0, padx=padx, pady=5, sticky="w")',
        is_compression_needed_checkbox: 'is_compression_needed_checkbox.grid(row=8, column=0, padx=padx, pady=5, sticky="w")',
        btn_to_work: 'btn_to_work.grid(row=18, column=0, padx=padx, pady=5, sticky="w")',
        "additional_elements": {
            "error_messages": {
                invalid_pdf_label: 'invalid_pdf_label.grid(row=3, column=0, pady=5, padx=padx, sticky="w")',
                invalid_pages_label: 'invalid_pages_label.grid(row=7, column=0, pady=5, padx=padx, sticky="w")'
            },
            "next_step_elements": {
                pdf_label: 'pdf_label.grid(row=3, column=0, padx=padx, pady=5, sticky="w")',
                progress_label: 'progress_label.grid(row=9, column=0, pady=5, padx=padx, sticky="w")',
                progress_bar: 'progress_bar.grid(row=10, column=0, pady=5, padx=padx, sticky="w")',
                conditions_message_label: 'conditions_message_label.grid(row=16, column=0, pady=5, padx=padx, sticky="w")'
            }
        },
        "work_conditions": (pdf_label,),
        "inhibitors": {
            invalid_pdf_label: "Для конвертации нужно выбрать файл в формате pdf",
            invalid_pages_label: "Введите номера страниц через запятую и/или диапазон страниц через дефис"}
    },
    "compress_mode": {
        back_button: 'back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")',
        header_label: 'header_label.grid(row=1, column=0, padx=padx, pady=5, sticky="w")',
        btn_file_pdf: 'btn_file_pdf.grid(row=2, column=0, padx=padx, pady=5, sticky="w")',
        btn_to_work: 'btn_to_work.grid(row=18, column=0, padx=padx, pady=5, sticky="w")',
        "additional_elements": {
            "error_messages": {
                invalid_pdf_label: 'invalid_pdf_label.grid(row=3, column=0, pady=5, padx=padx, sticky="w")',
            },
            "next_step_elements": {
                pdf_label: 'pdf_label.grid(row=3, column=0, padx=padx, pady=5, sticky="w")',
                progress_label: 'progress_label.grid(row=9, column=0, pady=5, padx=padx, sticky="w")',
                progress_bar: 'progress_bar.grid(row=10, column=0, pady=5, padx=padx, sticky="w")',
                conditions_message_label: 'conditions_message_label.grid(row=16, column=0, pady=5, padx=padx, sticky="w")'
            }
        },
        "work_conditions": (pdf_label,),
        "inhibitors": {
            invalid_pdf_label: "Для конвертации нужно выбрать файл в формате pdf",}
    },
    "convert_to_png_mode": {
        back_button: 'back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")',
        header_label: 'header_label.grid(row=1, column=0, padx=padx, pady=5, sticky="w")',
        btn_file_pdf: 'btn_file_pdf.grid(row=2, column=0, padx=padx, pady=5, sticky="w")',
        btn_to_work: 'btn_to_work.grid(row=18, column=0, padx=padx, pady=5, sticky="w")',
        "additional_elements": {
            "error_messages": {
                invalid_pdf_label: 'invalid_pdf_label.grid(row=3, column=0, pady=5, padx=padx, sticky="w")',
            },
            "next_step_elements": {
                pdf_label: 'pdf_label.grid(row=3, column=0, padx=padx, pady=5, sticky="w")',
                progress_label: 'progress_label.grid(row=9, column=0, pady=5, padx=padx, sticky="w")',
                progress_bar: 'progress_bar.grid(row=10, column=0, pady=5, padx=padx, sticky="w")',
                conditions_message_label: 'conditions_message_label.grid(row=16, column=0, pady=5, padx=padx, sticky="w")'
            }
        },
        "work_conditions": (pdf_label,),
        "inhibitors": {
            invalid_pdf_label: "Для конвертации нужно выбрать файл в формате pdf",}
    },

}



mode_settings = {
    "default_mode": {
        header_label: "Режим по умолчанию",
        btn_file_docx: "Выберите файл для сканирования",
        btn_file_last_page: "Выберите файл для последней части документа",
        btn_to_work: "Сканировать",
        conditions_message_label: "Для запуска сканирования нужно выбрать файл в формате docx"},
    "custom_mode": {
        header_label: "Пользовательский режим с настройками",
        btn_file_docx: "Выберите файл для сканирования",
        btn_file_last_page: "Выберите файл для последней части документа",
        btn_to_work: "Сканировать",
        conditions_message_label: "Для запуска сканирования нужно выбрать файл в формате docx"},
    "convert_to_pdf_mode": {
        header_label: "Конвертация docx в pdf",
        btn_file_docx: "Выберите файл для конвертации в pdf",
        btn_to_work: "Конвертировать",
        conditions_message_label: "Для конвертации нужно выбрать файл в формате docx"},
    "grayscale_mode": {
        header_label: "Сделать pdf чёрно-белым",
        btn_file_pdf: "Выберите pdf-файл",
        btn_to_work: "Изменить",
        conditions_message_label: "Для изменения нужно выбрать файл в формате pdf"},
    "compress_mode": {
        header_label: "Сжать pdf",
        btn_file_pdf: "Выберите pdf-файл",
        btn_to_work: "Сжать",
        conditions_message_label: "Для сжатия нужно выбрать файл в формате pdf"},
    "convert_to_png_mode": {
        header_label: "Конвертировать pdf в png",
        btn_file_pdf: "Выберите pdf-файл",
        btn_to_work: "Конвертировать",
        conditions_message_label: "Для конвертации нужно выбрать файл в формате pdf"},

}

user_input = {
    "default_mode": {
        "docx_path": 'docx_label.cget("text")',
        "last_page_path": 'last_page_label.cget("text")',
        "color": '0',
        "need_sign_translator": '1',
        "is_compression_needed": '1',
    },
    "custom_mode": {
        "docx_path": 'docx_label.cget("text")',
        "last_page_path": 'last_page_label.cget("text")',
        "color": 'color_var.get()',
        "need_sign_translator": '1',
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
    },
    "compress_mode": {
        "pdf_path": 'pdf_label.cget("text")',
        "is_compression_needed": '1',
    },
}

def update_elements(mode):
    # Скрываем все элементы из предыдущего режима
    global current_mode
    print(mode)
    current_mode = mode
    for element in win.winfo_children():
        element.grid_remove()

    # В зависимости от выбранного режима добавляем новые элементы
    for key, element in elements[mode].items():
        if not isinstance(key, str):
            eval(element)
    try:
        for element, text in mode_settings[current_mode].items():
            element.configure(text=text)
    except KeyError:
        pass
    auto_resize_window()


def is_ready_to_start_work():
    print("Функция is_ready_to_start_work")
    # Если не все элементы из work_conditions активны и имеют текст, то появляется
    # лейбл с сообщением о необходимых условиях.
    if not all(map(lambda x: (x.winfo_ismapped() and x.cget("text")), elements[current_mode]["work_conditions"])):
        eval(elements[current_mode]["additional_elements"]["next_step_elements"][conditions_message_label])
        conditions_message_label.configure(text=mode_settings[current_mode][conditions_message_label])
        auto_resize_window()
        print("Есть лейбл о том, что не хватает файла docx")
        return False
    entered_text = pages.get()
    on_validate(entered_text)
    if invalid_pages_label.winfo_ismapped():
        eval(elements[current_mode]["additional_elements"]["next_step_elements"][conditions_message_label])
        message = elements[current_mode]["inhibitors"][invalid_pages_label]
        conditions_message_label.configure(text=message)
        auto_resize_window()
        print('Лейбл о том, что нужно ввести правильно числа')
        return False

    conditions_message_label.grid_remove()
    # eval(elements[current_mode]["additional_elements"]["next_step_elements"][conditions_message_label])
    auto_resize_window()
    print('Функция is_ready_to_start_work вернула True')
    return True


def work():
    if not is_ready_to_start_work():
        return
    conditions_message_label.grid_remove()
    print("Закрепляем прогресс-бар")
    eval(elements[current_mode]["additional_elements"]["next_step_elements"][progress_label])
    eval(elements[current_mode]["additional_elements"]["next_step_elements"][progress_bar])
    progress_bar.set(0)
    auto_resize_window()
    user_input_data = {"mode": current_mode}
    for key, value in user_input[current_mode].items():
        user_input_data[key] = eval(value)
    print("\n\nuser_input_data =\n")
    print(user_input_data)




def flatten_dict(nested_dict):
    flatten_dict = {}
    for key, value in nested_dict.items():
        if not key in ("work_conditions", "inhibitors"):
            if not isinstance(key, str):
                flatten_dict[key] = value
            else:
                for value_2_depth in value.values():
                    flatten_dict.update(value_2_depth)
    # [print(element) for element in flatten_dict.keys()]
    return flatten_dict


def auto_resize_window():
    win.update_idletasks()  # Обновляем все отложенные задачи
    for element in flatten_dict(elements[current_mode]).keys():
        print(element.cget('text'), element)

    max_width_element = max(
        [element for element in flatten_dict(elements[current_mode]).keys() if element.winfo_ismapped()],
        key=lambda x: x.winfo_reqwidth()
    )
    # print(len(flatten_dict(elements[current_mode]).keys()))
    # print("Самый большой элемент:", max_width_element._text)
    active_widgets_width = [widget.winfo_height() for widget in win.winfo_children() if widget.winfo_ismapped()]
    total_height = sum(active_widgets_width)

    # Устанавливаем предварительный размер окна
    win.geometry(f"{max_width_element.winfo_reqwidth() + 2 * padx}x{total_height + 14 * len(active_widgets_width)}")
    win.update()  # Обновляем окно после изменения геометрии
    # print("total_height =", total_height, "win.winfo_height() =", win.winfo_height())

    # Учитываем минимальную высоту окна
    # if win.winfo_height() < total_height + 130:
    #     window_height = total_height + 130
    # else:
    #     window_height = win.winfo_height()

    # win.geometry(f"{max_width_element.winfo_reqwidth() + 2 * padx}x{window_height}")
    win.update()  # Обновляем окно ещё раз после изменения размера




def update_file_label(label, formats, alternative_label):
    filename = filedialog.askopenfilename()
    # print("Функция update_file_label запущена с параметрами:", label, formats, alternative_label)
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


import re

def on_validate(param):
    # Если передан объект события, получаем текст из поля
    if isinstance(param, tk.Event):
        entered_text = pages.get()  # Получаем введенный текст
    else:
        entered_text = param  # Используем переданный текст напрямую

    # Валидация текста
    if validate_input_pages(entered_text):
        print("Введенные данные корректны")
        pages.configure(fg_color="lightgreen")  # Зеленый цвет при корректном вводе
        invalid_pages_label.grid_remove()  # Убираем лейбл об ошибке
    else:
        print("Введенные данные некорректны")
        pages.configure(fg_color="lightcoral")  # Красный цвет при ошибке
        eval(flatten_dict(elements[current_mode])[invalid_pages_label])  # Показать лейбл об ошибке

    auto_resize_window()


# Функция-валидатор
def validate_input_pages(text):
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
def on_click(event):
    if event.widget != pages:  # Проверяем, что клик был не по полю ввода
        on_validate(event)



if __name__ == "__main__":
    # Создаем главное окно и запускаем цикл
    root = ctk.CTk()  # Главное окно
    modes_window = ModesWindow(root)  # Окно с кнопкой для объединения PDF

    root.mainloop()  # Запускаем цикл событий главного окна
