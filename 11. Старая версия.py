import tkinter as tk  # Импортируем модуль tkinter для создания графического интерфейса
from tkinter import filedialog  # Импортируем диалоговое окно для выбора файлов

def scan(settings):  # Определяем функцию для обработки настроек
    print(f"Выбранные настройки: {settings}")  # Выводим настройки на экран

def update_mode():  # Определяем функцию для обновления отображаемых элементов в зависимости от выбранного режима
    # Очистка текущего отображения
    for widget in custom_frame.winfo_children():  # Перебираем все виджеты в custom_frame
        widget.grid_forget()  # Скрываем текущие виджеты

    # Сначала показываем элементы для выбранного режима
    if mode_var.get() == "custom":  # Если выбран пользовательский режим
        # Добавляем элементы для пользовательского режима
        custom_frame.grid(row=6, column=0, pady=10, sticky="nsew")  # Отображаем custom_frame
        color_label.grid(row=0, column=0, sticky="w", padx=70)  # Отображаем лейбл для цвета
        color_red.grid(row=1, column=0, sticky="w", padx=70)  # Отображаем кнопку для красного цвета
        color_blue.grid(row=2, column=0, sticky="w", padx=70)  # Отображаем кнопку для синего цвета
        pages_label.grid(row=3, column=0, sticky="w", padx=70)  # Отображаем лейбл для выбора страниц
        pages_entry.grid(row=4, column=0, sticky="w", padx=70)  # Отображаем поле для ввода страниц
        signature_label.grid(row=5, column=0, sticky="w", padx=70)  # Отображаем лейбл для подписи
        signature_yes.grid(row=6, column=0, sticky="w", padx=70)  # Отображаем кнопку "Да" для подписи
        signature_no.grid(row=7, column=0, sticky="w", padx=70)  # Отображаем кнопку "Нет" для подписи
    else:  # Если выбран не пользовательский режим
        custom_frame.grid_forget()  # Прячем custom_frame

def update_file_label(label):  # Функция для обновления текста метки с путем к файлу
    filename = filedialog.askopenfilename()  # Открываем диалоговое окно для выбора файла
    label.config(text=filename if filename else None)  # Если файл выбран, показываем его путь, иначе — ничего

win = tk.Tk()  # Создаем объект окна
win.title("Сканирование")  # Устанавливаем заголовок окна
win.geometry("500x500")  # Устанавливаем размер окна
win.resizable(False, False)  # Отключаем изменение размеров окна

# Цветовая палитра
bg_color = "#2f2f2f"  # Цвет фона окна
btn_bg_color = "#003366"  # Цвет фона кнопок
btn_fg_color = "#FFFFFF"  # Цвет текста на кнопках
label_fg_color = "#B0B0B0"  # Цвет текста меток
entry_bg_color = "#F4F4F4"  # Цвет фона поля ввода

win.config(bg=bg_color)  # Применяем цвет фона

# Загружаем изображения для радиокнопок
radio_active = tk.PhotoImage(file="icon-radio-button-active.png")  # Изображение активной радиокнопки
radio_inactive = tk.PhotoImage(file="icon-radio-button-not-active.png")  # Изображение неактивной радиокнопки

# Функция для изменения состояния радиокнопки с иконками
def on_mode_change(value):  # Функция для изменения режима
    if value == "default":  # Если выбран режим по умолчанию
        mode_var.set("default")  # Устанавливаем значение переменной режима как "default"
        set_active(mode_default, radio_active)  # Устанавливаем активное состояние для кнопки по умолчанию
        set_active(mode_custom, radio_inactive)  # Устанавливаем неактивное состояние для пользовательской кнопки
    elif value == "custom":  # Если выбран пользовательский режим
        mode_var.set("custom")  # Устанавливаем значение переменной режима как "custom"
        set_active(mode_default, radio_inactive)  # Устанавливаем неактивное состояние для кнопки по умолчанию
        set_active(mode_custom, radio_active)  # Устанавливаем активное состояние для кнопки пользовательского режима

def set_active(button, image):  # Функция для установки изображения радиокнопки
    button.config(image=image)  # Меняем изображение на переданное

# Выбор файлов
btn_file_docx = tk.Button(win, text="Выбрать файл docx", command=lambda: update_file_label(docx_label),
                          bg=btn_bg_color, fg=btn_fg_color, relief="flat")  # Кнопка для выбора файла docx
btn_file_docx.grid(row=0, column=0, pady=10, padx=70, sticky="w")  # Размещаем кнопку

docx_label = tk.Label(win, text=None, fg=label_fg_color, bg=bg_color)  # Метка для отображения пути к файлу docx
docx_label.grid(row=1, column=0, pady=5, padx=70, sticky="w")  # Размещаем метку

