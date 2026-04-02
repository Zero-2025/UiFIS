import pygame
import pygame_gui
import math
import sys
import json
import os
from pygame.locals import *

# Инициализация
pygame.init()
pygame.display.set_caption("Солнечная система - Интерактивное управление")

# Константы
WIDTH, HEIGHT = 1280, 800
FPS = 60
BG_COLOR = (0, 0, 20)
SUN_COLOR = (255, 200, 50)
STAR_COUNT = 200

class Star:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.brightness = random.randint(50, 255)
        self.twinkle_speed = random.uniform(0.5, 2.0)
    
    def update(self):
        self.brightness += self.twinkle_speed
        if self.brightness > 255:
            self.brightness = 255
            self.twinkle_speed = -abs(self.twinkle_speed)
        elif self.brightness < 50:
            self.brightness = 50
            self.twinkle_speed = abs(self.twinkle_speed)

# Класс планеты
class Planet:
    def __init__(self, name, color, size, distance, eccentricity, speed, angle=0, description="", 
                 mass="", diameter="", temperature="", atmosphere=""):
        self.name = name
        self.color = color
        self.size = size
        self.distance = distance
        self.eccentricity = eccentricity
        self.speed = speed
        self.angle = angle
        self.original_speed = speed
        self.trail = []
        self.trail_length = 200
        self.description = description
        self.mass = mass
        self.diameter = diameter
        self.temperature = temperature
        self.atmosphere = atmosphere
        
    def get_position(self, center_x, center_y, zoom, offset_x, offset_y):
        a = self.distance * zoom
        e = self.eccentricity
        r = a * (1 - e**2) / (1 + e * math.cos(self.angle))
        x = r * math.cos(self.angle) + center_x + offset_x
        y = r * math.sin(self.angle) + center_y + offset_y
        return int(x), int(y)
    
    def update(self, time_multiplier=1.0):
        self.speed = self.original_speed * time_multiplier
        self.angle += self.speed
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
    
    def add_trail(self, pos):
        self.trail.append(pos)
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
    
    def draw_trail(self, screen):
        if len(self.trail) < 2:
            return
            
        for i in range(len(self.trail) - 1):
            alpha = int(180 * (i / len(self.trail)))
            color = tuple(min(255, c * alpha // 255) for c in self.color)
            width = max(1, int(self.size // 4 * (i / len(self.trail))))
            if self.trail[i] and self.trail[i+1]:
                try:
                    pygame.draw.line(screen, color, self.trail[i], self.trail[i + 1], width)
                except:
                    pass

# Класс камеры
class Camera:
    def __init__(self, width, height):
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.width = width
        self.height = height
        self.zoom_speed = 0.1
        self.pan_speed = 5
        
    def handle_event(self, event, ui_hover=False):
        if ui_hover:
            return
            
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.dragging = True
                self.last_mouse_x, self.last_mouse_y = pygame.mouse.get_pos()
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - self.last_mouse_x
                dy = mouse_y - self.last_mouse_y
                self.offset_x += dx
                self.offset_y += dy
                self.last_mouse_x, self.last_mouse_y = mouse_x, mouse_y
    
    def handle_keys(self, keys):
        if keys[K_LEFT]:
            self.offset_x += self.pan_speed
        if keys[K_RIGHT]:
            self.offset_x -= self.pan_speed
        if keys[K_UP]:
            self.offset_y += self.pan_speed
        if keys[K_DOWN]:
            self.offset_y -= self.pan_speed
    
    def zoom_in(self):
        self.zoom = min(3.0, self.zoom + self.zoom_speed)
    
    def zoom_out(self):
        self.zoom = max(0.3, self.zoom - self.zoom_speed)
    
    def reset(self):
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

# Класс для управления настройками
class Settings:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.show_trails = True
        self.show_orbits = True
        self.show_labels = True
        self.show_grid = False
        self.quality = "high"
        self.load()
    
    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.show_trails = data.get('show_trails', True)
                    self.show_orbits = data.get('show_orbits', True)
                    self.show_labels = data.get('show_labels', True)
                    self.show_grid = data.get('show_grid', False)
                    self.quality = data.get('quality', 'high')
            except:
                pass
    
    def save(self):
        data = {
            'show_trails': self.show_trails,
            'show_orbits': self.show_orbits,
            'show_labels': self.show_labels,
            'show_grid': self.show_grid,
            'quality': self.quality
        }
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except:
            pass

# Класс для информации о планете
class PlanetInfoPanel:
    def __init__(self, ui_manager, x, y, width, height):
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((x, y), (width, height)),
            manager=ui_manager,
            object_id="#planet_info_panel"
        )
        
        # Заголовок с названием планеты
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (width - 20, 40)),
            text="ИНФОРМАЦИЯ О ПЛАНЕТЕ",
            manager=ui_manager,
            container=self.panel,
            object_id="#info_title"
        )
        
        # Иконка планеты (цветной круг)
        self.planet_icon = None
        self.planet_color = (100, 100, 100)
        
        # Текстовые поля для информации
        self.description_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 60), (width - 20, 80)),
            html_text="<font size=3><i>Нажмите на любую планету, чтобы увидеть информацию</i></font>",
            manager=ui_manager,
            container=self.panel
        )
        
        # Характеристики
        self.stats_frame = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 150), (width - 20, 200)),
            manager=ui_manager,
            container=self.panel
        )
        
        self.stats_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (width - 40, 25)),
            text="<b>ХАРАКТЕРИСТИКИ</b>",
            manager=ui_manager,
            container=self.stats_frame
        )
        
        # Создаем поля для статистики
        self.stats_labels = {}
        stats_y = 45
        stats = [
            ("mass", "Масса:"),
            ("diameter", "Диаметр:"),
            ("distance", "Расстояние от Солнца:"),
            ("orbit_time", "Период обращения:"),
            ("temperature", "Температура:"),
            ("atmosphere", "Атмосфера:")
        ]
        
        for key, label in stats:
            # Название характеристики
            name_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, stats_y), (150, 25)),
                text=label,
                manager=ui_manager,
                container=self.stats_frame
            )
            # Значение
            value_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((160, stats_y), (width - 190, 25)),
                text="—",
                manager=ui_manager,
                container=self.stats_frame
            )
            self.stats_labels[key] = value_label
            stats_y += 30
        
        # Дополнительная информация
        self.extra_info = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 360), (width - 20, 80)),
            html_text="",
            manager=ui_manager,
            container=self.panel
        )
        
        self.width = width
        self.height = height
        
    def update_info(self, planet):
        if not planet:
            self.title_label.set_text("ИНФОРМАЦИЯ О ПЛАНЕТЕ")
            self.description_text.set_text("<font size=3><i>Нажмите на любую планету, чтобы увидеть информацию</i></font>")
            for key in self.stats_labels:
                self.stats_labels[key].set_text("—")
            self.extra_info.set_text("")
            return
        
        # Обновляем заголовок
        self.title_label.set_text(f"<b>{planet.name.upper()}</b>")
        
        # Обновляем описание
        self.description_text.set_text(f"<font size=3>{planet.description}</font>")
        
        # Обновляем характеристики
        self.stats_labels["mass"].set_text(planet.mass)
        self.stats_labels["diameter"].set_text(planet.diameter)
        self.stats_labels["distance"].set_text(f"{planet.distance} млн км")
        self.stats_labels["orbit_time"].set_text(f"{365 / (planet.speed * 100):.1f} дней")
        self.stats_labels["temperature"].set_text(planet.temperature)
        self.stats_labels["atmosphere"].set_text(planet.atmosphere)
        
        # Дополнительная информация
        extra = f"""
        <font size=2>
        <b>Интересные факты:</b><br>
        • Эксцентриситет орбиты: {planet.eccentricity:.3f}<br>
        • Относительная скорость: {(planet.speed / 0.03):.2f}%<br>
        • Текущий угол: {planet.angle:.2f} рад
        </font>
        """
        self.extra_info.set_text(extra)
    
    def set_position(self, x, y):
        self.panel.set_relative_position((x, y))

