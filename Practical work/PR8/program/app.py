import requests
import json
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Tuple
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext


# ==================== МОДЕЛИ ДАННЫХ ====================

@dataclass
class Address:
    """Модель адреса или координат"""
    raw_input: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    display_name: Optional[str] = None
    
    def is_coordinates(self) -> bool:
        """Проверяет, являются ли данные координатами"""
        return self.latitude is not None and self.longitude is not None
    
    def __str__(self):
        if self.display_name:
            return self.display_name[:30] + "..." if len(self.display_name) > 30 else self.display_name
        elif self.is_coordinates():
            return f"{self.latitude}, {self.longitude}"
        return self.raw_input


@dataclass
class Transport:
    """Модель типа транспорта"""
    name: str
    rate_per_km: float
    avg_speed_kmh: float
    
    def calculate_time(self, distance_km: float) -> float:
        """Расчет времени в часах"""
        return distance_km / self.avg_speed_kmh
    
    def calculate_cost(self, distance_km: float) -> float:
        """Расчет стоимости"""
        return distance_km * self.rate_per_km


@dataclass
class DeliveryResult:
    """Модель результата расчета"""
    from_address: Address
    to_address: Address
    transport: Transport
    distance_km: float
    duration_hours: float
    cost_rub: float
    timestamp: datetime
    
    def format_duration(self) -> str:
        """Форматирование времени в часы и минуты"""
        hours = int(self.duration_hours)
        minutes = int((self.duration_hours - hours) * 60)
        return f"{hours} ч {minutes} мин"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для истории"""
        return {
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'from_raw': self.from_address.raw_input,
            'to_raw': self.to_address.raw_input,
            'from_display': str(self.from_address),
            'to_display': str(self.to_address),
            'transport_name': self.transport.name,
            'distance': round(self.distance_km, 1),
            'cost': round(self.cost_rub, 2)
        }


# ==================== СЕРВИС ====================

class DeliveryService:
    """Сервис для работы с API и расчета доставки"""
    
    # Базовые URL API
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"
    
    # Доступные типы транспорта
    TRANSPORTS = {
        "automobile": Transport("Автомобиль", 40.0, 60.0),
        "truck": Transport("Грузовик", 60.0, 55.0),
        "motorcycle": Transport("Мотоцикл", 25.0, 50.0)
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DeliveryCalculator/1.0'
        })
    
    def geocode_address(self, address: str) -> Optional[Address]:
        """
        Преобразование адреса в координаты через Nominatim API
        """
        if not address or not address.strip():
            return None
        
        # Проверка, является ли ввод координатами
        coords = self._parse_coordinates(address)
        if coords:
            lat, lon = coords
            return Address(
                raw_input=address,
                latitude=lat,
                longitude=lon,
                display_name=f"{lat}, {lon}"
            )
        
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            
            response = self.session.get(self.NOMINATIM_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                display_name = data[0]['display_name']
                
                return Address(
                    raw_input=address,
                    latitude=lat,
                    longitude=lon,
                    display_name=display_name
                )
            
            return None
            
        except requests.exceptions.Timeout:
            raise Exception("Превышено время ожидания ответа от сервера")
        except requests.exceptions.ConnectionError:
            raise Exception("Ошибка соединения с сервером. Проверьте интернет-соединение")
        except Exception as e:
            raise Exception(f"Ошибка геокодирования: {str(e)}")
    
    def _parse_coordinates(self, input_str: str) -> Optional[Tuple[float, float]]:
        """
        Парсинг координат из строки формата "широта, долгота" или "широта долгота"
        """
        # Замена запятой на пробел для унификации
        cleaned = input_str.replace(',', ' ')
        parts = cleaned.strip().split()
        
        if len(parts) >= 2:
            try:
                lat = float(parts[0])
                lon = float(parts[1])
                
                # Проверка диапазонов координат
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            except ValueError:
                pass
        
        return None
    
    def get_route(self, from_addr: Address, to_addr: Address) -> Tuple[float, float]:
        """
        Получение расстояния и времени маршрута через OSRM API
        """
        if not from_addr.is_coordinates() or not to_addr.is_coordinates():
            raise Exception("Координаты не определены")
        
        try:
            # Формирование URL для OSRM
            url = f"{self.OSRM_URL}{from_addr.longitude},{from_addr.latitude};{to_addr.longitude},{to_addr.latitude}"
            params = {
                'overview': 'false',
                'geometries': 'geojson'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] != 'Ok':
                raise Exception(f"Ошибка построения маршрута: {data.get('message', 'Неизвестная ошибка')}")
            
            # Расстояние в метрах, время в секундах
            distance_m = data['routes'][0]['distance']
            duration_s = data['routes'][0]['duration']
            
            # Перевод в километры и часы
            distance_km = distance_m / 1000
            duration_h = duration_s / 3600
            
            return distance_km, duration_h
            
        except requests.exceptions.Timeout:
            raise Exception("Превышено время ожидания ответа от сервера маршрутизации")
        except requests.exceptions.ConnectionError:
            raise Exception("Ошибка соединения с сервером маршрутизации")
        except Exception as e:
            raise Exception(f"Ошибка получения маршрута: {str(e)}")
    
    def calculate_delivery(self, from_input: str, to_input: str, transport_key: str) -> DeliveryResult:
        """
        Полный расчет доставки
        """
        # Проверка заполнения полей
        if not from_input or not from_input.strip():
            raise Exception("Заполните пункт отправления!")
        if not to_input or not to_input.strip():
            raise Exception("Заполните пункт назначения!")
        
        # Получение транспорта
        if transport_key not in self.TRANSPORTS:
            raise Exception("Выберите тип транспорта!")
        
        transport = self.TRANSPORTS[transport_key]
        
        # Геокодирование адресов
        from_addr = self.geocode_address(from_input)
        to_addr = self.geocode_address(to_input)
        
        if not from_addr:
            raise Exception(f"Не удалось определить координаты для: {from_input}")
        if not to_addr:
            raise Exception(f"Не удалось определить координаты для: {to_input}")
        
        # Получение маршрута
        distance_km, duration_h = self.get_route(from_addr, to_addr)
        
        # Расчет стоимости и времени с учетом типа транспорта
        cost_rub = transport.calculate_cost(distance_km)
        
        # Корректировка времени с учетом средней скорости транспорта
        adjusted_duration = transport.calculate_time(distance_km)
        
        return DeliveryResult(
            from_address=from_addr,
            to_address=to_addr,
            transport=transport,
            distance_km=distance_km,
            duration_hours=adjusted_duration,
            cost_rub=cost_rub,
            timestamp=datetime.now()
        )


# ==================== ГЛАВНАЯ ФОРМА ====================

class DeliveryCalculatorApp:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор доставки")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Сервис
        self.service = DeliveryService()
        
        # История расчетов
        self.history: List[DeliveryResult] = []
        
        # Создание интерфейса
        self._create_widgets()
        
        # Загрузка тестовых данных для демонстрации
        self._load_demo_history()
    
    def _create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # Основной контейнер с отступами
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Калькулятор доставки", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 15), sticky=tk.W)
        
        # Рамка параметров доставки
        params_frame = ttk.LabelFrame(main_frame, text="Параметры доставки", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # Пункт отправления
        ttk.Label(params_frame, text="Пункт отправления:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.from_entry = ttk.Entry(params_frame, width=50)
        self.from_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.from_entry.insert(0, "Москва, Красная площадь")
        
        ttk.Label(params_frame, text="(адрес или координаты, например: 55.7558, 37.6173)", 
                  font=('Arial', 8)).grid(row=1, column=1, sticky=tk.W)
        
        # Пункт назначения
        ttk.Label(params_frame, text="Пункт назначения:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.to_entry = ttk.Entry(params_frame, width=50)
        self.to_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        self.to_entry.insert(0, "Санкт-Петербург, Невский проспект")
        
        ttk.Label(params_frame, text="(адрес или координаты)", 
                  font=('Arial', 8)).grid(row=3, column=1, sticky=tk.W)
        
        # Тип транспорта
        ttk.Label(params_frame, text="Тип транспорта:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        self.transport_var = tk.StringVar(value="automobile")
        transport_frame = ttk.Frame(params_frame)
        transport_frame.grid(row=4, column=1, sticky=tk.W, pady=(10, 0))
        
        ttk.Radiobutton(transport_frame, text="Автомобиль (40 руб/км, 60 км/ч)", 
                        variable=self.transport_var, value="automobile").pack(anchor=tk.W)
        ttk.Radiobutton(transport_frame, text="Грузовик (60 руб/км, 55 км/ч)", 
                        variable=self.transport_var, value="truck").pack(anchor=tk.W)
        ttk.Radiobutton(transport_frame, text="Мотоцикл (25 руб/км, 50 км/ч)", 
                        variable=self.transport_var, value="motorcycle").pack(anchor=tk.W)
        
        # Кнопки
        buttons_frame = ttk.Frame(params_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=(15, 0))
        
        self.calc_button = ttk.Button(buttons_frame, text="Рассчитать", command=self.calculate_delivery)
        self.calc_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(buttons_frame, text="Очистить", command=self.clear_fields)
        self.clear_button.pack(side=tk.LEFT)
        
        # Рамка результата
        result_frame = ttk.LabelFrame(main_frame, text="Результат расчета", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        
        self.result_text = tk.Text(result_frame, height=8, width=70, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Рамка истории
        history_frame = ttk.LabelFrame(main_frame, text="История расчетов", padding="10")
        history_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Treeview для истории
        columns = ("time", "from_addr", "to_addr", "vehicle", "cost")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=6)
        
        self.history_tree.heading("time", text="Время")
        self.history_tree.heading("from_addr", text="Откуда")
        self.history_tree.heading("to_addr", text="Куда")
        self.history_tree.heading("vehicle", text="Транспорт")
        self.history_tree.heading("cost", text="Стоимость")
        
        self.history_tree.column("time", width=100)
        self.history_tree.column("from_addr", width=150)
        self.history_tree.column("to_addr", width=150)
        self.history_tree.column("vehicle", width=80)
        self.history_tree.column("cost", width=100)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Скроллбар для истории
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        history_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        # Привязка события двойного клика для загрузки из истории
        self.history_tree.bind("<Double-1>", self.load_from_history)
    
    def _load_demo_history(self):
        """Загрузка демонстрационных данных в историю"""
        # Демо-данные из задания
        demo_results = [
            {
                'timestamp': datetime(2026, 2, 17, 20, 41, 8),
                'from_raw': 'Москва, Красная площадь',
                'to_raw': 'Санкт-Петербург, Невский проспект',
                'transport': 'automobile',
                'distance': 633.6,
                'duration': 10.55,
                'cost': 25344.00
            },
            {
                'timestamp': datetime(2026, 2, 17, 20, 42, 14),
                'from_raw': '55.7558, 37.6173',
                'to_raw': '59.9343, 30.3351',
                'transport': 'truck',
                'distance': 633.0,
                'duration': 11.51,
                'cost': 37980.00
            }
        ]
        
        for demo in demo_results:
            from_addr = Address(raw_input=demo['from_raw'])
            to_addr = Address(raw_input=demo['to_raw'])
            
            # Попытка получить отображаемые имена
            try:
                geo_from = self.service.geocode_address(demo['from_raw'])
                if geo_from:
                    from_addr = geo_from
            except:
                pass
            
            try:
                geo_to = self.service.geocode_address(demo['to_raw'])
                if geo_to:
                    to_addr = geo_to
            except:
                pass
            
            transport = self.service.TRANSPORTS[demo['transport']]
            
            result = DeliveryResult(
                from_address=from_addr,
                to_address=to_addr,
                transport=transport,
                distance_km=demo['distance'],
                duration_hours=demo['duration'],
                cost_rub=demo['cost'],
                timestamp=demo['timestamp']
            )
            self.history.append(result)
            self._add_history_to_tree(result)
    
    def _add_history_to_tree(self, result: DeliveryResult):
        """Добавление результата в дерево истории"""
        time_str = result.timestamp.strftime("%H:%M:%S")
        from_str = str(result.from_address)
        to_str = str(result.to_address)
        vehicle_short = result.transport.name[:4] if len(result.transport.name) > 4 else result.transport.name
        cost_str = f"{result.cost_rub:.0f} руб."
        
        self.history_tree.insert("", 0, values=(time_str, from_str, to_str, vehicle_short, cost_str))
    
    def calculate_delivery(self):
        """Обработчик кнопки Рассчитать"""
        from_input = self.from_entry.get().strip()
        to_input = self.to_entry.get().strip()
        transport_key = self.transport_var.get()
        
        try:
            # Выполнение расчета через сервис
            result = self.service.calculate_delivery(from_input, to_input, transport_key)
            
            # Добавление в историю
            self.history.insert(0, result)
            self._add_history_to_tree(result)
            
            # Отображение результата
            self._show_result(result)
            
        except Exception as e:
            self._show_error(str(e))
    
    def _show_result(self, result: DeliveryResult):
        """Отображение результата расчета"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        result_text = f"""
