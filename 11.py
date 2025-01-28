import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('green')

win = ctk.CTk()
window_width = 400
window_height = 350
window_position_horizontal = 400
window_position_vertical = 10
win.geometry(
    f'{window_width}x{window_height}+{window_position_horizontal}+{window_position_vertical}')
win.minsize(300, 300)
win.title("ScanItEasy")
padx = 70
current_mode = "modes"


# Создаём все элементы программы
# Выбор режима программы
mode_var = ctk.StringVar(value="modes")
mode_label = ctk.CTkLabel(win, text="Выберите опцию")
mode_label.grid(row=0, column=0, padx=padx, pady=15, sticky="w")

default_mode = ctk.CTkRadioButton(win, text="Режим по умолчанию", variable=mode_var, value="default_mode", command=lambda: update_elements(mode_var.get()))
default_mode.grid(row=1, column=0, padx=padx, pady=5, sticky="w")

custom_mode = ctk.CTkRadioButton(win, text="Пользовательский режим с настройками", variable=mode_var, value="custom_mode", command=lambda: update_elements(mode_var.get()))
custom_mode.grid(row=2, column=0, padx=padx, pady=5, sticky="w")

additionally_label = ctk.CTkLabel(win, text="Дополнительно:", font=("Arial", 12, "italic"), justify='center')
additionally_label.grid(row=3)

convert_to_pdf = ctk.CTkRadioButton(win, text="Конвертировать docx в pdf", variable=mode_var, value="convert_to_pdf_mode", command=lambda: update_elements(mode_var.get()))
convert_to_pdf.grid(row=4, column=0, padx=padx, pady=5, sticky="w")

merge_pdf = ctk.CTkRadioButton(win, text="Объединить два или несколько pdf", variable=mode_var, value=3)
merge_pdf.grid(row=5, column=0, padx=padx, pady=5, sticky="w")

grayscale_mode = ctk.CTkRadioButton(win, text="Сделать pdf чёрно-белым", variable=mode_var, value="grayscale_mode", command=lambda: update_elements(mode_var.get()))
grayscale_mode.grid(row=6, column=0, padx=padx, pady=5, sticky="w")

compress_mode = ctk.CTkRadioButton(win, text="Сжать pdf", variable=mode_var, value="compress_mode", command=lambda: update_elements(mode_var.get()))
compress_mode.grid(row=7, column=0, padx=padx, pady=5, sticky="w")

convert_to_png = ctk.CTkRadioButton(win, text="Конвертировать pdf в png", variable=mode_var, value="convert_to_png_mode", command=lambda: update_elements(mode_var.get()))
convert_to_png.grid(row=8, column=0, padx=padx, pady=5, sticky="w")


# Кнопка Назад
dark_image = tk.PhotoImage(file="dark.png")  # Используется для кнопки при наведении и нажатии
light_image = tk.PhotoImage(file="light.png")  # Используется для кнопки в обычном состоянии

# Функция для обработки событий кнопки назад
def on_hover(event):
    back_button.config(image=dark_image)

def on_leave(event):
    back_button.config(image=light_image)


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

back_button.bind("<Enter>", on_hover)  # При наведении
back_button.bind("<Leave>", on_leave)  # При уходе курсора

# Режим по умолчанию
header_label = ctk.CTkLabel(win, text="Режим по умолчанию")
btn_file_docx = ctk.CTkButton(
    win, text="Выберите файл для сканирования",
    command=lambda: update_file_label(
        docx_label, ["docx"], invalid_docx_label))
docx_label = ctk.CTkLabel(win, text=None)
invalid_docx_label = ctk.CTkLabel(win, text="Файл должен быть формата docx", text_color="red", padx=20)
btn_file_last_page = ctk.CTkButton(
    win, text="Выберите файл для последней части документа",
    command=lambda: update_file_label(
        last_page_label, ["pdf", "jpeg", "jpg", "png"],
        invalid_last_page_label))
last_page_label = ctk.CTkLabel(win, text=None)
invalid_last_page_label = ctk.CTkLabel(win, text="Файл должен быть формата pdf, jpeg, jpg или png", text_color="red", padx=20)
progress_label = ctk.CTkLabel(win, text="0%")
progress_bar = ctk.CTkProgressBar(win, width=300, height=25)
conditions_message_label = ctk.CTkLabel(win, text="Для запуска сканирования нужно выбрать файл в формате docx", text_color="red", padx=20)

