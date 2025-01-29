import customtkinter as ctk
from modes import ModesWindow
from merge_pdf import GraphicalEditor

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