✅ Расчет выполнен успешно

Откуда: {result.from_address.raw_input}
Куда: {result.to_address.raw_input}
Транспорт: {result.transport.name}

Расстояние: {result.distance_km:.1f} км
Время: {result.format_duration()}
Стоимость: {result.cost_rub:.2f} руб.

Рассчитано: {result.timestamp.strftime('%d.%m.%Y %H:%M:%S')}
"""
        self.result_text.insert(1.0, result_text)
        self.result_text.config(state=tk.DISABLED)
    
    def _show_error(self, error_message: str):
        """Отображение ошибки"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        error_text = f"""
❌ Ошибка

{error_message}
"""
        self.result_text.insert(1.0, error_text)
        self.result_text.config(state=tk.DISABLED)
    
    def clear_fields(self):
        """Очистка полей ввода"""
        self.from_entry.delete(0, tk.END)
        self.to_entry.delete(0, tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
    
    def load_from_history(self, event):
        """Загрузка данных из истории по двойному клику"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.history_tree.item(item, 'values')
        
        # Поиск соответствующего результата в истории
        idx = self.history_tree.index(item)
        if idx < len(self.history):
            result = self.history[idx]
            self.from_entry.delete(0, tk.END)
            self.from_entry.insert(0, result.from_address.raw_input)
            self.to_entry.delete(0, tk.END)
            self.to_entry.insert(0, result.to_address.raw_input)
            
            # Установка типа транспорта
            for key, transport in self.service.TRANSPORTS.items():
                if transport.name == result.transport.name:
                    self.transport_var.set(key)
                    break


# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================

def main():
    root = tk.Tk()
    app = DeliveryCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()