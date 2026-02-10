import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import threading
import time
from datetime import datetime
from queue import Queue

class NetworkPacket:
    """Класс для представления сетевого пакета"""
    def __init__(self, packet_id, source, destination, size):
        self.id = packet_id
        self.source = source
        self.destination = destination
        self.size = size
        self.timestamp = datetime.now()
        self.sent_time = None
        self.delivered_time = None
        self.delay = 0
        self.path = []
        self.color = self.generate_color()
    
    def generate_color(self):
        """Генерация случайного цвета для пакета"""
        colors = ['#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0', 
                  '#118AB2', '#EF476F', '#7209B7', '#F15BB5']
        return random.choice(colors)
    
    def calculate_delay(self):
        """Расчет задержки доставки"""
        if self.sent_time and self.delivered_time:
            self.delay = int((self.delivered_time - self.sent_time).total_seconds() * 1000)
        return self.delay

class NetworkDevice:
    """Класс для представления сетевого устройства"""
    def __init__(self, name, device_type, x, y):
        self.name = name
        self.type = device_type  # 'pc' или 'switch'
        self.x = x
        self.y = y
        self.connected_to = []
        self.status = 'idle'  # idle, sending, receiving, processing
        self.packets = []
        self.indicator_color = '#2D3047'
        self.base_color = '#6C757D' if device_type == 'pc' else '#118AB2'
        
    def add_connection(self, device):
        """Добавление соединения с другим устройством"""
        self.connected_to.append(device)
    
    def update_status(self, status):
        """Обновление статуса устройства"""
        self.status = status
        if status == 'sending':
            self.indicator_color = '#FFD166'
        elif status == 'receiving':
            self.indicator_color = '#06D6A0'
        elif status == 'processing':
            self.indicator_color = '#7209B7'
        else:
            self.indicator_color = '#2D3047'