btn_file_last_page = tk.Button(win, text="Выбрать файл для последней страницы", command=lambda: update_file_label(last_page_label),
                               bg=btn_bg_color, fg=btn_fg_color, relief="flat")  # Кнопка для выбора файла последней страницы
btn_file_last_page.grid(row=2, column=0, pady=10, padx=70, sticky="w")  # Размещаем кнопку

last_page_label = tk.Label(win, text=None, fg=label_fg_color, bg=bg_color)  # Метка для отображения пути к файлу последней страницы
last_page_label.grid(row=3, column=0, pady=5, padx=70, sticky="w")  # Размещаем метку

# Режимы
mode_var = tk.StringVar(value="default")  # Переменная для хранения выбранного режима
mode_label = tk.Label(win, text="Выберите режим:", fg=label_fg_color, bg=bg_color)  # Лейбл для выбора режима
mode_label.grid(row=4, column=0, pady=5, padx=70, sticky="w")  # Размещаем лейбл

# Создаем кнопки с иконками вместо стандартных радиокнопок
mode_default = tk.Button(win, image=radio_inactive, command=lambda: on_mode_change("default"),
                         bg=bg_color, relief="flat")  # Кнопка для выбора режима по умолчанию
mode_default.grid(row=5, column=0, pady=5, padx=70, sticky="w")  # Размещаем кнопку

mode_custom = tk.Button(win, image=radio_inactive, command=lambda: on_mode_change("custom"),
                        bg=bg_color, relief="flat")  # Кнопка для выбора пользовательского режима
mode_custom.grid(row=6, column=0, pady=5, padx=70, sticky="w")  # Размещаем кнопку

# Настройки для пользовательского режима
custom_frame = tk.Frame(win, bg=bg_color)  # Создаем фрейм для пользовательских настроек

# Цвет ленты
color_var = tk.StringVar(value="red")  # Переменная для хранения выбранного цвета ленты
color_label = tk.Label(custom_frame, text="Выберите цвет ленты:", fg=label_fg_color, bg=bg_color)  # Лейбл для выбора цвета ленты

color_red = tk.Button(custom_frame, text="Красный", command=lambda: color_var.set("red"),
                      bg=btn_bg_color, fg=btn_fg_color, relief="flat")  # Кнопка для выбора красного цвета
color_red.grid(row=1, column=0, sticky="w", padx=70)  # Размещаем кнопку

color_blue = tk.Button(custom_frame, text="Синий", command=lambda: color_var.set("blue"),
                       bg=btn_bg_color, fg=btn_fg_color, relief="flat")  # Кнопка для выбора синего цвета
color_blue.grid(row=2, column=0, sticky="w", padx=70)  # Размещаем кнопку

# Выбор страниц
pages_label = tk.Label(custom_frame, text="Выберите страницы:", fg=label_fg_color, bg=bg_color)  # Лейбл для выбора страниц
pages_label.grid(row=3, column=0, sticky="w", padx=70)  # Размещаем лейбл

pages_entry = tk.Entry(custom_frame, bg=entry_bg_color)  # Поле ввода для выбора страниц
pages_entry.grid(row=4, column=0, sticky="w", padx=70)  # Размещаем поле ввода

# Подпись переводчика
signature_var = tk.StringVar(value="yes")  # Переменная для хранения выбора подписи
signature_label = tk.Label(custom_frame, text="Добавить подпись переводчика:", fg=label_fg_color, bg=bg_color)  # Лейбл для подписи
signature_label.grid(row=5, column=0, sticky="w", padx=70)  # Размещаем лейбл

signature_yes = tk.Button(custom_frame, text="Да", command=lambda: signature_var.set("yes"),
                          bg=btn_bg_color, fg=btn_fg_color, relief="flat")  # Кнопка для выбора "Да" для подписи
signature_yes.grid(row=6, column=0, sticky="w", padx=70)  # Размещаем кнопку

signature_no = tk.Button(custom_frame, text="Нет", command=lambda: signature_var.set("no"),
                         bg=btn_bg_color, fg=btn_fg_color, relief="flat")  # Кнопка для выбора "Нет" для подписи
signature_no.grid(row=7, column=0, sticky="w", padx=70)  # Размещаем кнопку


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

# Кнопка для сканирования
btn_scan = tk.Button(win, text="Отсканировать", command=on_scan, bg=btn_bg_color, fg=btn_fg_color)
btn_scan.grid(row=7, column=0, pady=20, padx=70, sticky="w")


win.mainloop()  # Запускаем главный цикл окна
