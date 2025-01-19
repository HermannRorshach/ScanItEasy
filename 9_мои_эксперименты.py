import tkinter as tk
from tkinter import filedialog

def scan(settings):
    print("Выбранные настройки:", settings)

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

docx_label = tk.Label(win, text="Название выбранного файла", fg=label_fg_color, bg=bg_color)
docx_label.grid(row=1, column=0, pady=5, padx=70, sticky="w")

btn_file_last_page = tk.Button(win, text="Выбрать файл для последней страницы", command=lambda: update_file_label(last_page_label),
                               bg=btn_bg_color, fg=btn_fg_color, relief="flat")
btn_file_last_page.grid(row=2, column=0, pady=10, padx=70, sticky="w")

last_page_label = tk.Label(win, text="Название выбранного файла", fg=label_fg_color, bg=bg_color)
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
signature_var = tk.StringVar(value="no")
signature_label = tk.Label(custom_frame, text="Нужна ли подпись переводчика?", fg=label_fg_color, bg=bg_color)

signature_yes = tk.Radiobutton(custom_frame, text="Да", variable=signature_var, value="yes", bg=bg_color, fg=label_fg_color)
signature_no = tk.Radiobutton(custom_frame, text="Нет", variable=signature_var, value="no", bg=bg_color, fg=label_fg_color)

# Кнопка "Отсканировать"
def on_scan():
    settings = {
        "mode": mode_var.get(),
        "color": color_var.get() if mode_var.get() == "custom" else "red",
        "pages": pages_entry.get() if mode_var.get() == "custom" else None,
        "signature": signature_var.get() if mode_var.get() == "custom" else None,
        "file_docx": docx_label.cget("text"),
        "file_last_page": last_page_label.cget("text"),
    }
    scan(settings)

btn_scan = tk.Button(win, text="Отсканировать", command=on_scan, bg=btn_bg_color, fg=btn_fg_color, relief="flat")
btn_scan.grid(row=7, column=0, pady=20, padx=70, sticky="w")

# Функция обновления метки с именем выбранного файла
def update_file_label(label):
    filename = filedialog.askopenfilename()
    label.config(text=filename if filename else "Название выбранного файла")


win.mainloop()
