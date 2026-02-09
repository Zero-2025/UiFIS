import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WeibullReliabilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчет надежности по распределению Вейбулла")
        self.root.geometry("1050x700")
        
        # Параметры по умолчанию
        self.alpha_default = 1.5
        self.lambda_default = 1e-4
        self.time_default = 100
        
        self.create_widgets()
        
    def create_widgets(self):
        # Фрейм для ввода параметров
        input_frame = ttk.LabelFrame(self.root, text="Параметры распределения Вейбулла", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Параметр α (форма)
        ttk.Label(input_frame, text="Параметр формы α:").grid(row=0, column=0, sticky="w", pady=5)
        self.alpha_var = tk.StringVar(value=str(self.alpha_default))
        alpha_entry = ttk.Entry(input_frame, textvariable=self.alpha_var, width=15)
        alpha_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # Параметр λ (масштаб)
        ttk.Label(input_frame, text="Параметр масштаба λ (1/час):").grid(row=1, column=0, sticky="w", pady=5)
        self.lambda_var = tk.StringVar(value=str(self.lambda_default))
        lambda_entry = ttk.Entry(input_frame, textvariable=self.lambda_var, width=15)
        lambda_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Время работы
        ttk.Label(input_frame, text="Время работы t (часы):").grid(row=2, column=0, sticky="w", pady=5)
        self.time_var = tk.StringVar(value=str(self.time_default))
        time_entry = ttk.Entry(input_frame, textvariable=self.time_var, width=15)
        time_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Кнопка расчета
        calc_button = ttk.Button(input_frame, text="Рассчитать", command=self.calculate)
        calc_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Фрейм для результатов
        result_frame = ttk.LabelFrame(self.root, text="Результаты расчета", padding=10)
        result_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Текстовое поле для результатов
        self.result_text = tk.Text(result_frame, height=10, width=70)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Фрейм для графиков
        graph_frame = ttk.LabelFrame(self.root, text="Графики функций надежности", padding=10)
        graph_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        # Создание фигуры для графиков
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Холст для графиков
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Настройка сетки
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
    def weibull_sf(self, t, alpha, lam):
        """Функция надежности (survival function) для распределения Вейбулла"""
        return np.exp(-(lam * t) ** alpha)
    
    def weibull_pdf(self, t, alpha, lam):
        """Функция плотности вероятности для распределения Вейбулла"""
        return alpha * lam * (lam * t) ** (alpha - 1) * np.exp(-(lam * t) ** alpha)
    
    def weibull_failure_rate(self, t, alpha, lam):
        """Интенсивность отказов для распределения Вейбулла"""
        return alpha * lam * (lam * t) ** (alpha - 1)
    
    def gamma_function(self, x):
        """Аппроксимация гамма-функции (без использования SciPy)"""
        # Коэффициенты для аппроксимации Ланцоша
        g = 7
        p = [
            0.99999999999980993,
            676.5203681218851,
            -1259.1392167224028,
            771.32342877765313,
            -176.61502916214059,
            12.507343278686905,
            -0.13857109526572012,
            9.9843695780195716e-6,
            1.5056327351493116e-7
        ]
        
        if x < 0.5:
            return math.pi / (math.sin(math.pi * x) * self.gamma_function(1 - x))
        
        x -= 1
        a = p[0]
        for i in range(1, len(p)):
            a += p[i] / (x + i)
        
        t = x + g + 0.5
        return math.sqrt(2 * math.pi) * (t ** (x + 0.5)) * math.exp(-t) * a
    
    def calculate_mean_time(self, alpha, lam):
        """Расчет средней наработки до отказа без SciPy"""
        # MTTF = (1/λ) * Γ(1 + 1/α)
        gamma_arg = 1 + 1/alpha
        gamma_value = self.gamma_function(gamma_arg)
        return (1/lam) * gamma_value
    
    def calculate(self):
        try:
            # Получение параметров
            alpha = float(self.alpha_var.get())
            lam = float(self.lambda_var.get())
            t = float(self.time_var.get())
            
            if alpha <= 0 or lam <= 0 or t < 0:
                messagebox.showerror("Ошибка", "Параметры должны быть положительными числами, время неотрицательным")
                return
            
            # Расчет характеристик надежности
            reliability = self.weibull_sf(t, alpha, lam)
            failure_probability = 1 - reliability
            failure_rate = self.weibull_failure_rate(t, alpha, lam)
            
            # Средняя наработка до отказа (без SciPy)
            mean_time = self.calculate_mean_time(alpha, lam)
            
            # Вывод результатов
            result_str = f"РАСЧЕТ ХАРАКТЕРИСТИК НАДЕЖНОСТИ\n"
            result_str += "=" * 50 + "\n"
            result_str += f"Параметры распределения Вейбулла:\n"
            result_str += f"  α (форма) = {alpha:.4f}\n"
            result_str += f"  λ (масштаб) = {lam:.6f} 1/час\n"
            result_str += f"Время работы: t = {t} часов\n\n"
            result_str += f"Количественные характеристики надежности:\n"
            result_str += f"  • Вероятность безотказной работы P(t) = {reliability:.6f}\n"
            result_str += f"  • Вероятность отказа F(t) = {failure_probability:.6f}\n"
            result_str += f"  • Интенсивность отказов λ(t) = {failure_rate:.8f} 1/час\n"
            result_str += f"  • Средняя наработка до отказа = {mean_time:.2f} часов\n\n"
            
            # Дополнительные характеристики
            # Медиана распределения
            median_time = (math.log(2) ** (1/alpha)) / lam
            result_str += f"Дополнительные характеристики:\n"
            result_str += f"  • Медиана наработки до отказа = {median_time:.2f} часов\n"
            
            # Квантили
            quantile_90 = ((-math.log(0.9)) ** (1/alpha)) / lam
            quantile_10 = ((-math.log(0.1)) ** (1/alpha)) / lam
            result_str += f"  • 90%-ная квантиль (P=0.9) = {quantile_90:.2f} часов\n"
            result_str += f"  • 10%-ная квантиль (P=0.1) = {quantile_10:.2f} часов\n\n"
            
            # Интерпретация
            result_str += f"ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ:\n"
            result_str += "=" * 50 + "\n"
            result_str += f"1. Изделие проработает {t} часов с вероятностью {reliability*100:.2f}%\n"
            result_str += f"2. Вероятность того, что изделие откажет за {t} часов: {failure_probability*100:.2f}%\n"
            
            if alpha > 1:
                result_str += f"3. При α > 1 интенсивность отказов возрастает со временем (износ)\n"
            elif alpha < 1:
                result_str += f"3. При α < 1 интенсивность отказов уменьшается со временем (приработка)\n"
            else:
                result_str += f"3. При α = 1 распределение становится экспоненциальным (постоянная интенсивность)\n"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result_str)
            
            # Построение графиков
            self.plot_graphs(alpha, lam, t)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", "Некорректный ввод. Проверьте введенные значения.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    
    def plot_graphs(self, alpha, lam, t):
        """Построение графиков функций надежности"""
        # Генерация временной оси
        time_max = min(1.5 * t, 5000)  # Ограничиваем максимальное время для графиков
        time_points = np.linspace(0, time_max, 500)
        
        # Очистка предыдущих графиков
        self.ax1.clear()
        self.ax2.clear()
        
        # График 1: Функция надежности и вероятность отказа
        reliability_curve = self.weibull_sf(time_points, alpha, lam)
        failure_curve = 1 - reliability_curve
        
        self.ax1.plot(time_points, reliability_curve, 'b-', label='Вероятность безотказной работы P(t)', linewidth=2)
        self.ax1.plot(time_points, failure_curve, 'r--', label='Вероятность отказа F(t)', linewidth=2)
        
        # Отметка времени t
        self.ax1.axvline(x=t, color='g', linestyle=':', linewidth=1.5, label=f't = {t} час.')
        self.ax1.axhline(y=self.weibull_sf(t, alpha, lam), color='b', linestyle=':', linewidth=1)
        self.ax1.axhline(y=1-self.weibull_sf(t, alpha, lam), color='r', linestyle=':', linewidth=1)
        
        self.ax1.set_xlabel('Время, час')
        self.ax1.set_ylabel('Вероятность')
        self.ax1.set_title('Функции надежности и вероятности отказа')
        self.ax1.legend(loc='best')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_xlim([0, time_max])
        self.ax1.set_ylim([0, 1.05])
        
        # График 2: Интенсивность отказов
        failure_rate_curve = self.weibull_failure_rate(time_points[1:], alpha, lam)  # Исключаем t=0
        
        self.ax2.plot(time_points[1:], failure_rate_curve, 'g-', label='Интенсивность отказов λ(t)', linewidth=2)
        
        # Отметка времени t
        self.ax2.axvline(x=t, color='g', linestyle=':', linewidth=1.5, label=f't = {t} час.')
        self.ax2.axhline(y=self.weibull_failure_rate(t, alpha, lam), color='g', linestyle=':', linewidth=1)
        
        self.ax2.set_xlabel('Время, час')
        self.ax2.set_ylabel('λ(t), 1/час')
        self.ax2.set_title('Интенсивность отказов')
        self.ax2.legend(loc='best')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_xlim([0, time_max])
        
        # Обновление холста
        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = WeibullReliabilityApp(root)
    
    # Устанавливаем минимальный размер окна
    root.minsize(900, 600)
    
    # Центрируем окно
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()