btn_to_work = ctk.CTkButton(win, fg_color="red",  # Основной цвет кнопки
    hover_color="#8B0000", text="Сканировать", command=lambda: work())

# Пользовательский режим с настройками
color_var = ctk.IntVar(value=0) # Значение цвета ленточки
color_label = ctk.CTkLabel(win, text="Выберите цвет ленточки")


red = ctk.CTkRadioButton(win, text="Красный", variable=color_var, value=0, command=lambda: print("Цвет ленты: красный"))
blue = ctk.CTkRadioButton(win, text="Синий", variable=color_var, value=1, command=lambda: print("Цвет ленты: Синий"))

pages_label = ctk.CTkLabel(win, text="Выберите страницы")
text_help_label = ctk.CTkLabel(win, text="Если нужны все страницы, оставьте поле пустым", font=("Arial", 12, "italic"), text_color="green", justify='center')
pages = ctk.CTkEntry(win,
                     placeholder_text="Введите номера страниц через запятую и/или диапазон страниц через дефис",   # Текст-подсказка
                     fg_color="lightgray",                # Цвет фона
                     placeholder_text_color="Gray",
                     text_color="black",                  # Цвет текста
                     width=470,                           # Ширина поля
                     corner_radius=10,                    # Скругленные углы
                     font=("Arial", 12),                   # Шрифт текста
                     )
invalid_pages_label = ctk.CTkLabel(win, text="Введите номера страниц через запятую и/или диапазон страниц через дефис", text_color="red", padx=20)

# Подпись переводчика
signature_var = ctk.IntVar(value=1)
signature_label = ctk.CTkLabel(win, text="Нужна ли подпись переводчика?")

signature_yes = ctk.CTkRadioButton(win, text="Да", variable=signature_var, value=1, command=lambda: print("Подпись переводчика нужна"))
signature_no = ctk.CTkRadioButton(win, text="Нет", variable=signature_var, value=0, command=lambda: print("Подпись переводчика не нужна"))

# Режим конвертации из docx в pdf
is_compression_needed = ctk.BooleanVar(value=True)
is_compression_needed_checkbox = ctk.CTkCheckBox(
    master=win,
    text="Сжать итоговый pdf",
    variable=is_compression_needed,
    command=lambda: print(is_compression_needed)
)

# Режим превращения pdf в чёрно-белый документ
btn_file_pdf = ctk.CTkButton(
    win, text="Выберите pdf-файл",
    command=lambda: update_file_label(
        pdf_label, ["pdf"], invalid_pdf_label))
pdf_label = ctk.CTkLabel(win, text=None)
invalid_pdf_label = ctk.CTkLabel(win, text="Файл должен быть формата pdf", text_color="red", padx=20)

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

# window_sizes = {
#     "modes": {"window_widht": 400, "window_height": 300},
#     "default_mode": {"window_widht": 400, "window_height": 200},
#     "custom_mode": {"window_widht": 400, "window_height": 200},
#     "convert_to_pdf_mode": {"window_widht": 400, "window_height": 200},
# }

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
    max_width_element = max(
        [element for element in flatten_dict(elements[current_mode]).keys() if element.winfo_ismapped()],
        key=lambda x: x.winfo_reqwidth()
    )
    # print(len(flatten_dict(elements[current_mode]).keys()))
    # print("Самый большой элемент:", max_width_element._text)
    active_widgets_width = [widget.winfo_height() for widget in win.winfo_children() if widget.winfo_ismapped()]
    total_height = sum(active_widgets_width)

    # Устанавливаем предварительный размер окна
    win.geometry(f"{max_width_element.winfo_reqwidth() + 2 * padx}x{total_height + 12 * len(active_widgets_width)}")
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

# Привязка события для проверки при клике на любое место
win.bind("<Button-1>", on_click)  # Привязка на клик по окну
pages.bind("<FocusOut>", on_validate)

def add_label(row, text):  # создаём функцию, которая добавляет лейбл на окно

    ctk.CTkLabel(
        win, text=text, text_color="red", padx=20).grid(
            row=row, column=0, pady=5, padx=70, sticky="w")


win.mainloop()
