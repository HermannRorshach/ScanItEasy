import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from time import sleep


# Цветовая палитра
bg_color = "#2f2f2f"  # Темно-серый
btn_bg_color = "#003366"  # Темно-синий
btn_fg_color = "#FFFFFF"  # Белый
label_fg_color = "#B0B0B0"  # Светло-серый для текста
entry_bg_color = "#F4F4F4"  # Светлый серый для фона ввода

win = tk.Tk()
win.title("Сканирование")
win.geometry("500x500")
win.resizable(False, False)

progress = ttk.Progressbar(win, mode="indeterminate", length=200)
progress.grid(row=8, column=0, pady=10, padx=70, sticky="w")


log_box = ScrolledText(win, height=10, width=50, bg=bg_color, fg=label_fg_color, state="disabled")
log_box.grid(row=15, column=0, pady=10, padx=70, sticky="w")

def log_message(message):
    log_box.config(state="normal")
    log_box.insert("end", message + "\n")
    log_box.config(state="disabled")
    log_box.see("end")  # Автоматическая прокрутка вниз

def console():
    log_message("Программа запущена.")
    for i in range(100):
        log_message(f"Выполняем задачу №{i}")

def start_animation():
    progress.start(10)  # Запускаем анимацию с интервалом 10 мс
    win.update()

def stop_animation():
    progress.stop()  # Останавливаем анимацию
    # progress.grid_remove()  # Убираем Progressbar с интерфейса

# Пример использования:
def simulate_long_task():
    start_animation()
    win.after(3000, stop_animation)  # Симуляция задачи на 3 секунды

btn_long_task = tk.Button(win, text="Начать долгую задачу", command=simulate_long_task)
btn_long_task.grid(row=9, column=0, pady=10, padx=70, sticky="w")

btn_console = tk.Button(win, text="Начать выполнение 100 задач", command=console)
btn_console.grid(row=11, column=0, pady=10, padx=70, sticky="w")

# # Пример с изображениями:
# custom_radio_var = tk.StringVar(value="option1")

# def select_radio(value):
#     custom_radio_var.set(value)

# radio_frame = tk.Frame(win, bg=bg_color)
# radio_frame.grid(row=11, column=0, pady=10, padx=70, sticky="w")

# red_img = tk.PhotoImage(file="red_icon.png")  # Ваши иконки
# blue_img = tk.PhotoImage(file="blue_icon.png")

# red_button = tk.Button(radio_frame, image=red_img, command=lambda: select_radio("red"), bg=bg_color, borderwidth=0)
# red_button.grid(row=0, column=0)

# blue_button = tk.Button(radio_frame, image=blue_img, command=lambda: select_radio("blue"), bg=bg_color, borderwidth=0)
# blue_button.grid(row=0, column=1)

# # Пример получения выбранного значения:
# print(custom_radio_var.get())



win.mainloop()