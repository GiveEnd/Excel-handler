import tkinter as tk
from tkinter import messagebox
import threading
import main
import gemini_api_question
from tkinter import ttk
from tkinter import filedialog
import os

selected_file_path = "" 

def run_main():
    # изменение статуса
    status_label.config(text="Ожидайте...", bg="orange")

    def task():
        try:
            # запуск main.py
            main.main()
            # После завершения — обновляем статус
            status_label.config(text="Готово", bg="green")
        except Exception as e:
            status_label.config(text="Ошибка", bg="red")
            messagebox.showerror("Ошибка", f"main.py завершился с ошибкой:\n{e}")

    # запуск main.py
    threading.Thread(target=task).start()

def set_text1():
    status_label1.config(text="Ожидайте...", bg="orange")

    def task():
        text = entry1.get()   

        if selected_file_path:
            input_file = selected_file_path
        else:
            input_file = 0

        gemini_api_question.run(text, input_file)
        status_label1.config(text="Готово", bg="green")

    threading.Thread(target=task, daemon=True).start()



def add_to_entry(event=None):
    # Берём выбранное значение из Combobox
    selected = combo.get()
    # Добавляем его в Entry
    entry1.delete(0, tk.END)  # очищаем Entry
    entry1.insert(0, selected) # вставляем выбранный текст




def choose_file():
    global selected_file_path
    selected_file_path = filedialog.askopenfilename()




# создание окна
root = tk.Tk()
root.title("Project")
root.geometry("700x250")

# разбивка таблицы
frame0 = tk.Frame(root)
frame0.pack(pady=10, padx=10, fill="x")

tk.Label(frame0, text="Преобразование исходной таблицы", font=("Arial", 12)).pack(anchor="w")

# кнопка запуска
run_button = tk.Button(frame0, text="Запустить", command=run_main)
run_button.pack(side=tk.LEFT, padx=(0,10)) 

# индикатор статуса
status_label = tk.Label(frame0, text="Не запущено", bg="red", fg="white", width=11)
status_label.pack(side=tk.LEFT)




# текстовое поле
frame1 = tk.Frame(root)
frame1.pack(pady=10, padx=10, fill="x")

tk.Label(frame1, text="Запрос:", font=("Arial", 12)).pack(anchor="w")

entry1 = tk.Entry(frame1, font=("Arial", 11))
entry1.pack(side=tk.LEFT, expand=True, fill="x", padx=(0,10))

btn1 = tk.Button(frame1, text="Запустить", command=set_text1)
btn1.pack(side=tk.LEFT)

status_label1 = tk.Label(frame1, text="Не запущено", bg="red", fg="white", width=11)
status_label1.pack(side=tk.LEFT, padx=5)




# выпадающий список
frame2 = tk.Frame(root)
frame2.pack(pady=10, padx=10, fill="x")
tk.Label(frame2, text="Шаблоны:", font=("Arial", 12)).pack(anchor="w")

options = ["Определи страну регистрации каждой компании из колонки «Компания». создай справа новую колонку «Страна» и напиши в соответствующую ячейку ответ (название страны регистрации компании из колонки «Компания»). Создай еще одну колонку справа для внесения результатов самопроверки. Проверь свой ответ. Если в ответе есть ошибка или информация требует ручной перепроверки из-за наличия двух и более вариантов ответа в этой колонке, то поставь в ней восклицательный знак."         
             ,
               "Создай колонку Самопроверка 2. Проверь свой ответ в колонке Страна. Советует ли он данным колонки «компания» и «проект». Если нет, поставь восклицательный знак в колонку. "
               , "Вариант 3"]
combo = ttk.Combobox(frame2, values=options, font=("Arial", 12), width=15)
combo.pack(side=tk.LEFT)
# combo.pack(fill="x")
combo.bind("<<ComboboxSelected>>", add_to_entry)  # событие выбора

#выбор файла
choose_btn = tk.Button(frame2, text="Выбрать файл...", command=choose_file)
choose_btn.pack(side=tk.LEFT, padx=(10,0))

root.mainloop()
