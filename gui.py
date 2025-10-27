import tkinter as tk
from tkinter import messagebox
import threading
import main

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

# создание окна
root = tk.Tk()
root.title("Project")
root.geometry("500x250")

# кнопка запуска
run_button = tk.Button(root, text="Запустить", command=run_main, font=("Arial", 12))
run_button.pack(pady=5)

# индикатор статуса
status_label = tk.Label(root, text="Не запущено", bg="red", fg="white", font=("Arial", 12), width=15)
status_label.pack(pady=5)

root.mainloop()
