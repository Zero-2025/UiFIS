import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Database
import os

class MainForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Предложения по расширению ИС")
        self.root.geometry("900x500")
        self.db = Database()
        
        # Устанавливаем иконку (если есть)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.setup_ui()
        self.load_proposals()
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Формирование предложений о расширении информационной системы", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Создаем фрейм для таблицы
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Таблица с предложениями
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Подразделение", "Предложение", "Приоритет", "Стоимость"), 
                                show="headings", height=15)
        
        # Настройка колонок
        columns = [
            ("ID", 50, "center"),
            ("Подразделение", 150, "center"),
            ("Предложение", 300, "w"),
            ("Приоритет", 100, "center"),
            ("Стоимость", 150, "center")
        ]
        
        for col, width, anchor in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        # Полосы прокрутки
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение элементов
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Настройка веса строк и колонок
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Фрейм для кнопок
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Создаем кнопки
        buttons = [
            ("Добавить предложение", self.add_proposal),
            ("Просмотр деталей", self.view_details),
            ("Сформировать отчет", self.generate_report),
            ("Выход", self.on_closing)
        ]
        
        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, width=20, height=2, 
                           command=command, bg="#4CAF50", fg="white", 
                           font=("Arial", 10))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Подсказка
        hint_label = tk.Label(self.root, text="Выберите предложение и нажмите 'Просмотр деталей' для получения подробной информации",
                             font=("Arial", 9), fg="gray")
        hint_label.pack(pady=5)
    
    def load_proposals(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загрузка данных из БД
        query = "SELECT id, department, proposal, priority, cost FROM proposal ORDER BY priority DESC, id"
        proposals = self.db.fetch_all(query)
        
        # Цвета для приоритетов
        priority_colors = {
            "Высокий": "#FF6B6B",
            "Средний": "#FFD166",
            "Низкий": "#06D6A0"
        }
        
        for proposal in proposals:
            item = self.tree.insert("", "end", values=proposal)
            # Устанавливаем цвет строки в зависимости от приоритета
            if proposal[3] in priority_colors:
                self.tree.tag_configure(proposal[3], background=priority_colors[proposal[3]])
                self.tree.item(item, tags=(proposal[3],))
    
    def add_proposal(self):
        AddProposalForm(self.root, self)
    
    def view_details(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите предложение для просмотра деталей")
            return
        
        item = self.tree.item(selected_item[0])
        proposal_id = item['values'][0]
        DetailsForm(self.root, proposal_id, self.db)
    
    def generate_report(self):
        ReportForm(self.root, self.db)
    
    def on_closing(self):
        if self.db:
            self.db.close()
        self.root.destroy()


class AddProposalForm:
    def __init__(self, parent, main_form):
        self.parent = parent
        self.main_form = main_form
        self.db = main_form.db
        
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление нового предложения")
        self.window.geometry("500x450")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Заголовок
        tk.Label(self.window, text="Добавление нового предложения", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Основной фрейм для полей ввода
        main_frame = tk.Frame(self.window)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Словарь для хранения виджетов
        self.entries = {}
        
        # Поля ввода
        fields = [
            ("Подразделение:", "department", tk.Entry, 30),
            ("Предложение:", "proposal", tk.Entry, 30),
            ("Приоритет:", "priority", ttk.Combobox, 20),
            ("Стоимость (₽):", "cost", tk.Entry, 30),
            ("Срок реализации:", "date", tk.Entry, 30),
        ]
        
        row = 0
        for label_text, key, widget_type, width in fields:
            tk.Label(main_frame, text=label_text, anchor="w").grid(row=row, column=0, sticky="w", pady=5)
            
            if widget_type == ttk.Combobox:
                entry = ttk.Combobox(main_frame, width=width)
                entry['values'] = ('Высокий', 'Средний', 'Низкий')
                entry.current(0)
            else:
                entry = tk.Entry(main_frame, width=width)
            
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            self.entries[key] = entry
            row += 1
        
        # Поле для обоснования
        tk.Label(main_frame, text="Обоснование:", anchor="w").grid(row=row, column=0, sticky="nw", pady=5)
        self.justification_text = tk.Text(main_frame, width=40, height=6)
        self.justification_text.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        row += 1
        
        # Установка текущей даты по умолчанию
        self.entries['date'].insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        # Кнопки
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Сохранить", width=15, bg="#4CAF50", fg="white",
                 command=self.save_proposal).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", width=15, bg="#f44336", fg="white",
                 command=self.window.destroy).pack(side=tk.LEFT, padx=10)
    
    def save_proposal(self):
        try:
            # Получение данных
            department = self.entries['department'].get().strip()
            proposal_text = self.entries['proposal'].get().strip()
            priority = self.entries['priority'].get()
            cost = self.entries['cost'].get().strip()
            date_str = self.entries['date'].get().strip()
            justification = self.justification_text.get("1.0", tk.END).strip()
            
            # Валидация
            if not department or not proposal_text or not cost:
                messagebox.showwarning("Ошибка", "Заполните все обязательные поля!")
                return
            
            try:
                cost_value = float(cost)
                if cost_value <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Ошибка", "Введите корректную стоимость!")
                return
            
            # Преобразование даты
            try:
                if date_str:
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
                    date_for_db = date_obj.strftime("%Y-%m-%d")
                else:
                    date_for_db = None
            except ValueError:
                messagebox.showwarning("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
                return
            
            # Сохранение в БД
            query = """INSERT INTO proposal (department, proposal, priority, cost, 
                      justification, implementation_date) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            
            params = (department, proposal_text, priority, cost_value, 
                     justification, date_for_db)
            
            if self.db.execute_query(query, params):
                messagebox.showinfo("Успех", "Предложение успешно добавлено!")
                self.window.destroy()
                self.main_form.load_proposals()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")


class DetailsForm:
    def __init__(self, parent, proposal_id, db):
        self.parent = parent
        self.proposal_id = proposal_id
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Детали предложения #{proposal_id}")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.load_details()
    
    def load_details(self):
        query = """SELECT id, department, proposal, priority, cost, 
                          justification, implementation_date 
                   FROM proposal WHERE id = %s"""
        
        result = self.db.fetch_all(query, (self.proposal_id,))
        
        if not result:
            messagebox.showerror("Ошибка", "Предложение не найдено")
            self.window.destroy()
            return
        
        data = result[0]
        
        # Основной фрейм
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Заголовок
        tk.Label(main_frame, text="ПОДРОБНАЯ ИНФОРМАЦИЯ О ПРЕДЛОЖЕНИИ", 
                font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Информация в виде таблицы
        details = [
            ("ID:", data[0]),
            ("Подразделение:", data[1]),
            ("Предложение:", data[2]),
            ("Приоритет:", data[3]),
            ("Стоимость:", f"{float(data[4]):,.2f} ₽"),
            ("Срок реализации:", data[6].strftime("%d.%m.%Y") if data[6] else "Не указан")
        ]
        
        for i, (label, value) in enumerate(details):
            frame = tk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=2)
            
            tk.Label(frame, text=label, width=20, anchor="w", 
                    font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            tk.Label(frame, text=value, anchor="w").pack(side=tk.LEFT)
        
        # Обоснование
        tk.Label(main_frame, text="\nОБОСНОВАНИЕ:", 
                font=("Arial", 10, "bold")).pack(pady=(10, 5), anchor="w")
        
        justification_frame = tk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        justification_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        justification_text = tk.Text(justification_frame, wrap=tk.WORD, height=8)
        justification_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Вставляем текст обоснования
        justification = data[5] if data[5] else "Обоснование не предоставлено"
        justification_text.insert("1.0", justification)
        justification_text.config(state="disabled")
        
        # Кнопка закрытия
        tk.Button(self.window, text="Закрыть", width=15, 
                 command=self.window.destroy, bg="#2196F3", fg="white").pack(pady=10)


class ReportForm:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("Отчет по предложениям")
        self.window.geometry("700x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.generate_report()
    
    def generate_report(self):
        # Получение статистики
        total_query = "SELECT COUNT(*) FROM proposal"
        high_priority_query = "SELECT COUNT(*) FROM proposal WHERE priority = 'Высокий'"
        cost_query = "SELECT SUM(cost) FROM proposal"
        
        total = self.db.fetch_all(total_query)[0][0]
        high_priority = self.db.fetch_all(high_priority_query)[0][0]
        total_cost = self.db.fetch_all(cost_query)[0][0] or 0
        
        # Получение всех предложений
        proposals_query = """SELECT id, department, proposal, priority, cost, 
                                    justification, implementation_date 
                             FROM proposal 
                             ORDER BY FIELD(priority, 'Высокий', 'Средний', 'Низкий') DESC, id"""
        proposals = self.db.fetch_all(proposals_query)
        
        # Создание текста отчета
        report_text = f"""ОТЧЕТ ПО ПРЕДЛОЖЕНИЯМ О РАСШИРЕНИИ ИС
Дата формирования: {datetime.now().strftime("%d.%m.%Y %H:%M")}
Всего предложений: {total}
Высокоприоритетных: {high_priority}
Общая стоимость: {total_cost:,.2f} ₽

{"="*70}

СПИСОК ПРЕДЛОЖЕНИЙ:

"""
        
        for prop in proposals:
            date_str = prop[6].strftime("%d.%m.%Y") if prop[6] else "Не указан"
            report_text += f"""[ID: {prop[0]}] {prop[1]}
Предложение: {prop[2]}
Приоритет: {prop[3]} | Стоимость: {float(prop[4]):,.2f} ₽
Срок: {date_str}
Обоснование: {prop[5] if prop[5] else 'Не указано'}

{"-"*70}

"""
        
        self.report_text = report_text  # Сохраняем текст для печати
        
        # Фрейм для текста отчета
        text_frame = tk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Виджет Text для отображения отчета
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Вставляем текст отчета
        text_widget.insert("1.0", report_text)
        text_widget.config(state="disabled")
        
        # Фрейм для кнопок
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        
        # Кнопка печати (открывает системный диалог печати)
        tk.Button(button_frame, text="Печать", width=15, bg="#2196F3", fg="white",
                 command=self.open_print_dialog, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # Кнопка сохранения в файл
        tk.Button(button_frame, text="Сохранить в файл", width=15, bg="#4CAF50", fg="white",
                 command=self.save_to_file, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # Кнопка закрытия
        tk.Button(button_frame, text="Закрыть", width=15, bg="#f44336", fg="white",
                 command=self.window.destroy, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def save_to_file(self):
        """Сохранить отчет в текстовый файл"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                initialfile=f"отчет_предложения_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.report_text)
                messagebox.showinfo("Успех", f"Отчет успешно сохранен в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def open_print_dialog(self):
        """Открыть системный диалог печати"""
        try:
            import tempfile
            import webbrowser
            import os
            import platform
            
            # Создаем HTML файл для печати
            html_content = self.create_html_for_printing()
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                           encoding='utf-8', delete=False) as f:
                f.write(html_content)
                temp_file = f.name
            
            # Открываем в браузере для печати
            try:
                # Пытаемся открыть системный диалог печати напрямую
                if platform.system() == "Windows":
                    os.startfile(temp_file, "print")
                    messagebox.showinfo("Печать", "Документ отправлен на печать через системный диалог.")
                else:
                    # Для других ОС открываем в браузере
                    webbrowser.open(f'file://{temp_file}')
                    
                    # Показываем инструкцию
                    messagebox.showinfo("Печать", 
                        "Отчет открыт в браузере.\n"
                        "Нажмите Ctrl+P или выберите 'Печать' в меню браузера для печати.")
            
            except Exception as e:
                # Fallback: открываем в браузере
                webbrowser.open(f'file://{temp_file}')
                messagebox.showinfo("Печать", 
                    "Отчет открыт в браузере.\n"
                    "Нажмите Ctrl+P или выберите 'Печать' в меню браузера.")
            
            # Удаляем временный файл через некоторое время
            import threading
            import time
            
            def delete_temp_file(file_path):
                time.sleep(10)  # Ждем 10 секунд
                try:
                    os.unlink(file_path)
                except:
                    pass
            
            threading.Thread(target=delete_temp_file, args=(temp_file,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть диалог печати: {str(e)}")
    
    def create_html_for_printing(self):
        """Создать HTML контент для печати"""
        proposals_query = """SELECT id, department, proposal, priority, cost, 
                                    justification, implementation_date 
                             FROM proposal 
                             ORDER BY FIELD(priority, 'Высокий', 'Средний', 'Низкий') DESC, id"""
        proposals = self.db.fetch_all(proposals_query)
        
        # Генерируем HTML таблицу с предложениями
        proposals_html = ""
        for prop in proposals:
            date_str = prop[6].strftime("%d.%m.%Y") if prop[6] else "Не указан"
            
            # Цвет для приоритета
            priority_color = {
                "Высокий": "#FF6B6B",
                "Средний": "#FFD166",
                "Низкий": "#06D6A0"
            }.get(prop[3], "#000000")
            
            proposals_html += f"""
            <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; page-break-inside: avoid;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-weight: bold; color: #2c3e50;">[ID: {prop[0]}] {prop[1]}</span>
                    <span style="font-weight: bold; color: {priority_color};">{prop[3]}</span>
                </div>
                <div style="margin-bottom: 5px;">
                    <strong>Предложение:</strong> {prop[2]}
                </div>
                <div style="margin-bottom: 5px;">
                    <strong>Стоимость:</strong> <span style="color: #2980b9; font-weight: bold;">{float(prop[4]):,.2f} ₽</span> | 
                    <strong>Срок:</strong> {date_str}
                </div>
                <div style="margin-top: 10px; padding: 5px; background-color: #f8f9fa; border-radius: 3px;">
                    <strong>Обоснование:</strong><br>
                    {prop[5] if prop[5] else 'Не указано'}
                </div>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Отчет по предложениям</title>
            <style>
                @media print {{
                    body {{
                        font-family: "Arial", sans-serif;
                        margin: 20px;
                        font-size: 12pt;
                    }}
                    .no-print {{
                        display: none;
                    }}
                    .page-break {{
                        page-break-after: always;
                    }}
                }}
                @media screen {{
                    body {{
                        font-family: "Arial", sans-serif;
                        margin: 40px;
                        max-width: 800px;
                        margin: 0 auto;
                    }}
                }}
                h1 {{
                    text-align: center;
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                .header-info {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .stats {{
                    display: flex;
                    justify-content: space-between;
                    margin: 20px 0;
                }}
                .stat-item {{
                    text-align: center;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    flex: 1;
                    margin: 0 5px;
                }}
                .stat-value {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #3498db;
                }}
                .print-button {{
                    text-align: center;
                    margin: 20px 0;
                }}
                button {{
                    background-color: #2196F3;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }}
                button:hover {{
                    background-color: #1976D2;
                }}
            </style>
            <script>
                function printReport() {{
                    window.print();
                }}
                
                // Автоматически вызываем печать при загрузке страницы
                window.onload = function() {{
                    // Можно раскомментировать для автоматического открытия диалога печати
                    // setTimeout(function() {{ window.print(); }}, 1000);
                }};
            </script>
        </head>
        <body>
            <h1>ОТЧЕТ ПО ПРЕДЛОЖЕНИЯМ О РАСШИРЕНИИ ИС</h1>
            
            <div class="header-info">
                <p><strong>Дата формирования:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</p>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div>Всего предложений</div>
                    <div class="stat-value">{self.get_statistic("total")}</div>
                </div>
                <div class="stat-item">
                    <div>Высокий приоритет</div>
                    <div class="stat-value">{self.get_statistic("high_priority")}</div>
                </div>
                <div class="stat-item">
                    <div>Общая стоимость</div>
                    <div class="stat-value">{self.get_statistic("total_cost"):,.2f} ₽</div>
                </div>
            </div>
            
            <h2>СПИСОК ПРЕДЛОЖЕНИЙ</h2>
            
            {proposals_html}
            
            <div class="print-button no-print">
                <button onclick="printReport()">
                    📄 Печать отчета
                </button>
                <p style="color: #666; font-size: 12px; margin-top: 10px;">
                    Нажмите кнопку выше или используйте Ctrl+P для печати
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #777;">
                <p>Сформировано автоматически системой управления предложениями</p>
                <p>Дата: {datetime.now().strftime("%d.%m.%Y")}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_statistic(self, stat_type):
        """Получить статистику для отчета"""
        if stat_type == "total":
            return self.db.fetch_all("SELECT COUNT(*) FROM proposal")[0][0]
        elif stat_type == "high_priority":
            return self.db.fetch_all("SELECT COUNT(*) FROM proposal WHERE priority = 'Высокий'")[0][0]
        elif stat_type == "total_cost":
            cost = self.db.fetch_all("SELECT SUM(cost) FROM proposal")[0][0]
            return float(cost) if cost else 0.0
        return 0

def main():
    try:
        root = tk.Tk()
        app = MainForm(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Не удалось запустить приложение: {str(e)}")


if __name__ == "__main__":
    main()