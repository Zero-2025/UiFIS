import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox, font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class ReliabilityAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ надежности систем")
        self.root.geometry("1200x800")
        
        # Подключение к базе данных
        self.db_connection = self.connect_to_database()
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Создаем фреймы для каждой вкладки
        self.frame_task1 = ttk.Frame(self.notebook)
        self.frame_task2 = ttk.Frame(self.notebook)
        self.frame_task3 = ttk.Frame(self.notebook)
        
        self.notebook.add(self.frame_task1, text='Задание 1: Расчет MTBF')
        self.notebook.add(self.frame_task2, text='Задание 2: Наработка на отказ')
        self.notebook.add(self.frame_task3, text='Задание 3: Коэффициент готовности')
        
        # Инициализируем интерфейсы для каждого задания
        self.init_task1_ui()
        self.init_task2_ui()
        self.init_task3_ui()
        
        # Загружаем данные из БД
        self.load_all_data()
    
    def connect_to_database(self):
        """Подключение к базе данных MySQL"""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='system_reliability'
            )
            if connection.is_connected():
                print("Успешное подключение к базе данных")
                return connection
        except Error as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к БД: {e}")
            return None
    
    def load_all_data(self):
        """Загрузка всех данных из БД"""
        self.load_task1_data()
        self.load_task2_data()
        self.load_task3_data()
    
    # ========== ЗАДАНИЕ 1 ==========
    def init_task1_ui(self):
        # Основной контейнер
        main_frame = tk.Frame(self.frame_task1, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = tk.Label(main_frame, 
                              text="Расчет средней наработки на отказ системы", 
                              font=('Arial', 16, 'bold'),
                              bg='white')
        title_label.pack(pady=10)
        
        # Описание
        desc_text = """Исходные данные:
Система отказала 6 раз.
Время работы до отказов:
• 1-й отказ: 185 часов
• 2-й отказ: 342 часа
• 3-й отказ: 268 часов
• 4-й отказ: 220 часов
• 5-й отказ: 96 часов
• 6-й отказ: 102 часов"""
        
        desc_label = tk.Label(main_frame, text=desc_text, justify=tk.LEFT,
                             font=('Arial', 11), bg='white')
        desc_label.pack(pady=10)
        
        # Разделитель
        separator = tk.Frame(main_frame, height=2, bg='black')
        separator.pack(fill='x', pady=10)
        
        # Фрейм для данных и графика
        content_frame = tk.Frame(main_frame, bg='white')
        content_frame.pack(fill='both', expand=True)
        
        # Левый фрейм - данные и расчет
        left_frame = tk.Frame(content_frame, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Подзаголовок
        sub_title = tk.Label(left_frame, text="РАССЧИТАТЬ MTBF", 
                            font=('Arial', 14, 'bold'), bg='white')
        sub_title.pack(pady=10)
        
        # Результаты расчета
        results_frame = tk.Frame(left_frame, bg='lightgray', bd=2, relief='groove')
        results_frame.pack(pady=10, padx=10, fill='x')
        
        results_text = """РЕЗУЛЬТАТ РАСЧЕТА

1. Сумма времени работы:
   Σt = 185 + 342 + 268 + 220 + 96 + 102
   Σt = 1233 часов

2. Количество отказов:
   n = 6

3. Формула расчета:
   MTBF = Σt / n
   
   MTBF = 1233 / 6 = 205.5 часов"""
        
        result_label = tk.Label(results_frame, text=results_text, 
                               justify=tk.LEFT, font=('Arial', 11), 
                               bg='lightgray')
        result_label.pack(pady=10, padx=10)
        
        # Кнопка расчета
        calc_button = tk.Button(left_frame, text="ВЫЧИСЛИТЬ MTBF",
                               font=('Arial', 12, 'bold'),
                               bg='lightblue',
                               command=self.calculate_task1,
                               width=20)
        calc_button.pack(pady=20)
        
        # Правая часть - график
        right_frame = tk.Frame(content_frame, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        graph_title = tk.Label(right_frame, text="График времени до отказа",
                              font=('Arial', 14, 'bold'), bg='white')
        graph_title.pack(pady=10)
        
        # Создаем график
        self.create_task1_graph(right_frame)
        
        # Таблица данных
        self.create_task1_table(left_frame)
    
    def create_task1_table(self, parent):
        """Создание таблицы для задания 1"""
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(pady=20)
        
        columns = ['Отказ №', 'Время до отказа, час']
        
        # Заголовки таблицы
        for i, col in enumerate(columns):
            header = tk.Label(table_frame, text=col, font=('Arial', 11, 'bold'),
                             bg='gray', fg='white', width=15, padx=10, pady=5)
            header.grid(row=0, column=i, padx=1, pady=1)
        
        # Данные таблицы
        data = [
            (1, 185),
            (2, 342),
            (3, 268),
            (4, 220),
            (5, 96),
            (6, 102)
        ]
        
        for i, (failure_num, time) in enumerate(data, 1):
            # Номер отказа
            num_label = tk.Label(table_frame, text=str(failure_num),
                                bg='lightgray', width=15, padx=10, pady=5)
            num_label.grid(row=i, column=0, padx=1, pady=1)
            
            # Время
            time_label = tk.Label(table_frame, text=str(time),
                                 bg='lightgray', width=15, padx=10, pady=5)
            time_label.grid(row=i, column=1, padx=1, pady=1)
    
    def create_task1_graph(self, parent):
        """Создание графика для задания 1"""
        fig = Figure(figsize=(6, 4), dpi=80)
        ax = fig.add_subplot(111)
        
        # Данные для графика
        failures = [1, 2, 3, 4, 5, 6]
        times = [185, 342, 268, 220, 96, 102]
        mtbf_value = 205.5  # Среднее значение
        
        # Строим столбчатую диаграмму
        bars = ax.bar(failures, times, color='skyblue', alpha=0.7)
        
        # Линия среднего значения
        ax.axhline(y=mtbf_value, color='red', linestyle='--', linewidth=2, 
                  label=f'MTBF = {mtbf_value:.1f} час')
        
        # Настройка графика
        ax.set_xlabel('Номер отказа', fontsize=12)
        ax.set_ylabel('Время до отказа, час', fontsize=12)
        ax.set_title('Время работы системы до отказа', fontsize=14, fontweight='bold')
        ax.set_xticks(failures)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Добавляем значения на столбцы
        for bar, time in zip(bars, times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{time}', ha='center', va='bottom', fontweight='bold')
        
        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def load_task1_data(self):
        """Загрузка данных для задания 1"""
        # В этом интерфейсе данные жестко заданы
        pass
    
    def calculate_task1(self):
        """Расчет MTBF для задания 1"""
        times = [185, 342, 268, 220, 96, 102]
        total_time = sum(times)
        failures = len(times)
        mtbf = total_time / failures
        
        messagebox.showinfo("Результат расчета", 
                           f"MTBF = {total_time} / {failures} = {mtbf:.1f} часов")
    
    # ========== ЗАДАНИЕ 2 ==========
    def init_task2_ui(self):
        # Основной контейнер
        main_frame = tk.Frame(self.frame_task2, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = tk.Label(main_frame, 
                              text="Наработка на отказ по данным наблюдения", 
                              font=('Arial', 16, 'bold'),
                              bg='white')
        title_label.pack(pady=10)
        
        # Создаем таблицу с данными
        self.create_task2_table(main_frame)
        
        # Разделитель
        separator = tk.Frame(main_frame, height=2, bg='black')
        separator.pack(fill='x', pady=20)
        
        # Фрейм для расчета
        calc_frame = tk.Frame(main_frame, bg='white')
        calc_frame.pack(fill='both', expand=True)
        
        # Левая часть - расчет
        left_calc_frame = tk.Frame(calc_frame, bg='white')
        left_calc_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Подзаголовок
        sub_title = tk.Label(left_calc_frame, text="РАСЧЕТ НАРАБОТКИ НА ОТКАЗ", 
                            font=('Arial', 14, 'bold'), bg='white')
        sub_title.pack(pady=10)
        
        # Результаты расчета
        results_text = """1. ДАННЫЕ ПО СИСТЕМАМ:

   Система 1: t₁ = 358 час, n₁ = 4
   Система 2: t₂ = 385 час, n₂ = 3
   Система 3: t₃ = 400 час, n₃ = 2

2. ИНДИВИДУАЛЬНЫЕ РАСЧЕТЫ:

   MTBF₁ = t₁ / n₁ = 358 / 4 = 89.50 час
   MTBF₂ = t₂ / n₂ = 385 / 3 = 128.33 час
   MTBF₃ = t₃ / n₃ = 400 / 2 = 200.00 час

3. ОБЩИЙ РАСЧЕТ:

   Общее время: Σt = 358 + 385 + 400 = 1143 час
   Общее число отказов: Σn = 4 + 3 + 2 = 9
   
   Общий MTBF = Σt / Σn = 1143 / 9 = 127.00 час"""
        
        results_frame = tk.Frame(left_calc_frame, bg='lightgray', bd=2, relief='groove')
        results_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        result_label = tk.Label(results_frame, text=results_text, 
                               justify=tk.LEFT, font=('Courier', 10), 
                               bg='lightgray')
        result_label.pack(pady=10, padx=10)
        
        # Кнопка расчета
        calc_button = tk.Button(left_calc_frame, text="РАССЧИТАТЬ ОБЩИЙ MTBF",
                               font=('Arial', 12, 'bold'),
                               bg='lightgreen',
                               command=self.calculate_task2,
                               width=25)
        calc_button.pack(pady=20)
        
        # Правая часть - график
        right_calc_frame = tk.Frame(calc_frame, bg='white')
        right_calc_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        self.create_task2_graph(right_calc_frame)
    
    def create_task2_table(self, parent):
        """Создание таблицы для задания 2"""
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(pady=10)
        
        # Заголовок таблицы
        table_title = tk.Label(table_frame, text="Исходные данные:", 
                              font=('Arial', 12, 'bold'), bg='white')
        table_title.grid(row=0, column=0, columnspan=5, pady=10)
        
        # Заголовки колонок
        headers = ['Система', 'Время работы, час', 'Количество отказов', 'MTBF системы, час']
        
        for i, header in enumerate(headers):
            header_label = tk.Label(table_frame, text=header, 
                                   font=('Arial', 11, 'bold'),
                                   bg='gray', fg='white',
                                   width=20, padx=10, pady=5)
            header_label.grid(row=1, column=i, padx=1, pady=1)
        
        # Данные таблицы
        data = [
            ('Система 1', 358, 4, 89.50),
            ('Система 2', 385, 3, 128.33),
            ('Система 3', 400, 2, 200.00)
        ]
        
        for i, (system, time, failures, mtbf) in enumerate(data, 2):
            # Система
            sys_label = tk.Label(table_frame, text=system,
                                bg='lightgray', width=20, padx=10, pady=5)
            sys_label.grid(row=i, column=0, padx=1, pady=1)
            
            # Время работы
            time_label = tk.Label(table_frame, text=str(time),
                                 bg='lightgray', width=20, padx=10, pady=5)
            time_label.grid(row=i, column=1, padx=1, pady=1)
            
            # Отказы
            fail_label = tk.Label(table_frame, text=str(failures),
                                 bg='lightgray', width=20, padx=10, pady=5)
            fail_label.grid(row=i, column=2, padx=1, pady=1)
            
            # MTBF
            mtbf_label = tk.Label(table_frame, text=f"{mtbf:.2f}",
                                 bg='lightgray', width=20, padx=10, pady=5)
            mtbf_label.grid(row=i, column=3, padx=1, pady=1)
    
    def create_task2_graph(self, parent):
        """Создание графика для задания 2"""
        fig = Figure(figsize=(6, 5), dpi=80)
        ax = fig.add_subplot(111)
        
        # Данные для графика
        systems = ['Система 1', 'Система 2', 'Система 3', 'Общий']
        mtbf_values = [89.50, 128.33, 200.00, 127.00]
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'gold']
        
        # Строим столбчатую диаграмму
        bars = ax.bar(systems, mtbf_values, color=colors, alpha=0.7)
        
        # Настройка графика
        ax.set_xlabel('Системы', fontsize=12)
        ax.set_ylabel('MTBF, час', fontsize=12)
        ax.set_title('Сравнение MTBF систем', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Добавляем значения на столбцы
        for bar, value in zip(bars, mtbf_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}', ha='center', va='bottom', 
                   fontweight='bold', fontsize=10)
        
        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def load_task2_data(self):
        """Загрузка данных для задания 2"""
        pass
    
    def calculate_task2(self):
        """Расчет общего MTBF для задания 2"""
        total_time = 358 + 385 + 400
        total_failures = 4 + 3 + 2
        overall_mtbf = total_time / total_failures
        
        messagebox.showinfo("Результат расчета", 
                           f"Общий MTBF = {total_time} / {total_failures} = {overall_mtbf:.2f} часов")
    
    # ========== ЗАДАНИЕ 3 ==========
    def init_task3_ui(self):
        # Основной контейнер
        main_frame = tk.Frame(self.frame_task3, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = tk.Label(main_frame, 
                              text="Анализ безотказности и восстанавливаемости", 
                              font=('Arial', 16, 'bold'),
                              bg='white')
        title_label.pack(pady=10)
        
        # Разделитель
        separator = tk.Frame(main_frame, height=2, bg='black')
        separator.pack(fill='x', pady=10)
        
        # Создаем таблицу с данными
        self.create_task3_table(main_frame)
        
        # Разделитель
        separator2 = tk.Frame(main_frame, height=2, bg='black')
        separator2.pack(fill='x', pady=20)
        
        # Фрейм для расчета
        calc_frame = tk.Frame(main_frame, bg='white')
        calc_frame.pack(fill='both', expand=True)
        
        # Левая часть - расчет
        left_calc_frame = tk.Frame(calc_frame, bg='white')
        left_calc_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Подзаголовок
        sub_title = tk.Label(left_calc_frame, text="Сравнительный анализ двух систем", 
                            font=('Arial', 14, 'bold'), bg='white')
        sub_title.pack(pady=10)
        
        # Результаты расчета
        results_text = """ИСХОДНЫЕ ДАННЫЕ:

• Система 1: t₀ = 24 час, tᵥ = 16 час
• Система 2: t₀ = 400 час, tᵥ = 32 час

РАСЧЕТ ПОКАЗАТЕЛЕЙ НАДЕЖНОСТИ:

СИСТЕМА 1:
• MTBF (средняя наработка на отказ) = 24 час
• MTTR (среднее время восстановления) = 16 час
• Коэффициент готовности:
  Kг = t₀ / (t₀ + tᵥ) = 24 / (24 + 16)
  Kг = 0.6000

СИСТЕМА 2:
• MTBF (средняя наработка на отказ) = 400 час
• MTTR (среднее время восстановления) = 32 час
• Коэффициент готовности:
  Kг = t₀ / (t₀ + tᵥ) = 400 / (400 + 32)
  Kг = 0.9259

ВЫВОД: Система 2 более надежна (Kг₂ > Kг₁)"""
        
        results_frame = tk.Frame(left_calc_frame, bg='lightgray', bd=2, relief='groove')
        results_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        result_label = tk.Label(results_frame, text=results_text, 
                               justify=tk.LEFT, font=('Courier', 10), 
                               bg='lightgray')
        result_label.pack(pady=10, padx=10)
        
        # Кнопка расчета
        calc_button = tk.Button(left_calc_frame, text="РАССЧИТАТЬ КОЭФФИЦИЕНТЫ",
                               font=('Arial', 12, 'bold'),
                               bg='lightcoral',
                               command=self.calculate_task3,
                               width=25)
        calc_button.pack(pady=20)
        
        # Правая часть - график
        right_calc_frame = tk.Frame(calc_frame, bg='white')
        right_calc_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        self.create_task3_graph(right_calc_frame)
    
    def create_task3_table(self, parent):
        """Создание таблицы для задания 3"""
        # Контейнер для таблицы с прокруткой
        table_container = tk.Frame(parent, bg='white')
        table_container.pack(pady=10)
        
        # Заголовок таблицы
        table_title = tk.Label(table_container, text="Экспериментальные данные по системам", 
                              font=('Arial', 12, 'bold'), bg='white')
        table_title.grid(row=0, column=0, columnspan=5, pady=10)
        
        # Заголовки колонок
        headers = ['Вариант', 'Система 1: t₀', 'Система 1: tᵥ', 
                  'Система 2: t₀', 'Система 2: tᵥ']
        
        for i, header in enumerate(headers):
            header_label = tk.Label(table_container, text=header, 
                                   font=('Arial', 10, 'bold'),
                                   bg='gray', fg='white',
                                   width=15, padx=8, pady=5)
            header_label.grid(row=1, column=i, padx=1, pady=1)
        
        # Данные таблицы (сокращенный набор для отображения)
        data = [
            (1, 24, 16, 400, 32),
            (2, 84, 24, 184, 32),
            (3, 225, 8, 64, 24),
            (4, 20, 6, 16, 8),
            (5, 58, 2, 16, 8),
            (6, 516, 19, 160, 8),
            (7, 287, 16, 8, 4),
            (8, 464, 64, 8, 16),
            (9, 96, 12, 48, 8),
            (10, 4, 3, 104, 8),
            (11, 37, 3, 272, 8),
            (12, 101, 3, 336, 8),
            (13, 29, 4, 370, 8),
            (14, 12, 5, 384, 7),
            (15, 3, 24, 56, 8),
            (16, 304, 16, 4, 8)
        ]
        
        for i, (variant, sys1_t0, sys1_tv, sys2_t0, sys2_tv) in enumerate(data, 2):
            # Вариант
            var_label = tk.Label(table_container, text=str(variant),
                                bg='lightgray', width=15, padx=8, pady=5)
            var_label.grid(row=i, column=0, padx=1, pady=1)
            
            # Система 1: t₀
            sys1_t0_label = tk.Label(table_container, text=str(sys1_t0),
                                    bg='lightblue', width=15, padx=8, pady=5)
            sys1_t0_label.grid(row=i, column=1, padx=1, pady=1)
            
            # Система 1: tᵥ
            sys1_tv_label = tk.Label(table_container, text=str(sys1_tv),
                                    bg='lightblue', width=15, padx=8, pady=5)
            sys1_tv_label.grid(row=i, column=2, padx=1, pady=1)
            
            # Система 2: t₀
            sys2_t0_label = tk.Label(table_container, text=str(sys2_t0),
                                    bg='lightgreen', width=15, padx=8, pady=5)
            sys2_t0_label.grid(row=i, column=3, padx=1, pady=1)
            
            # Система 2: tᵥ
            sys2_tv_label = tk.Label(table_container, text=str(sys2_tv),
                                    bg='lightgreen', width=15, padx=8, pady=5)
            sys2_tv_label.grid(row=i, column=4, padx=1, pady=1)
    
    def create_task3_graph(self, parent):
        """Создание графика для задания 3"""
        fig = Figure(figsize=(6, 5), dpi=80)
        ax = fig.add_subplot(111)
        
        # Данные для графика
        systems = ['Система 1', 'Система 2']
        availability = [0.6000, 0.9259]  # Коэффициенты готовности
        colors = ['lightblue', 'lightgreen']
        
        # Строим столбчатую диаграмму
        bars = ax.bar(systems, availability, color=colors, alpha=0.7)
        
        # Настройка графика
        ax.set_xlabel('Системы', fontsize=12)
        ax.set_ylabel('Коэффициент готовности (Kг)', fontsize=12)
        ax.set_title('Сравнение коэффициентов готовности', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.0)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Линия идеального значения
        ax.axhline(y=1.0, color='red', linestyle=':', linewidth=1, alpha=0.5)
        
        # Добавляем значения на столбцы
        for bar, value in zip(bars, availability):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.4f}', ha='center', va='bottom', 
                   fontweight='bold', fontsize=11)
            
            # Процентное значение
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                   f'{value*100:.1f}%', ha='center', va='center', 
                   fontweight='bold', fontsize=12, color='darkblue')
        
        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def load_task3_data(self):
        """Загрузка данных для задания 3"""
        pass
    
    def calculate_task3(self):
        """Расчет коэффициента готовности для задания 3"""
        # Для простоты берем первые значения из таблицы
        sys1_t0 = 24
        sys1_tv = 16
        sys2_t0 = 400
        sys2_tv = 32
        
        kg1 = sys1_t0 / (sys1_t0 + sys1_tv)
        kg2 = sys2_t0 / (sys2_t0 + sys2_tv)
        
        result = f"СИСТЕМА 1:\n"
        result += f"Kг = {sys1_t0} / ({sys1_t0} + {sys1_tv}) = {kg1:.4f}\n\n"
        result += f"СИСТЕМА 2:\n"
        result += f"Kг = {sys2_t0} / ({sys2_t0} + {sys2_tv}) = {kg2:.4f}\n\n"
        
        if kg1 > kg2:
            result += f"ВЫВОД: Система 1 более надежна"
        elif kg2 > kg1:
            result += f"ВЫВОД: Система 2 более надежна"
        else:
            result += f"ВЫВОД: Системы равны по надежности"
        
        messagebox.showinfo("Результат расчета коэффициентов готовности", result)

def main():
    root = tk.Tk()
    app = ReliabilityAnalysisApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()