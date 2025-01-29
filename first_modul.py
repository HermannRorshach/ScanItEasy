import customtkinter as ctk
import tkinter as tk


# Класс ModesWindow
class ModesWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app = master  # Сохраняем ссылку на родительское окно

        self.configure(bg_color="white")

        self.merge_button = ctk.CTkButton(
            self, text="Объединить PDF", command=self.on_merge_button_click
        )
        self.merge_button.pack(pady=20)

    def on_merge_button_click(self):
        self.app.switch_to_merge_pdf()  # Переключаем окно на GraphicalEditor


# Класс GraphicalEditor
class GraphicalEditor(ctk.CTk):
    def __init__(self, master=None):  # Принимаем master как аргумент конструктора
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
        back_button = tk.Button(
            self, text="Назад", font=("Arial", 14, "normal"),
            fg="white", padx=10, pady=10, bg=self["bg"], activebackground=self["bg"],
            borderwidth=0, command=self.on_back_button_click, compound="left", relief="flat"
        )

        back_button.grid(row=0, column=0, padx=35, pady=5, sticky="w")

    def on_back_button_click(self):
        self.destroy()  # Закрываем текущее окно (GraphicalEditor)
        self.master.switch_to_modes()  # Возвращаем в ModesWindow


# Главный класс приложения
class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry('700x600')
        self.title("Главное окно")

        # Создаем и показываем окно ModesWindow
        self.modes_window = ModesWindow(self)
        self.modes_window.pack(fill="both", expand=True)

        self.merge_pdf_window = None

    def switch_to_merge_pdf(self):
        # Деактивируем окно modes
        self.modes_window.pack_forget()

        # Создаем и активируем окно merge_pdf
        self.merge_pdf_window = GraphicalEditor(self)
        self.merge_pdf_window.pack(fill="both", expand=True)

    def switch_to_modes(self):
        # Деактивируем окно merge_pdf
        self.merge_pdf_window.pack_forget()

        # Возвращаем окно modes
        self.modes_window.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = MainApplication()  # Создаем главное окно
    app.mainloop()  # Запускаем цикл событий
