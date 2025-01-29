import os
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import logging
# from modes import ModesWindow


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('editor_log.txt', encoding='utf-8', mode='w'),
        logging.StreamHandler()
    ]
)


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

        # Создаем и показываем окно ModesWindow
        self.master = ModesWindow(self)  # Передаем master как родительское окно
        self.master.pack(fill="both", expand=True)


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


if __name__ == "__main__":
    app = GraphicalEditor()
    app.mainloop()