# Главная функция
def main():
    import random
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT), RESIZABLE)
    
    # Инициализация объектов
    clock = pygame.time.Clock()
    ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    camera = Camera(WIDTH, HEIGHT)
    settings = Settings()
    
    # Звездное небо
    stars = []
    for _ in range(STAR_COUNT):
        stars.append(Star(WIDTH, HEIGHT))
    
    # Создание планет с подробными характеристиками
    planets = [
        Planet("Меркурий", (180, 180, 180), 4, 80, 0.205, 0.0478, 
               description="Ближайшая к Солнцу планета. Самая маленькая и быстрая планета Солнечной системы.",
               mass="3.30 × 10²³ кг", diameter="4 879 км", 
               temperature="от -173°C до +427°C", atmosphere="Разреженная (кислород, натрий, водород)"),
        Planet("Венера", (255, 200, 100), 6, 120, 0.007, 0.0350,
               description="Самая горячая планета. Имеет плотную атмосферу из углекислого газа.",
               mass="4.87 × 10²⁴ кг", diameter="12 104 км",
               temperature="+462°C (средняя)", atmosphere="Углекислый газ (96%), азот (3.5%)"),
        Planet("Земля", (100, 150, 255), 7, 160, 0.017, 0.0298,
               description="Наш дом! Единственная известная планета с жизнью.",
               mass="5.97 × 10²⁴ кг", diameter="12 742 км",
               temperature="от -88°C до +58°C", atmosphere="Азот (78%), кислород (21%)"),
        Planet("Марс", (200, 100, 80), 6, 200, 0.093, 0.0241,
               description="Красная планета. Имеет самую высокую гору в Солнечной системе - Олимп.",
               mass="6.42 × 10²³ кг", diameter="6 779 км",
               temperature="от -140°C до +20°C", atmosphere="Углекислый газ (95%), аргон (1.6%)"),
        Planet("Юпитер", (200, 160, 100), 16, 280, 0.048, 0.0131,
               description="Самая большая планета. Имеет 79 известных спутников.",
               mass="1.90 × 10²⁷ кг", diameter="139 820 км",
               temperature="-145°C (средняя)", atmosphere="Водород (90%), гелий (10%)"),
        Planet("Сатурн", (220, 180, 100), 14, 360, 0.056, 0.0097,
               description="Известен своими красивыми кольцами. Вторая по величине планета.",
               mass="5.68 × 10²⁶ кг", diameter="116 460 км",
               temperature="-178°C (средняя)", atmosphere="Водород (96%), гелий (3%)"),
        Planet("Уран", (150, 200, 220), 11, 440, 0.047, 0.0068,
               description="Вращается 'лежа на боку'. Первая планета, открытая с помощью телескопа.",
               mass="8.68 × 10²⁵ кг", diameter="50 724 км",
               temperature="-224°C (средняя)", atmosphere="Водород, гелий, метан"),
        Planet("Нептун", (80, 100, 200), 11, 520, 0.009, 0.0054,
               description="Самая ветреная планета со скоростью ветра до 2100 км/ч.",
               mass="1.02 × 10²⁶ кг", diameter="49 244 км",
               temperature="-214°C (средняя)", atmosphere="Водород, гелий, метан"),
    ]
    
    # UI элементы
    control_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((10, 10), (300, 420)),
        manager=ui_manager
    )
    
    # Заголовок
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 10), (280, 40)),
        text="УПРАВЛЕНИЕ СОЛНЕЧНОЙ СИСТЕМОЙ",
        manager=ui_manager,
        container=control_panel
    )
    
    # Скорость времени
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 60), (120, 30)),
        text="Скорость времени:",
        manager=ui_manager,
        container=control_panel
    )
    
    time_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 90), (280, 20)),
        start_value=1.0,
        value_range=(0.1, 5.0),
        manager=ui_manager,
        container=control_panel
    )
    
    time_value_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 60), (70, 30)),
        text="1.00x",
        manager=ui_manager,
        container=control_panel
    )
    
    # Масштаб
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 125), (100, 30)),
        text="Масштаб:",
        manager=ui_manager,
        container=control_panel
    )
    
    zoom_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 155), (280, 20)),
        start_value=1.0,
        value_range=(0.3, 3.0),
        manager=ui_manager,
        container=control_panel
    )
    
    zoom_value_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((220, 125), (70, 30)),
        text="1.00x",
        manager=ui_manager,
        container=control_panel
    )
    
    # Кнопки
    reset_camera_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 195), (280, 35)),
        text="Сбросить камеру",
        manager=ui_manager,
        container=control_panel
    )
    
    pause_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 240), (135, 35)),
        text="Пауза",
        manager=ui_manager,
        container=control_panel
    )
    
    trails_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((155, 240), (135, 35)),
        text=f"Траектории: {'Вкл' if settings.show_trails else 'Выкл'}",
        manager=ui_manager,
        container=control_panel
    )
    
    orbits_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 285), (135, 35)),
        text=f"Орбиты: {'Вкл' if settings.show_orbits else 'Выкл'}",
        manager=ui_manager,
        container=control_panel
    )
    
    labels_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((155, 285), (135, 35)),
        text=f"Подписи: {'Вкл' if settings.show_labels else 'Выкл'}",
        manager=ui_manager,
        container=control_panel
    )
    
    # Панель информации о планете
    planet_info = PlanetInfoPanel(ui_manager, WIDTH - 350, 10, 340, 500)
    
    # Панель статистики
    stats_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((WIDTH - 350, HEIGHT - 100), (340, 90)),
        manager=ui_manager
    )
    
    stats_text = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 10), (320, 70)),
        text="",
        manager=ui_manager,
        container=stats_panel
    )
    
    # Переменные состояния
    selected_planet = None
    hovered_planet = None
    paused = False
    time_multiplier = 1.0
    current_width, current_height = WIDTH, HEIGHT
    show_fps = False
    
    font = pygame.font.Font(None, 20)
    title_font = pygame.font.Font(None, 36)
    
    # Флаг для отслеживания наведения на UI
    mouse_over_ui = False
    
    running = True
    while running:
        time_delta = clock.tick(FPS) / 1000.0
        
        # Обновление звезд
        for star in stars:
            star.update()
        
        # Получаем позицию мыши
        mouse_pos = pygame.mouse.get_pos()
        
        # Проверяем, находится ли мышь над UI панелями
        mouse_over_ui = False
        
        # Проверяем все UI элементы на наличие ховера
        # Получаем все виджеты из менеджера
        for widget in ui_manager.get_root_container().get_container().elements:
            if hasattr(widget, 'relative_rect'):
                # Получаем абсолютную позицию виджета
                widget_rect = widget.get_relative_rect()
                # Простая проверка - если мышь внутри области виджета
                if widget_rect.collidepoint(mouse_pos):
                    mouse_over_ui = True
                    break
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == QUIT:
                settings.save()
                running = False
            
            elif event.type == VIDEORESIZE:
                current_width, current_height = event.w, event.h
                screen = pygame.display.set_mode((current_width, current_height), RESIZABLE)
                ui_manager.set_window_resolution((current_width, current_height))
                planet_info.set_position(current_width - 350, 10)
                stats_panel.set_relative_position((current_width - 350, current_height - 100))
            
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == reset_camera_btn:
                    camera.reset()
                    zoom_slider.set_current_value(camera.zoom)
                elif event.ui_element == pause_btn:
                    paused = not paused
                    pause_btn.set_text("Запуск" if paused else "Пауза")
                elif event.ui_element == trails_btn:
                    settings.show_trails = not settings.show_trails
                    trails_btn.set_text(f"Траектории: {'Вкл' if settings.show_trails else 'Выкл'}")
                elif event.ui_element == orbits_btn:
                    settings.show_orbits = not settings.show_orbits
                    orbits_btn.set_text(f"Орбиты: {'Вкл' if settings.show_orbits else 'Выкл'}")
                elif event.ui_element == labels_btn:
                    settings.show_labels = not settings.show_labels
                    labels_btn.set_text(f"Подписи: {'Вкл' if settings.show_labels else 'Выкл'}")
            
            elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == time_slider:
                    time_multiplier = event.value
                    time_value_label.set_text(f"{time_multiplier:.2f}x")
                elif event.ui_element == zoom_slider:
                    camera.zoom = event.value
                    zoom_value_label.set_text(f"{camera.zoom:.2f}x")
            
            elif event.type == MOUSEBUTTONDOWN:
                # Проверяем, был ли клик по UI элементу
                if mouse_over_ui:
                    # Если клик по UI, не обрабатываем клик по планете
                    pass
                else:
                    if event.button == 4:  # Колесо вверх
                        camera.zoom_in()
                        zoom_slider.set_current_value(camera.zoom)
                    elif event.button == 5:  # Колесо вниз
                        camera.zoom_out()
                        zoom_slider.set_current_value(camera.zoom)
                    elif event.button == 1:  # Левая кнопка мыши
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        center_x, center_y = current_width // 2, current_height // 2
                        
                        # Проверка клика по планете
                        clicked_planet = None
                        for planet in planets:
                            pos = planet.get_position(center_x, center_y, camera.zoom, camera.offset_x, camera.offset_y)
                            planet_size = int(planet.size * camera.zoom)
                            dx = mouse_x - pos[0]
                            dy = mouse_y - pos[1]
                            if math.sqrt(dx*dx + dy*dy) <= planet_size:
                                clicked_planet = planet
                                break
                        
                        if clicked_planet:
                            # Если кликнули по планете, обновляем информацию
                            selected_planet = clicked_planet
                            planet_info.update_info(clicked_planet)
                        else:
                            # Если кликнули в пустоту, не сбрасываем выделение
                            # Информация остается о последней выбранной планете
                            pass
            
            elif event.type == KEYDOWN:
                if event.key == K_f:
                    show_fps = not show_fps
                elif event.key == K_SPACE:
                    paused = not paused
                    pause_btn.set_text("Запуск" if paused else "Пауза")
                elif event.key == K_r:
                    camera.reset()
                    zoom_slider.set_current_value(camera.zoom)
                elif event.key == K_g:
                    settings.show_grid = not settings.show_grid
                elif event.key == K_t:
                    settings.show_trails = not settings.show_trails
                    trails_btn.set_text(f"Траектории: {'Вкл' if settings.show_trails else 'Выкл'}")
                elif event.key == K_ESCAPE:
                    # Очистить выделение
                    selected_planet = None
                    planet_info.update_info(None)
            
            # Обработка событий камеры (с флагом UI)
            camera.handle_event(event, mouse_over_ui)
            
            # Обработка событий UI
            ui_manager.process_events(event)
        
        # Управление с клавиатуры
        keys = pygame.key.get_pressed()
        camera.handle_keys(keys)
        
        # Обновление планет
        if not paused:
            for planet in planets:
                planet.update(time_multiplier)
        
        # Рисование
        screen.fill(BG_COLOR)
        
        # Рисование звезд
        for star in stars:
            star_color = (star.brightness, star.brightness, star.brightness)
            pygame.draw.circle(screen, star_color, (star.x, star.y), 1)
        
        center_x, center_y = current_width // 2, current_height // 2
        
        # Рисование сетки
        if settings.show_grid:
            grid_color = (30, 30, 50)
            for x in range(0, current_width, 50):
                pygame.draw.line(screen, grid_color, (x, 0), (x, current_height), 1)
            for y in range(0, current_height, 50):
                pygame.draw.line(screen, grid_color, (0, y), (current_width, y), 1)
        
        # Рисование орбит
        if settings.show_orbits:
            for planet in planets:
                a = planet.distance * camera.zoom
                e = planet.eccentricity
                b = a * math.sqrt(1 - e**2)
                ellipse_rect = pygame.Rect(
                    center_x + camera.offset_x - a,
                    center_y + camera.offset_y - b,
                    a * 2,
                    b * 2
                )
                pygame.draw.ellipse(screen, (60, 60, 90), ellipse_rect, 1)
        
        # Солнце
        sun_radius = int(25 * camera.zoom)
        sun_pos = (center_x + int(camera.offset_x), center_y + int(camera.offset_y))
        
        for i in range(5, 0, -1):
            alpha = 30 // i
            glow_radius = sun_radius + i * 3
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*SUN_COLOR, alpha), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (sun_pos[0] - glow_radius, sun_pos[1] - glow_radius))
        
        pygame.draw.circle(screen, SUN_COLOR, sun_pos, sun_radius)
        
        # Планеты
        hovered_planet = None
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if settings.show_trails:
            for planet in planets:
                pos = planet.get_position(center_x, center_y, camera.zoom, camera.offset_x, camera.offset_y)
                planet.add_trail(pos)
                planet.draw_trail(screen)
        
        for planet in planets:
            pos = planet.get_position(center_x, center_y, camera.zoom, camera.offset_x, camera.offset_y)
            planet_size = int(planet.size * camera.zoom)
            
            dx = mouse_x - pos[0]
            dy = mouse_y - pos[1]
            if math.sqrt(dx*dx + dy*dy) <= planet_size + 3:
                hovered_planet = planet
                pygame.draw.circle(screen, (255, 255, 200), pos, planet_size + 4, 2)
            
            pygame.draw.circle(screen, planet.color, pos, planet_size)
            
            if planet.name == "Сатурн" and camera.zoom > 0.4:
                ring_radius = int(planet.size * camera.zoom * 1.8)
                ring_inner = int(planet.size * camera.zoom * 1.3)
                pygame.draw.ellipse(screen, (180, 150, 100), 
                                   (pos[0] - ring_radius, pos[1] - ring_radius // 2,
                                    ring_radius * 2, ring_radius), 3)
                pygame.draw.ellipse(screen, (140, 110, 70), 
                                   (pos[0] - ring_inner, pos[1] - ring_inner // 2,
                                    ring_inner * 2, ring_inner), 2)
            
            if settings.show_labels and camera.zoom > 0.5:
                text = font.render(planet.name, True, (200, 200, 200))
                screen.blit(text, (pos[0] - text.get_width() // 2, pos[1] + planet_size + 5))
        
        # Отображение наведения
        if hovered_planet and not mouse_over_ui:
            hint_text = font.render(f"Нажмите для информации о {hovered_planet.name}", True, (255, 255, 150))
            screen.blit(hint_text, (current_width // 2 - hint_text.get_width() // 2, current_height - 60))
        
        # Заголовок
        title = title_font.render("СОЛНЕЧНАЯ СИСТЕМА", True, (255, 255, 200))
        screen.blit(title, (current_width // 2 - title.get_width() // 2, 10))
        
        # Подсказки
        y_offset = current_height - 90
        hints = [
            "Перетащите мышью - панорамирование | Колесико - масштаб",
            "Пробел - пауза | R - сброс камеры | ESC - очистить выделение | F - FPS | T - треки | G - сетка"
        ]
        for hint in hints:
            hint_surface = font.render(hint, True, (150, 150, 180))
            screen.blit(hint_surface, (current_width // 2 - hint_surface.get_width() // 2, y_offset))
            y_offset += 22
        
        # Отображение FPS
        if show_fps:
            fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (100, 255, 100))
            screen.blit(fps_text, (current_width - 80, 20))
        
        # Обновление статистики
        stats_text.set_text(f"Скорость: {time_multiplier:.1f}x | Масштаб: {camera.zoom:.1f}x | "
                           f"Планет: {len(planets)} | {'Пауза' if paused else 'Игра'}")
        
        # UI
        ui_manager.update(time_delta)
        ui_manager.draw_ui(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    import random
    main()