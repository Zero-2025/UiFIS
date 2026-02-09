import tkinter as tk
from tkinter import ttk, messagebox

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер валют")
        self.root.geometry("400x550")
        
        # Курсы валют к RUB (можно обновлять)
        self.rates = {
            "RUB": 1.0,
            "USD": 77.70,
            "EUR": 90.34,
            "CNY": 10.96,
            "KRW": 0.0670
        }
        
        # Названия валют для отображения
        self.currency_names = {
            "RUB": "Российский рубль",
            "USD": "Доллар США",
            "EUR": "Евро",
            "CNY": "Китайский юань",
            "KRW": "Южнокорейская вона"
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Конвертер валют", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Исходная валюта
        from_frame = tk.Frame(self.root)
        from_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(from_frame, text="Из:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.from_currency = tk.StringVar()
        self.from_combo = ttk.Combobox(from_frame, textvariable=self.from_currency, 
                                     values=list(self.currency_names.values()),
                                     state="readonly", width=25)
        self.from_combo.pack(side="left", padx=5)
        self.from_combo.set("Российский рубль")
        
        # Целевая валюта
        to_frame = tk.Frame(self.root)
        to_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(to_frame, text="В:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.to_currency = tk.StringVar()
        self.to_combo = ttk.Combobox(to_frame, textvariable=self.to_currency,
                                    values=list(self.currency_names.values()),
                                    state="readonly", width=25)
        self.to_combo.pack(side="left", padx=5)
        self.to_combo.set("Доллар США")
        
        # Сумма
        amount_frame = tk.Frame(self.root)
        amount_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(amount_frame, text="Сумма:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(amount_frame, textvariable=self.amount_var, 
                                   font=("Arial", 12), width=20)
        self.amount_entry.pack(side="left", padx=5)
        
        # Кнопка конвертации
        
        
        # Результат
        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(result_frame, text="Результат:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        self.result_var = tk.StringVar()
        self.result_label = tk.Label(result_frame, textvariable=self.result_var, 
                                   font=("Arial", 14, "bold"), fg="blue")
        self.result_label.pack(side="left", padx=5)
        
        # Таблица курсов
        rates_frame = tk.LabelFrame(self.root, text="Курсы валют к RUB", font=("Arial", 12, "bold"))
        rates_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Заголовок таблицы
        header = tk.Label(rates_frame, text="1 USD = ... RUB", font=("Arial", 10), anchor="w")
        header.pack(fill="x", padx=10, pady=5)
        
        # Отображение курсов
        self.rate_labels = {}
        for code in ["USD", "EUR", "CNY", "KRW"]:
            rate_text = f"1 {code} = {self.rates[code]:.4f} RUB"
            label = tk.Label(rates_frame, text=rate_text, font=("Arial", 10), anchor="w")
            label.pack(fill="x", padx=10, pady=2)
            self.rate_labels[code] = label
        
        # Кнопка обновления курсов
        update_btn = tk.Button(self.root, text="Обновить курсы", command=self.update_rates,
                             font=("Arial", 10), bg="#2196F3", fg="white")
        update_btn.pack(pady=5)
        
        # Привязка события для автоматического пересчета при изменении
        self.amount_var.trace("w", lambda *args: self.convert())
        self.from_combo.bind("<<ComboboxSelected>>", lambda e: self.convert())
        self.to_combo.bind("<<ComboboxSelected>>", lambda e: self.convert())
        
    def get_currency_code(self, display_name):
        """Получить код валюты по отображаемому имени"""
        for code, name in self.currency_names.items():
            if name == display_name:
                return code
        return "RUB"
    
    def convert(self, event=None):
        try:
            # Получаем коды валют
            from_code = self.get_currency_code(self.from_currency.get())
            to_code = self.get_currency_code(self.to_currency.get())
            
            # Получаем сумму
            amount_str = self.amount_var.get().replace(",", ".")
            if not amount_str:
                self.result_var.set("")
                return
                
            amount = float(amount_str)
            
            # Конвертация
            # Сначала в рубли, затем в целевую валюту
            if from_code == "RUB":
                rub_amount = amount
            else:
                rub_amount = amount * self.rates[from_code]
                
            if to_code == "RUB":
                result = rub_amount
            else:
                result = rub_amount / self.rates[to_code]
            
            # Форматирование результата
            if result >= 1000:
                formatted_result = f"{result:,.2f}".replace(",", " ").replace(".", ",")
            else:
                formatted_result = f"{result:.2f}".replace(".", ",")
            
            self.result_var.set(formatted_result)
            
        except ValueError:
            self.result_var.set("Ошибка ввода")
        except Exception as e:
            self.result_var.set("Ошибка")
    
    def update_rates(self):
        # В реальном приложении здесь был бы запрос к API
        # Для примера просто немного изменяем курсы
        import random
        
        for code in ["USD", "EUR", "CNY", "KRW"]:
            change = random.uniform(-0.5, 0.5)
            self.rates[code] = max(0.01, self.rates[code] + change)
            
            # Обновляем отображение
            rate_text = f"1 {code} = {self.rates[code]:.4f} RUB"
            self.rate_labels[code].config(text=rate_text)
        
        # Пересчитываем результат, если он есть
        if self.amount_var.get():
            self.convert()
        
        messagebox.showinfo("Обновлено", "Курсы валют обновлены!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()