class NetworkTerminal:
    """Основной класс приложения сетевого терминала"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Сетевой терминал - Имитация ЛВС")
        self.root.geometry("1400x800")
        self.root.configure(bg='#1A1A2E')
        
        # Переменные управления
        self.running = False
        self.packets_per_second = 3
        self.packet_counter = 0
        self.total_packets = 0
        self.active_packets = []
        self.message_queue = Queue()
        self.stop_requested = False  # Флаг для запроса остановки
        
        # Создание сетевых устройств
        self.devices = self.create_network_devices()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Запуск потоков
        self.start_animation_thread()
        self.start_log_thread()
        
    def create_network_devices(self):
        """Создание сетевых устройств"""
        devices = []
        
        # Создание компьютеров
        pc1 = NetworkDevice('ПК1', 'pc', 100, 100)
        pc2 = NetworkDevice('ПК2', 'pc', 100, 600)
        pc3 = NetworkDevice('ПК3', 'pc', 1200, 100)
        pc4 = NetworkDevice('ПК4', 'pc', 1200, 600)
        
        # Создание коммутатора
        switch = NetworkDevice('SWITCH', 'switch', 650, 350)
        
        devices.extend([pc1, pc2, pc3, pc4, switch])
        
        # Создание соединений (каждый ПК подключен к коммутатору)
        for pc in [pc1, pc2, pc3, pc4]:
            pc.add_connection(switch)
            switch.add_connection(pc)
        
        return devices
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создание главного фрейма
        main_frame = tk.Frame(self.root, bg='#1A1A2E')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - сетевая визуализация
        left_frame = tk.Frame(main_frame, bg='#162447', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Холст для отрисовки сети
        self.canvas = tk.Canvas(left_frame, bg='#162447', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Правая панель - консоль и управление
        right_frame = tk.Frame(main_frame, bg='#1F4068', width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Заголовок консоли
        console_label = tk.Label(right_frame, text="КОНСОЛЬ СЕТИ ПВС", 
                                font=('Consolas', 14, 'bold'), 
                                bg='#1F4068', fg='#FFFFFF')
        console_label.pack(pady=(10, 5))
        
        # Консоль вывода
        self.console = scrolledtext.ScrolledText(
            right_frame, 
            font=('Consolas', 10), 
            bg='#0F3460', 
            fg='#E1E5EA',
            wrap=tk.WORD,
            height=25,
            relief=tk.FLAT,
            insertbackground='white'
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Панель управления
        control_frame = tk.Frame(right_frame, bg='#1F4068')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Кнопки управления
        self.start_button = tk.Button(
            control_frame,
            text="▶ СТАРТ",
            command=self.start_transmission,
            font=('Arial', 10, 'bold'),
            bg='#06D6A0',
            fg='white',
            relief=tk.RAISED,
            bd=2,
            width=10
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = tk.Button(
            control_frame,
            text="⏹ СТОП",
            command=self.stop_transmission,
            font=('Arial', 10, 'bold'),
            bg='#EF476F',
            fg='white',
            relief=tk.RAISED,
            bd=2,
            width=10,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(
            control_frame,
            text="🧹 ОЧИСТИТЬ",
            command=self.clear_console_and_reset,
            font=('Arial', 10, 'bold'),
            bg='#FFD166',
            fg='black',
            relief=tk.RAISED,
            bd=2,
            width=12
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Регулятор скорости
        speed_frame = tk.Frame(control_frame, bg='#1F4068')
        speed_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        speed_label = tk.Label(speed_frame, text="СКОРОСТЬ:", 
                              bg='#1F4068', fg='white')
        speed_label.pack(anchor=tk.W)
        
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            length=100,
            bg='#1F4068',
            fg='white',
            troughcolor='#0F3460',
            highlightbackground='#1F4068',
            command=self.update_speed
        )
        self.speed_scale.set(self.packets_per_second)
        self.speed_scale.pack()
        
        # Панель статуса (без счетчика пакетов)
        status_frame = tk.Frame(right_frame, bg='#1A1A2E')
        status_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="✓ СИСТЕМА ГОТОВА",
            font=('Arial', 10, 'bold'),
            bg='#1A1A2E',
            fg='#4ECDC4'
        )
        self.status_label.pack(anchor=tk.W)
        
        # Отрисовка начального состояния сети
        self.draw_network()
        
        # Инициализация консоли с примером из задания
        self.initialize_console()
    
    def initialize_console(self):
        """Инициализация консоли примерами из задания"""
        example_logs = [
            "# Сетевой терминал - Имитация ЛВС",
            "",
            "## ПК1",
            "- АКТИВЕН",
            "- SWITCH",
            "",
            "---",
            "",
            "### КОНСОЛЬ СЕТИ ПВС",
            "",
            "[20:39:05.783] Пакет #5 достиг SWITCH",
            "[20:39:05] Передача пакетов остановлена",
            "Всего передано пакетов: 7",
            "",
            "---",
            ""
        ]
        
        for log in example_logs:
            self.console.insert(tk.END, log + "\n")
        self.console.see(tk.END)
    
    def draw_network(self):
        """Отрисовка сетевых устройств и соединений"""
        self.canvas.delete("all")
        
        # Рисование соединений (пунктирные линии)
        for device in self.devices:
            if device.type == 'switch':
                for connected in device.connected_to:
                    self.canvas.create_line(
                        device.x, device.y, connected.x, connected.y,
                        fill='#4A4E69', width=2, dash=(5, 5), tags="connection"
                    )
        
        # Рисование устройств
        for device in self.devices:
            if device.type == 'pc':
                # Компьютеры - прямоугольники с деталями
                self.draw_pc(device)
            else:
                # Коммутатор - голубой прямоугольник с портами
                self.draw_switch(device)
    
    def draw_pc(self, device):
        """Отрисовка компьютера"""
        # Основной корпус
        self.canvas.create_rectangle(
            device.x-40, device.y-20, device.x+40, device.y+20,
            fill=device.base_color, outline='#495057', width=2,
            tags=f"device_{device.name}"
        )
        
        # Индикатор состояния
        self.canvas.create_oval(
            device.x+25, device.y-15, device.x+35, device.y-5,
            fill=device.indicator_color, outline='',
            tags=f"indicator_{device.name}"
        )
        
        # Экран (прямоугольник внутри)
        self.canvas.create_rectangle(
            device.x-30, device.y-10, device.x+20, device.y+5,
            fill='#343A40', outline='#495057', width=1,
            tags=f"device_{device.name}"
        )
        
        # Название устройства
        self.canvas.create_text(
            device.x, device.y+35,
            text=device.name,
            fill='#E9ECEF',
            font=('Arial', 10, 'bold'),
            tags=f"label_{device.name}"
        )
        
        # Статус под ПК
        status_text = "✓ АКТИВЕН" if device.name == "ПК1" else "✓ ГОТОВ"
        self.canvas.create_text(
            device.x, device.y-25,
            text=status_text,
            fill='#06D6A0',
            font=('Arial', 9, 'bold'),
            tags=f"status_{device.name}"
        )
    
    def draw_switch(self, device):
        """Отрисовка коммутатора"""
        # Основной корпус
        self.canvas.create_rectangle(
            device.x-60, device.y-40, device.x+60, device.y+40,
            fill=device.base_color, outline='#0D3B66', width=3,
            tags=f"device_{device.name}"
        )
        
        # Индикаторы портов
        port_positions = [(-40, -25), (-20, -25), (0, -25), (20, -25), (40, -25),
                         (-40, 0), (-20, 0), (0, 0), (20, 0), (40, 0),
                         (-40, 25), (-20, 25), (0, 25), (20, 25), (40, 25)]
        
        for i, (dx, dy) in enumerate(port_positions):
            color = '#FFD166' if i < 4 else '#2D3047'  # Первые 4 порта активны
            self.canvas.create_oval(
                device.x+dx-5, device.y+dy-5, device.x+dx+5, device.y+dy+5,
                fill=color, outline='#0D3B66', width=1,
                tags=f"port_{device.name}_{i}"
            )
        
        # Название устройства
        self.canvas.create_text(
            device.x, device.y+65,
            text=device.name,
            fill='#E9ECEF',
            font=('Arial', 11, 'bold'),
            tags=f"label_{device.name}"
        )
        
        # Статус
        self.canvas.create_text(
            device.x, device.y-55,
            text="✓ АКТИВЕН",
            fill='#06D6A0',
            font=('Arial', 9, 'bold'),
            tags=f"status_{device.name}"
        )
    
    def draw_packet(self, packet, x, y):
        """Отрисовка пакета"""
        return self.canvas.create_oval(
            x-15, y-15, x+15, y+15,
            fill=packet.color, outline='white', width=2,
            tags=f"packet_{packet.id}"
        )
    
    def update_device_status(self, device_name, status):
        """Обновление статуса устройства"""
        for device in self.devices:
            if device.name == device_name:
                device.update_status(status)
                self.canvas.itemconfig(f"indicator_{device_name}", fill=device.indicator_color)
                break
    
    def start_transmission(self):
        """Начало передачи пакетов"""
        if not self.running:
            self.running = True
            self.stop_requested = False
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="✓ ПЕРЕДАЧА АКТИВНА", fg='#FFD166')
            self.log_message("\n" + "="*50)
            self.log_message("Передача пакетов начата")
            self.log_message("="*50)
    
    def stop_transmission(self):
        """Остановка передачи пакетов"""
        if self.running:
            # Устанавливаем флаг остановки
            self.stop_requested = True
            self.running = False
            
            # Получаем текущее время в формате HH:MM:SS
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Выводим сообщение об остановке в формате из задания
            self.log_message(f"\n[{current_time}] Передача пакетов остановлена")
            self.log_message(f"Всего передано пакетов: {self.total_packets}")
            
            # Обновляем интерфейс
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="✓ СИСТЕМА ОСТАНОВЛЕНА", fg='#EF476F')
            
            # Добавляем разделитель для читаемости
            self.log_message("-" * 50)
    
    def clear_console_and_reset(self):
        """Полный сброс системы"""
        # Останавливаем текущую передачу если она активна
        if self.running:
            self.stop_requested = True
            self.running = False
        
        # Сбрасываем все счетчики
        self.packet_counter = 0
        self.total_packets = 0
        
        # Очищаем очередь сообщений
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except:
                break
        
        # Очищаем холст (удаляем все пакеты)
        self.canvas.delete("packet")
        self.canvas.delete("all")
        
        # Сбрасываем статусы всех устройств
        for device in self.devices:
            device.status = 'idle'
            device.indicator_color = '#2D3047'
            device.packets = []
        
        # Перерисовываем сеть
        self.draw_network()
        
        # Очищаем консоль
        self.console.delete(1.0, tk.END)
        
        # Сбрасываем интерфейс к начальному состоянию
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="✓ СИСТЕМА СБРОШЕНА", fg='#FFD166')
        
        # Инициализируем консоль заново
        self.initialize_console()
        
        # Сбрасываем флаг остановки
        self.stop_requested = False
        
        # Выводим сообщение о сбросе
        self.log_message("\n" + "="*50)
        self.log_message("СИСТЕМА ПОЛНОСТЬЮ СБРОШЕНА")
        self.log_message("Все счетчики обнулены")
        self.log_message("Готов к новой сессии")
        self.log_message("="*50)
    
    def update_speed(self, value):
        """Обновление скорости передачи"""
        self.packets_per_second = int(value)
    
    def log_message(self, message):
        """Добавление сообщения в консоль"""
        self.message_queue.put(message)
    
    def generate_packet(self):
        """Генерация случайного пакета"""
        if not self.running or self.stop_requested:
            return None
        
        self.packet_counter += 1
        self.total_packets += 1
        
        # Случайный выбор источника и получателя
        sources = ['ПК1', 'ПК2', 'ПК3', 'ПК4']
        destinations = ['ПК1', 'ПК2', 'ПК3', 'ПК4']
        
        source = random.choice(sources)
        # Исключаем возможность отправки пакета самому себе
        possible_destinations = [d for d in destinations if d != source]
        if not possible_destinations:
            possible_destinations = destinations
        
        destination = random.choice(possible_destinations)
        
        # Случайный размер пакета
        size = random.randint(100, 1500)
        
        packet = NetworkPacket(self.packet_counter, source, destination, size)
        packet.sent_time = datetime.now()
        
        # Логирование создания пакета
        timestamp = packet.timestamp.strftime("%H:%M:%S.%f")[:-3]
        self.log_message(f"[{timestamp}] Пакет #{packet.id}: {packet.source} -> {packet.destination}, Размер: {packet.size} байт")
        
        return packet
    
    def simulate_delivery(self, packet):
        """Симуляция доставки пакета"""
        # Проверяем флаг остановки
        if self.stop_requested:
            return
        
        # Имитация задержки
        delay_ms = random.randint(2000, 4000)
        
        # Разбиваем задержку на части для проверки флага остановки
        chunk_size = 0.1  # 100 мс
        chunks = int(delay_ms / 100)
        
        for i in range(chunks):
            if self.stop_requested:
                return
            time.sleep(chunk_size)
        
        # Проверяем еще раз после задержки
        if self.stop_requested:
            return
        
        packet.delivered_time = datetime.now()
        packet.calculate_delay()
        
        # Логирование доставки
        timestamp = packet.delivered_time.strftime("%H:%M:%S.%f")[:-3]
        self.log_message(f"[{timestamp}] Пакет #{packet.id} доставлен на {packet.destination} (задержка: {packet.delay} мс)")
        
        # Логирование прохождения через коммутатор (раньше времени доставки)
        switch_time = datetime.fromtimestamp(
            packet.sent_time.timestamp() + (packet.delivered_time.timestamp() - packet.sent_time.timestamp()) * 0.5
        ).strftime("%H:%M:%S.%f")[:-3]
        self.log_message(f"[{switch_time}] Пакет #{packet.id} достиг SWITCH")
    
    def animate_packet(self, packet):
        """Анимация движения пакета"""
        # Проверяем флаг остановки
        if self.stop_requested:
            return
        
        # Находим устройства
        source_device = next((d for d in self.devices if d.name == packet.source), None)
        dest_device = next((d for d in self.devices if d.name == packet.destination), None)
        switch_device = next((d for d in self.devices if d.type == 'switch'), None)
        
        if not all([source_device, dest_device, switch_device]):
            return
        
        # Анимация от источника к коммутатору
        self.update_device_status(packet.source, 'sending')
        packet_obj = self.draw_packet(packet, source_device.x, source_device.y)
        
        steps = 50
        for i in range(steps + 1):
            if self.stop_requested:
                self.canvas.delete(packet_obj)
                self.update_device_status(packet.source, 'idle')
                return
            t = i / steps
            x = source_device.x + (switch_device.x - source_device.x) * t
            y = source_device.y + (switch_device.y - source_device.y) * t
            self.canvas.coords(packet_obj, x-15, y-15, x+15, y+15)
            self.root.update()
            time.sleep(0.02)
        
        # Пауза на коммутаторе
        if self.stop_requested:
            self.canvas.delete(packet_obj)
            self.update_device_status(packet.source, 'idle')
            self.update_device_status('SWITCH', 'idle')
            return
        
        self.update_device_status('SWITCH', 'processing')
        time.sleep(0.3)
        
        # Анимация от коммутатора к получателю
        if self.stop_requested:
            self.canvas.delete(packet_obj)
            self.update_device_status('SWITCH', 'idle')
            self.update_device_status(packet.source, 'idle')
            return
        
        self.update_device_status('SWITCH', 'idle')
        self.update_device_status(packet.destination, 'receiving')
        
        for i in range(steps + 1):
            if self.stop_requested:
                self.canvas.delete(packet_obj)
                self.update_device_status(packet.destination, 'idle')
                return
            t = i / steps
            x = switch_device.x + (dest_device.x - switch_device.x) * t
            y = switch_device.y + (dest_device.y - switch_device.y) * t
            self.canvas.coords(packet_obj, x-15, y-15, x+15, y+15)
            self.root.update()
            time.sleep(0.02)
        
        # Удаление пакета
        if not self.stop_requested:
            time.sleep(0.5)
            self.canvas.delete(packet_obj)
            self.update_device_status(packet.destination, 'idle')
    
    def packet_generator_thread(self):
        """Поток генерации и обработки пакетов"""
        while True:
            if self.running and not self.stop_requested:
                packet = self.generate_packet()
                if packet:
                    # Запуск анимации и симуляции в отдельных потоках
                    threading.Thread(
                        target=self.animate_packet,
                        args=(packet,),
                        daemon=True
                    ).start()
                    
                    threading.Thread(
                        target=self.simulate_delivery,
                        args=(packet,),
                        daemon=True
                    ).start()
                
                # Задержка между генерацией пакетов
                delay = 1.0 / self.packets_per_second
                chunks = int(delay / 0.1)
                for i in range(chunks):
                    if self.stop_requested:
                        break
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
    
    def start_animation_thread(self):
        """Запуск потока анимации"""
        threading.Thread(target=self.packet_generator_thread, daemon=True).start()
    
    def start_log_thread(self):
        """Запуск потока обработки логов"""
        def process_logs():
            while True:
                try:
                    message = self.message_queue.get(timeout=0.1)
                    self.console.insert(tk.END, message + "\n")
                    self.console.see(tk.END)
                    self.root.update()
                except:
                    pass
        
        threading.Thread(target=process_logs, daemon=True).start()

def main():
    """Основная функция"""
    root = tk.Tk()
    app = NetworkTerminal(root)
    root.mainloop()

if __name__ == "__main__":
    main()