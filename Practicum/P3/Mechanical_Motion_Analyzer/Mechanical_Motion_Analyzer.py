import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class MotionAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор механического движения")
        self.root.geometry("900x700")
        
        # Основные переменные
        self.v0_var = tk.DoubleVar(value=0.0)
        self.a_var = tk.DoubleVar(value=0.0)
        self.t_var = tk.DoubleVar(value=0.0)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Анализатор механического движения", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Основной фрейм
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Левая панель - входные данные и результаты
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Входные данные
        input_frame = tk.LabelFrame(left_frame, text="Входные данные", font=("Arial", 10, "bold"))
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Начальная скорость
        v0_frame = tk.Frame(input_frame)
        v0_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(v0_frame, text="Начальная скорость:", width=20, anchor='w').pack(side=tk.LEFT)
        v0_entry = tk.Entry(v0_frame, textvariable=self.v0_var, width=15)
        v0_entry.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(v0_frame, text="м/с").pack(side=tk.LEFT, padx=(5, 0))
        
        # Ускорение
        a_frame = tk.Frame(input_frame)
        a_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(a_frame, text="Ускорение:", width=20, anchor='w').pack(side=tk.LEFT)
        a_entry = tk.Entry(a_frame, textvariable=self.a_var, width=15)
        a_entry.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(a_frame, text="м/с²").pack(side=tk.LEFT, padx=(5, 0))
        
        # Время движения
        t_frame = tk.Frame(input_frame)
        t_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(t_frame, text="Время движения:", width=20, anchor='w').pack(side=tk.LEFT)
        t_entry = tk.Entry(t_frame, textvariable=self.t_var, width=15)
        t_entry.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(t_frame, text="с").pack(side=tk.LEFT, padx=(5, 0))
        
        # Кнопки
        button_frame = tk.Frame(input_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        calc_button = tk.Button(button_frame, text="Рассчитать", command=self.calculate,
                               bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        calc_button.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        clear_button = tk.Button(button_frame, text="Очистить", command=self.clear_all,
                                bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        clear_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Результаты
        results_frame = tk.LabelFrame(left_frame, text="Результаты", font=("Arial", 10, "bold"))
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Тип движения
        self.type_label = tk.Label(results_frame, text="Тип движения:", font=("Arial", 10))
        self.type_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Пройденный путь
        self.distance_label = tk.Label(results_frame, text="Пройденный путь:", font=("Arial", 10))
        self.distance_label.pack(anchor='w', padx=10, pady=5)
        
        # Конечная скорость
        self.velocity_label = tk.Label(results_frame, text="Конечная скорость:", font=("Arial", 10))
        self.velocity_label.pack(anchor='w', padx=10, pady=5)
        
        # Описание движения
        self.description_label = tk.Label(results_frame, text="Описание движения:", 
                                         font=("Arial", 10), wraplength=350, justify=tk.LEFT)
        self.description_label.pack(anchor='w', padx=10, pady=(5, 10))
        
        # Уравнение движения
        self.equation_label = tk.Label(results_frame, text="Уравнение:", 
                                      font=("Arial", 10), wraplength=350, justify=tk.LEFT)
        self.equation_label.pack(anchor='w', padx=10, pady=(0, 10))
        
        # Правая панель - график
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        graph_frame = tk.LabelFrame(right_frame, text="График зависимости пути от времени", 
                                   font=("Arial", 10, "bold"))
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание фигуры matplotlib
        self.figure, self.ax = plt.subplots(figsize=(6, 4), dpi=80)
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Инициализация пустого графика
        self.init_graph()
    
    def init_graph(self):
        """Инициализация пустого графика"""
        self.ax.clear()
        self.ax.set_xlabel("Время, с", fontsize=10)
        self.ax.set_ylabel("Путь, м", fontsize=10)
        self.ax.set_title("График не построен (время = 0)", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.canvas.draw()
    
    def calculate(self):
        """Выполнение расчетов"""
        try:
            # Получение значений
            v0 = float(self.v0_var.get())
            a = float(self.a_var.get())
            t = float(self.t_var.get())
            
            if t < 0:
                messagebox.showerror("Ошибка", "Время не может быть отрицательным!")
                return
            
            # Расчет параметров движения
            s = v0 * t + (a * t**2) / 2
            v_final = v0 + a * t
            
            # Определение типа движения
            if a > 0:
                motion_type = "Равноускоренное движение (разгон)"
                description = f"Ускорение положительное ({a:.2f} м/с²). Тело разгоняется."
            elif a < 0:
                motion_type = "Равноускоренное движение (замедление)"
                description = f"Ускорение отрицательное ({a:.2f} м/с²). Тело замедляется."
            else:
                motion_type = "Равномерное движение"
                description = f"Ускорение равно нулю. Тело движется равномерно."
            
            # Обновление результатов
            self.type_label.config(text=f"Тип движения: {motion_type}")
            self.distance_label.config(text=f"Пройденный путь: {s:.2f} м")
            self.velocity_label.config(text=f"Конечная скорость: {v_final:.2f} м/с")
            self.description_label.config(text=f"Описание движения: {description}")
            
            # Формирование уравнения
            if a >= 0:
                equation = f"S(t) = {v0:.1f}t + ({abs(a):.1f}t²)/2"
            else:
                equation = f"S(t) = {v0:.1f}t - ({abs(a):.1f}t²)/2"
            self.equation_label.config(text=f"Уравнение: {equation}")
            
            # Построение графика
            self.plot_graph(v0, a, t, s)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения!")
    
    def plot_graph(self, v0, a, t, s):
        """Построение графика зависимости пути от времени"""
        self.ax.clear()
        
        # Создание точек для графика
        if t > 0:
            time_points = np.linspace(0, t, 100)
            path_points = v0 * time_points + (a * time_points**2) / 2
            
            # Построение основной кривой
            self.ax.plot(time_points, path_points, 'b-', linewidth=2, label='S(t)')
            
            # Добавление ключевых точек (красные точки)
            key_times = np.linspace(0, t, min(6, int(t) + 2))
            key_paths = v0 * key_times + (a * key_times**2) / 2
            self.ax.plot(key_times, key_paths, 'ro', markersize=6, label='Ключевые точки')
            
            # Конечная точка
            self.ax.plot(t, s, 'ro', markersize=8)
            
            # Настройка графика
            self.ax.set_xlim(0, max(t * 1.1, 1))
            self.ax.set_ylim(0, max(s * 1.1, 1))
            self.ax.set_title(f"График пути: v₀ = {v0:.1f} м/с, a = {a:.1f} м/с²", fontsize=12)
            self.ax.legend()
        else:
            # Пустой график для t = 0
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.set_title("График не построен (время = 0)", fontsize=12)
        
        self.ax.set_xlabel("Время, с", fontsize=10)
        self.ax.set_ylabel("Путь, м", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Обновление canvas
        self.canvas.draw()
    
    def clear_all(self):
        """Очистка всех данных"""
        self.v0_var.set(0.0)
        self.a_var.set(0.0)
        self.t_var.set(0.0)
        
        # Сброс результатов
        self.type_label.config(text="Тип движения:")
        self.distance_label.config(text="Пройденный путь:")
        self.velocity_label.config(text="Конечная скорость:")
        self.description_label.config(text="Описание движения:")
        self.equation_label.config(text="Уравнение:")
        
        # Сброс графика
        self.init_graph()


def main():
    root = tk.Tk()
    app = MotionAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()