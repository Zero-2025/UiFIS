import tkinter as tk
from tkinter import ttk, messagebox

def calculate_k_e():
    """
    Расчет коэффициента сохранения эффективности K_Э
    Формула: K_Э = P_факт / P_ном
    где P_факт - фактическая производительность,
    P_ном - номинальная производительность
    """
    try:
        # Получаем данные из полей ввода
        P_nom = float(entry_nominal.get())
        P_fact = float(entry_actual.get())
        hours = float(entry_hours.get())
        
        # Проверка на корректность данных
        if P_nom <= 0:
            messagebox.showerror("Ошибка", "Номинальная производительность должна быть больше 0")
            return
        if P_fact < 0:
            messagebox.showerror("Ошибка", "Фактическая производительность не может быть отрицательной")
            return
        if hours <= 0:
            messagebox.showerror("Ошибка", "Количество часов должно быть больше 0")
            return
        if P_fact > P_nom:
            messagebox.showwarning("Предупреждение", 
                                 "Фактическая производительность превышает номинальную.\n"
                                 "Это может указывать на ошибку в данных.")
        
        # Расчет коэффициента
        K_e = P_fact / P_nom
        
        # Вывод результата
        result_text = f"Результаты расчета:\n\n"
        result_text += f"Номинальная производительность: {P_nom:.2f} ед./ч\n"
        result_text += f"Фактическая производительность: {P_fact:.2f} ед./ч\n"
        result_text += f"Период наблюдения: {hours:.0f} часов\n"
        result_text += f"\nКоэффициент сохранения эффективности K_Э = {K_e:.4f}\n"
        result_text += f"Или в процентах: {K_e*100:.2f}%"
        
        # Обновляем текстовое поле с результатами
        result_text_area.config(state='normal')
        result_text_area.delete(1.0, tk.END)
        result_text_area.insert(1.0, result_text)
        result_text_area.config(state='disabled')
        
        # Обновляем прогресс-бар (визуализация коэффициента)
        progress_bar['value'] = K_e * 100
        
        # Устанавливаем цвет прогресс-бара в зависимости от значения
        if K_e >= 0.9:
            progress_bar['style'] = 'green.Horizontal.TProgressbar'
        elif K_e >= 0.7:
            progress_bar['style'] = 'yellow.Horizontal.TProgressbar'
        else:
            progress_bar['style'] = 'red.Horizontal.TProgressbar'
            
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")
    except ZeroDivisionError:
        messagebox.showerror("Ошибка", "Номинальная производительность не может быть равна 0")

def fill_example():
    """Заполнение полей примером из задания"""
    entry_nominal.delete(0, tk.END)
    entry_nominal.insert(0, "100")
    
    entry_actual.delete(0, tk.END)
    entry_actual.insert(0, "95")
    
    entry_hours.delete(0, tk.END)
    entry_hours.insert(0, "2000")

def clear_all():
    """Очистка всех полей"""
    entry_nominal.delete(0, tk.END)
    entry_actual.delete(0, tk.END)
    entry_hours.delete(0, tk.END)
    
    result_text_area.config(state='normal')
    result_text_area.delete(1.0, tk.END)
    result_text_area.config(state='disabled')
    
    progress_bar['value'] = 0

# Создание главного окна
root = tk.Tk()
root.title("Расчет коэффициента сохранения эффективности K_Э")
root.geometry("600x550")
root.resizable(False, False)

# Устанавливаем стиль для прогресс-бара
style = ttk.Style()
style.theme_use('clam')

# Настраиваем цвета для прогресс-бара
style.configure('green.Horizontal.TProgressbar', 
                background='green', 
                troughcolor='lightgray')
style.configure('yellow.Horizontal.TProgressbar', 
                background='orange', 
                troughcolor='lightgray')
style.configure('red.Horizontal.TProgressbar', 
                background='red', 
                troughcolor='lightgray')

# Заголовок
title_label = tk.Label(root, 
                      text="Расчет коэффициента сохранения эффективности K_Э", 
                      font=("Arial", 14, "bold"),
                      pady=10)
