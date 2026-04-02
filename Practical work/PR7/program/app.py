import tkinter as tk
from tkinter import messagebox

def calculate_coefficient():
    """Вычисляет коэффициент выявления ошибок."""
    try:
        # Получаем значения из полей ввода
        total_text = entry_total.get().strip()
        detected_text = entry_detected.get().strip()
        
        # Проверка на пустые поля
        if not total_text or not detected_text:
            messagebox.showwarning("Внимание", "Заполните оба поля!")
            return
        
        # Преобразуем в числа
        total_errors = float(total_text)
        detected_errors = float(detected_text)
        
        # Проверка на отрицательные числа
        if total_errors < 0:
            messagebox.showerror("Ошибка", "Общее количество ошибок не может быть отрицательным!")
            return
        
        if detected_errors < 0:
            messagebox.showerror("Ошибка", "Количество выявленных ошибок не может быть отрицательным!")
            return
        
        # Проверка, что выявленных не больше общего количества
        if detected_errors > total_errors:
            messagebox.showerror("Ошибка", "Выявленных ошибок не может быть больше общего количества!")
            return
        
        # Расчет коэффициента (в процентах)
        if total_errors == 0:
            coefficient = 0
        else:
            coefficient = (detected_errors / total_errors) * 100
        
        # Вывод результата
        result_text = f"K_выявл = {coefficient:.2f}%"
        label_result.config(text=result_text, fg="green")
        
        # Дополнительная информация
        label_detail.config(text=f"Формула: {detected_errors:.0f} / {total_errors:.0f} × 100% = {coefficient:.2f}%")
        
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числа (целые или дробные)!")

def clear_fields():
    """Очищает поля ввода."""
    entry_total.delete(0, tk.END)
    entry_detected.delete(0, tk.END)
    label_result.config(text="K_выявл = ?", fg="blue")
    label_detail.config(text="")

def set_example():
    """Устанавливает пример с 80 и 70."""
    entry_total.delete(0, tk.END)
    entry_total.insert(0, "80")
    entry_detected.delete(0, tk.END)
    entry_detected.insert(0, "70")
    calculate_coefficient()

# Создаем главное окно
root = tk.Tk()
root.title("Расчет коэффициента выявления ошибок")
root.geometry("450x300")
root.configure(bg="#f0f0f0")

# Заголовок
title_label = tk.Label(root, text="Коэффициент выявления ошибок", 
                       font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#333")
title_label.pack(pady=15)

# Рамка для ввода данных
input_frame = tk.Frame(root, bg="#f0f0f0")
input_frame.pack(pady=10)

# Поле для общего количества
tk.Label(input_frame, text="Общее количество ошибок:", 
         font=("Arial", 10), bg="#f0f0f0", width=22, anchor="w").grid(row=0, column=0, padx=5, pady=8)
entry_total = tk.Entry(input_frame, width=15, font=("Arial", 10), justify="right")
entry_total.grid(row=0, column=1, padx=5, pady=8)
entry_total.bind('<Return>', lambda event: calculate_coefficient())

# Поле для выявленных ошибок
tk.Label(input_frame, text="Количество выявленных ошибок:", 
         font=("Arial", 10), bg="#f0f0f0", width=22, anchor="w").grid(row=1, column=0, padx=5, pady=8)
entry_detected = tk.Entry(input_frame, width=15, font=("Arial", 10), justify="right")
entry_detected.grid(row=1, column=1, padx=5, pady=8)
entry_detected.bind('<Return>', lambda event: calculate_coefficient())

# Кнопки
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=15)

calc_button = tk.Button(button_frame, text="Рассчитать", command=calculate_coefficient,
                        bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                        padx=20, pady=5, cursor="hand2")
calc_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(button_frame, text="Очистить", command=clear_fields,
                         bg="#f44336", fg="white", font=("Arial", 10),
                         padx=20, pady=5, cursor="hand2")
clear_button.pack(side=tk.LEFT, padx=5)

example_button = tk.Button(button_frame, text="Пример (80/70)", command=set_example,
                           bg="#2196F3", fg="white", font=("Arial", 10),
                           padx=20, pady=5, cursor="hand2")
example_button.pack(side=tk.LEFT, padx=5)

# Результат
result_frame = tk.Frame(root, bg="#ffffff", relief="solid", borderwidth=1)
result_frame.pack(pady=15, padx=20, fill="both")

label_result = tk.Label(result_frame, text="K_выявл = ?", 
                        font=("Arial", 16, "bold"), bg="#ffffff", fg="blue")
label_result.pack(pady=10)

label_detail = tk.Label(result_frame, text="", 
                        font=("Arial", 9), bg="#ffffff", fg="#666")
label_detail.pack(pady=5)

# Информация внизу
info_label = tk.Label(root, text="Формула: K = (выявленные / общие) × 100%", 
                      font=("Arial", 8), bg="#f0f0f0", fg="#888")
info_label.pack(side=tk.BOTTOM, pady=5)

# Запускаем с примером по умолчанию
root.after(100, set_example)

# Запуск приложения
root.mainloop()