title_label.pack()

# Фрейм для ввода данных
input_frame = tk.Frame(root, padx=20, pady=10)
input_frame.pack(fill="x")

# Номинальная производительность
tk.Label(input_frame, text="Номинальная производительность (ед./ч):", 
         font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
entry_nominal = tk.Entry(input_frame, font=("Arial", 10), width=20)
entry_nominal.grid(row=0, column=1, padx=10, pady=5)

# Фактическая производительность
tk.Label(input_frame, text="Фактическая производительность (ед./ч):", 
         font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
entry_actual = tk.Entry(input_frame, font=("Arial", 10), width=20)
entry_actual.grid(row=1, column=1, padx=10, pady=5)

# Период наблюдения
tk.Label(input_frame, text="Период наблюдения (часов):", 
         font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
entry_hours = tk.Entry(input_frame, font=("Arial", 10), width=20)
entry_hours.grid(row=2, column=1, padx=10, pady=5)

# Фрейм для кнопок
button_frame = tk.Frame(root, pady=10)
button_frame.pack()

# Кнопки управления
ttk.Button(button_frame, text="Рассчитать", 
          command=calculate_k_e, 
          width=15).pack(side="left", padx=5)
ttk.Button(button_frame, text="Заполнить пример", 
          command=fill_example, 
          width=15).pack(side="left", padx=5)
ttk.Button(button_frame, text="Очистить все", 
          command=clear_all, 
          width=15).pack(side="left", padx=5)

# Фрейм для результатов
result_frame = tk.Frame(root, padx=20, pady=10)
result_frame.pack(fill="both", expand=True)

# Текстовое поле для вывода результатов
tk.Label(result_frame, text="Результаты:", 
         font=("Arial", 11, "bold")).pack(anchor="w")
result_text_area = tk.Text(result_frame, 
                          height=8, 
                          width=60, 
                          font=("Arial", 10),
                          wrap="word",
                          state='disabled',
                          bg="#f0f0f0")
result_text_area.pack(pady=5)

# Прогресс-бар для визуализации коэффициента
tk.Label(result_frame, text="Визуализация коэффициента K_Э:", 
         font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 5))
progress_bar = ttk.Progressbar(result_frame, 
                              length=400, 
                              mode='determinate',
                              style='green.Horizontal.TProgressbar')
progress_bar.pack(pady=5)

# Легенда для прогресс-бара
legend_frame = tk.Frame(result_frame)
legend_frame.pack(pady=5)

tk.Label(legend_frame, text="Отличный (≥90%)", 
         fg="green", font=("Arial", 9)).pack(side="left", padx=10)
tk.Label(legend_frame, text="Удовлетворительный (70-90%)", 
         fg="orange", font=("Arial", 9)).pack(side="left", padx=10)
tk.Label(legend_frame, text="Низкий (<70%)", 
         fg="red", font=("Arial", 9)).pack(side="left", padx=10)

# Фрейм для формулы
formula_frame = tk.Frame(root, pady=10, padx=20)
formula_frame.pack(fill="x")

# Пояснение формулы
formula_text = "Формула расчета:\nK_Э = P_факт / P_ном\nгде:\n"
formula_text += "K_Э - коэффициент сохранения эффективности\n"
formula_text += "P_факт - фактическая средняя производительность (ед./ч)\n"
formula_text += "P_ном - номинальная производительность (ед./ч)"

formula_label = tk.Label(formula_frame, 
                        text=formula_text,
                        font=("Arial", 9),
                        justify="left",
                        bg="#e8f4f8",
                        relief="solid",
                        padx=10,
                        pady=10,
                        borderwidth=1)
formula_label.pack(fill="x")

# Информация о программе
info_label = tk.Label(root, 
                     text="© Программа для расчета коэффициента сохранения эффективности",
                     font=("Arial", 8),
                     fg="gray",
                     pady=5)
info_label.pack()

# Запускаем главный цикл
root.mainloop()