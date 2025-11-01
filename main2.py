# main2.py - с полностью переработанным демо-режимом
import os
import sys
import math
import time
import msvcrt  # Для Windows input
import traceback  # Для сохранения ошибок
import random

from maze_generator import MazeGenerator
from player import Player
from raycasting import RayCaster
from config import *

class MazeGame:
    def __init__(self):
        self.maze_generator = MazeGenerator()
        self.player = None
        self.raycaster = RayCaster(CONSOLE_WIDTH, CONSOLE_HEIGHT)
        self.running = False
        self.game_won = False
        self.console_output = []  # Храним вывод консоли
        self.show_interface = True  # Флаг отображения интерфейса
        self.pressed_keys = set()  # Множество нажатых клавиш
        self.difficulty = "легкая"  # Сложность по умолчанию
        self._last_i_state = False  # Исправлено: инициализируем здесь
        self.demo_mode = False  # Режим демо
        self.demo_path = []  # Путь для демо-режима
        self.demo_actions = []  # Последовательность действий для демо-режима
        self.demo_action_index = 0  # Текущий индекс действия
        self.demo_state = "finding_path"  # Состояние демо: finding_path, moving, rotating, completed
        
    def select_difficulty(self):
        """Выбор сложности игры"""
        self.clear_console()
        print("=== ВЫБОР СЛОЖНОСТИ ЛАБИРИНТА ===")
        print()
        
        difficulties = list(DIFFICULTIES.keys())
        for i, diff in enumerate(difficulties, 1):
            size = DIFFICULTIES[diff]
            print(f"{i}. {diff.capitalize()} - {size['width']}x{size['height']} (комнаты: {size['room_size']}x{size['room_size']})")
        
        print()
        print("Выберите сложность (1-5) или нажмите Enter для стандартной (легкая):")
        
        while True:
            try:
                choice = input().strip()
                if not choice:  # Enter - стандартная сложность
                    self.difficulty = "легкая"
                    break
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(difficulties):
                    self.difficulty = difficulties[choice_num - 1]
                    break
                else:
                    print(f"Пожалуйста, введите число от 1 до {len(difficulties)}:")
            except ValueError:
                print("Пожалуйста, введите число:")
        
        # Обновляем глобальные константы размера карты и комнат
        global MAP_WIDTH, MAP_HEIGHT, ROOM_SIZE
        MAP_WIDTH = DIFFICULTIES[self.difficulty]["width"]
        MAP_HEIGHT = DIFFICULTIES[self.difficulty]["height"]
        ROOM_SIZE = DIFFICULTIES[self.difficulty]["room_size"]
        
        # Пересоздаем генератор лабиринта с новыми размерами
        self.maze_generator = MazeGenerator()
        
        print(f"Выбрана сложность: {self.difficulty.capitalize()}")
        print(f"Размер лабиринта: {MAP_WIDTH}x{MAP_HEIGHT}")
        print(f"Размер комнат: {ROOM_SIZE}x{ROOM_SIZE}")
        print("Нажмите любую клавишу для продолжения...")
        input()
    
    def clear_console(self):
        """Очищает консоль"""
        clear()
    
    def save_console_output(self, text):
        """Сохраняет вывод консоли для дампа"""
        self.console_output.append(text)
    
    def create_dump_file(self, error_info=None):
        """Создает файл дампа с содержимым консоли и полной картой"""
        try:
            with open(DUMP_FILENAME, 'w', encoding='utf-8') as f:
                f.write("=== ДАМП ИГРЫ ЛАБИРИНТ ===\n")
                f.write(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Сложность: {self.difficulty.capitalize()}\n")
                f.write(f"Ожидаемый размер: {MAP_WIDTH}x{MAP_HEIGHT}\n")
                f.write(f"Размер комнат: {ROOM_SIZE}x{ROOM_SIZE}\n")
                f.write(f"Статус: {'ПОБЕДА' if self.game_won else 'В ПРОЦЕССЕ'}\n")
                f.write(f"Режим: {'ДЕМО' if self.demo_mode else 'НОРМАЛЬНЫЙ'}\n")
            
                if error_info:
                    f.write(f"Ошибка: {error_info}\n")
            
                # ДОБАВЛЯЕМ ИНФОРМАЦИЮ О ФАКТИЧЕСКОМ РАЗМЕРЕ
                if hasattr(self, 'maze_generator') and self.maze_generator.get_maze():
                    actual_maze = self.maze_generator.get_maze()
                    actual_width = len(actual_maze[0])
                    actual_height = len(actual_maze)
                    f.write(f"Фактический размер: {actual_width}x{actual_height}\n")
            
                f.write("\n=== ПОСЛЕДНИЙ ВЫВОД КОНСОЛИ ===\n")
            
                # Сохраняем последние 100 строк вывода
                for line in self.console_output[-100:]:
                    f.write(line + '\n')

                # Добавляем информацию о игроке и лабиринте (с проверкой на None)
                f.write(f"\n=== ИНФОРМАЦИЯ О ИГРОКЕ ===\n")
                if self.player is not None:
                    f.write(f"Позиция: ({self.player.x:.2f}, {self.player.y:.2f})\n")
                    f.write(f"Угол: {self.player.get_angle_degrees():.1f}°\n")
                    f.write(f"Нашел выход: {self.game_won}\n")
                else:
                    f.write("Игрок не инициализирован\n")
            
                if hasattr(self, 'maze_generator') and self.maze_generator.get_maze():
                    f.write(f"\n=== МИНИ-КАРТА ===\n")
                    if self.player is not None:
                        minimap = self.raycaster.render_minimap(self.player, self.maze_generator.get_maze())
                        f.write(minimap)
                    else:
                        f.write("Игрок не инициализирован, мини-карта недоступна\n")
                
                    # ДОБАВЛЯЕМ ПОЛНУЮ КАРТУ БЕЗ СЖАТИЯ
                    f.write(f"\n=== ПОЛНАЯ КАРТА ЛАБИРИНТА ===\n")
                    actual_maze = self.maze_generator.get_maze()
                    actual_width = len(actual_maze[0])
                    actual_height = len(actual_maze)
                    f.write(f"Фактический размер: {actual_width}x{actual_height}\n")
                    f.write(f"Ожидаемый размер: {MAP_WIDTH}x{MAP_HEIGHT}\n")
                
                    # ВСЕГДА показываем полную карту без сжатия
                    full_map = self.maze_generator.get_maze_string()
                    f.write(full_map)
            
                f.write(f"\n=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===\n")
                f.write(f"Ожидаемый размер: {MAP_WIDTH}x{MAP_HEIGHT}\n")
                f.write(f"FOV: {math.degrees(FOV):.1f}°\n")
                f.write(f"Макс. дистанция рендера: {MAX_RENDER_DISTANCE}\n")
            
            print(f"\nДамп игры сохранен в файл: {DUMP_FILENAME}")
        except Exception as e:
            print(f"Ошибка при создании дампа: {e}")
    
    def setup_game(self):
        """Инициализация игры"""
        self.clear_console()
        self.console_output = []
        self.show_interface = True
        self.pressed_keys = set()
        self._last_i_state = False
        self.demo_mode = '-demo' in sys.argv  # Проверяем аргумент командной строки
    
        print(f"Сложность: {self.difficulty.capitalize()}")
        print(f"Размер лабиринта: {MAP_WIDTH}x{MAP_HEIGHT}")
        print(f"Размер комнат: {ROOM_SIZE}x{ROOM_SIZE}")
        if self.demo_mode:
            print("РЕЖИМ ДЕМО: игра будет проходить автоматически")
        print("Генерация лабиринта...")
    
        try:
            # ПЕРЕСОЗДАЕМ генератор с ПРАВИЛЬНЫМИ размерами
            self.maze_generator = MazeGenerator(MAP_WIDTH, MAP_HEIGHT, ROOM_SIZE)
        
            if not self.maze_generator.generate_maze():
                error_msg = "Ошибка: не удалось сгенерировать проходимый лабиринт!"
                print(error_msg)
                self.save_console_output(error_msg)
                self.create_dump_file(error_msg)
                return False
        
            maze = self.maze_generator.get_maze()
        
            # Проверка размеров
            actual_width = len(maze[0])
            actual_height = len(maze)
            print(f"Фактический размер лабиринта: {actual_width}x{actual_height}")
        
            if actual_width != MAP_WIDTH or actual_height != MAP_HEIGHT:
                error_msg = f"ОШИБКА: Размер лабиринта {actual_width}x{actual_height} не соответствует ожидаемому {MAP_WIDTH}x{MAP_HEIGHT}!"
                print(error_msg)
                return False
        
            # Находим стартовую позицию
            start_x, start_y = 0, 0
            for y in range(min(100, len(maze))):
                for x in range(min(100, len(maze[0]))):
                    if maze[y][x] == PLAYER_START_SYMBOL:
                        start_x = x + 0.5
                        start_y = y + 0.5
                        break
        
            self.player = Player(start_x, start_y)
            self.running = True
            self.game_won = False
            
            # Инициализация демо-режима
            if self.demo_mode:
                self.demo_path = []
                self.demo_actions = []
                self.demo_action_index = 0
                self.demo_state = "finding_path"
                print("Поиск кратчайшего пути...")
                self._find_shortest_path()
                if self.demo_path:
                    print("Построение маршрута...")
                    self._build_demo_actions()
                    self.demo_state = "moving"
        
            success_msg = f"Лабиринт {MAP_WIDTH}x{MAP_HEIGHT} сгенерирован успешно!"
            print(success_msg)
            if self.demo_mode and self.demo_path:
                print(f"Найден путь длиной {len(self.demo_path)} шагов")
                print(f"Построено {len(self.demo_actions)} действий")
            return True
        
        except MemoryError:
            error_msg = "ОШИБКА ПАМЯТИ: Слишком большой лабиринт! Попробуйте меньшую сложность."
            print(error_msg)
            return False
        except Exception as e:
            error_msg = f"Ошибка при инициализации игры: {e}"
            print(error_msg)
            return False
    
    def _find_shortest_path(self):
        """Находит кратчайший путь от старта до выхода (алгоритм BFS)"""
        maze = self.maze_generator.get_maze()
        
        # Находим стартовую позицию и выход
        start_pos = None
        exit_pos = None
        
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == PLAYER_START_SYMBOL:
                    start_pos = (x, y)
                elif maze[y][x] == EXIT_SYMBOL:
                    exit_pos = (x, y)
        
        if not start_pos or not exit_pos:
            print("Ошибка: не найдена стартовая позиция или выход!")
            return
        
        # BFS для поиска кратчайшего пути
        queue = [(start_pos, [start_pos])]
        visited = set([start_pos])
        
        while queue:
            (x, y), path = queue.pop(0)
            
            # Проверяем, достигли ли выхода
            if (x, y) == exit_pos:
                self.demo_path = path
                return
            
            # Проверяем соседние клетки
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and
                    (nx, ny) not in visited and
                    maze[ny][nx] in (EMPTY_SYMBOL, EXIT_SYMBOL, PLAYER_START_SYMBOL)):
                    
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        
        print("Ошибка: путь до выхода не найден!")
        self.demo_path = []
    
    def _calculate_angle_to_target(self, current_pos, target_pos):
        """Вычисляет угол для поворота к целевой позиции"""
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        if dx == 1 and dy == 0:  # Вправо
            return 0
        elif dx == -1 and dy == 0:  # Влево
            return math.pi
        elif dx == 0 and dy == 1:  # Вниз
            return math.pi / 2
        elif dx == 0 and dy == -1:  # Вверх
            return 3 * math.pi / 2
        else:
            # Для диагональных движений (на всякий случай)
            return math.atan2(dy, dx)
    
    def _build_demo_actions(self):
        """Строит последовательность действий для демо-режима"""
        if not self.demo_path:
            return
        
        self.demo_actions = []
        current_angle = self.player.angle
        
        for i in range(len(self.demo_path) - 1):
            current_pos = self.demo_path[i]
            next_pos = self.demo_path[i + 1]
            
            # Вычисляем целевой угол
            target_angle = self._calculate_angle_to_target(current_pos, next_pos)
            
            # Добавляем действие поворота, если нужно
            if abs(target_angle - current_angle) > 0.01:
                self.demo_actions.append(('rotate', target_angle))
                current_angle = target_angle
            
            # Добавляем действие движения
            target_x = next_pos[0] + 0.5
            target_y = next_pos[1] + 0.5
            self.demo_actions.append(('move', target_x, target_y))
    
    def _demo_update(self):
        """Обновляет демо-режим"""
        if self.demo_state == "completed":
            return
        
        # Если игрок движется или поворачивается, обновляем движение
        if self.player.is_moving or self.player.is_rotating:
            self.player.update_demo_movement()
            return
        
        # Если текущее действие завершено, переходим к следующему
        if self.demo_action_index >= len(self.demo_actions):
            self.demo_state = "completed"
            return
        
        # Выполняем следующее действие
        action = self.demo_actions[self.demo_action_index]
        
        if action[0] == 'rotate':
            self.player.set_target_angle(action[1])
        elif action[0] == 'move':
            self.player.set_target_position(action[1], action[2])
        
        self.demo_action_index += 1
    
    def handle_input(self):
        """Обработка пользовательского ввода для Windows"""
        # В демо-режиме игрок управляется автоматически
        if self.demo_mode:
            self._demo_update()
            return
            
        try:
            # Временное множество для новых нажатий в этом кадре
            new_presses = set()
            
            # Собираем все нажатые клавиши в этом кадре
            while msvcrt.kbhit():
                try:
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key in ['w', 'a', 's', 'd', 'z', 'c', 'q', 'r', 'l', 'i']:
                        new_presses.add(key)
                except:
                    pass  # Игнорируем специальные клавиши
            
            # Обновляем множество нажатых клавиш
            # Клавиши остаются нажатыми, только если они были нажаты в этом кадре
            self.pressed_keys = new_presses
            
            # Обработка специальных клавиш (не для движения)
            maze = self.maze_generator.get_maze()
            
            if 'q' in self.pressed_keys:
                self.running = False
                print("Выход из игры...")
                self.save_console_output("Выход из игры...")
                return
            
            if 'r' in self.pressed_keys:
                print("Рестарт игры...")
                self.save_console_output("Рестарт игры...")
                self.setup_game()
                return
            
            if 'l' in self.pressed_keys:
                print("Создание дампа игры...")
                self.save_console_output("Создание дампа игры...")
                self.create_dump_file()
                # Не удаляем 'l', чтобы можно было удерживать для многократного сохранения
            
            # ИСПРАВЛЕННАЯ ОБРАБОТКА КНОПКИ 'I'
            if 'i' in self.pressed_keys:
                # Переключение интерфейса только при новом нажатии
                if not self._last_i_state:
                    self.show_interface = not self.show_interface
                    if self.show_interface:
                        print("Интерфейс включен")
                        self.save_console_output("Интерфейс включен")
                    else:
                        print("Интерфейс скрыт")
                        self.save_console_output("Интерфейс скрыт")
                    self._last_i_state = True
            else:
                self._last_i_state = False
            
            # Обработка одновременного движения и поворота
            move_forward = 'w' in self.pressed_keys
            move_backward = 's' in self.pressed_keys
            rotate_left = 'a' in self.pressed_keys
            rotate_right = 'd' in self.pressed_keys
            strafe_left = 'z' in self.pressed_keys
            strafe_right = 'c' in self.pressed_keys
            
            # Применяем все движения одновременно
            if move_forward:
                self.player.move_forward(maze)
            if move_backward:
                self.player.move_backward(maze)
            if rotate_left:
                self.player.rotate_left()
            if rotate_right:
                self.player.rotate_right()
            if strafe_left:
                self.player.strafe_left(maze)
            if strafe_right:
                self.player.strafe_right(maze)
                    
        except Exception as e:
            # Игнорируем ошибки декодирования (специальные клавиши)
            pass
    
    def render_ui(self):
        """Рендерит интерфейс пользователя"""
        if not self.show_interface:
            # Минималистичный интерфейс
            ui = "\n" + "=" * CONSOLE_WIDTH + "\n"
            ui += "Нажмите I для отображения интерфейса\n"
            ui += "=" * CONSOLE_WIDTH + "\n"
            return ui
        
        # Полный интерфейс
        ui = "\n" + "=" * CONSOLE_WIDTH + "\n"
        ui += f"ЛАБИРИНТ | Сложность: {self.difficulty.capitalize()} | Размер: {MAP_WIDTH}x{MAP_HEIGHT} | Комнаты: {ROOM_SIZE}x{ROOM_SIZE}\n"
        
        if self.demo_mode:
            ui += f"РЕЖИМ ДЕМО | Действие: {self.demo_action_index}/{len(self.demo_actions)} | Состояние: {self.demo_state}\n"
        else:
            ui += "Управление: W/S - вперед/назад, A/D - поворот\n"
            ui += "Z/C - стрейф влево/вправо, Q - выход, I - интерфейс\n"
            ui += "R - рестарт, L - сохранить дамп игры\n"
        
        ui += f"Позиция: ({self.player.x:.1f}, {self.player.y:.1f}) | "
        ui += f"Угол: {self.player.get_angle_degrees():.1f}°\n"
        
        # Показываем активные клавиши (только в обычном режиме)
        if not self.demo_mode and self.pressed_keys:
            active_keys = ', '.join(self.pressed_keys).upper()
            ui += f"Активные клавиши: {active_keys}\n"
        
        if self.player.check_exit(self.maze_generator.get_maze()):
            if self.demo_mode:
                ui += "*** ДЕМО ЗАВЕРШЕНО! Лабиринт пройден ***\n"
            else:
                ui += "*** ВЫ НАШЛИ ВЫХОД! Нажмите R для рестарта ***\n"
            self.game_won = True
        
        ui += "=" * CONSOLE_WIDTH + "\n"
        return ui
    
    def run(self):
        """Главный игровой цикл"""
        # Проверяем аргументы командной строки
        if '-demo' in sys.argv:
            self.demo_mode = True
            print("Запуск в режиме ДЕМО...")
        
        # Выбор сложности перед началом игры
        self.select_difficulty()
        
        if not self.setup_game():
            return
        
        frame_count = 0
        try:
            while self.running:
                frame_count += 1
                
                # Обработка ввода
                self.handle_input()
                
                if not self.running:
                    break
                
                # Проверка победы
                if self.player.check_exit(self.maze_generator.get_maze()):
                    self.game_won = True
                    if self.demo_mode:
                        self.demo_state = "completed"
                
                # Очистка консоли и рендеринг
                self.clear_console()
                
                # Raycasting рендер
                frame = self.raycaster.render_frame(
                    self.player, 
                    self.maze_generator.get_maze()
                )
                print(frame)
                self.save_console_output(frame)
                
                # UI
                ui_text = self.render_ui()
                print(ui_text)
                self.save_console_output(ui_text)
                
                # Мини-карта (показываем только при включенном интерфейсе)
                if self.show_interface:
                    minimap = self.raycaster.render_minimap(
                        self.player, 
                        self.maze_generator.get_maze()
                    )
                    print("Мини-карта:")
                    print(minimap)
                    self.save_console_output("Мини-карта:")
                    self.save_console_output(minimap)
                
                # Отладочная информация (только при включенном интерфейсе)
                if self.show_interface:
                    debug_info = f"Кадр: {frame_count}"
                    if self.demo_mode:
                        debug_info += f" | Действие: {self.demo_action_index}/{len(self.demo_actions)}"
                        if self.player.is_moving:
                            debug_info += " | ДВИЖЕНИЕ"
                        elif self.player.is_rotating:
                            debug_info += " | ПОВОРОТ"
                    print(debug_info)
                    self.save_console_output(debug_info)
                
                # Задержка между кадрами для плавности
                time.sleep(0.03)  # Немного увеличили задержку для лучшей видимости демо
                
        except KeyboardInterrupt:
            print("\nИгра прервана пользователем")
            self.save_console_output("Игра прервана пользователем")
            self.create_dump_file("KeyboardInterrupt")
        except Exception as e:
            error_msg = f"\nПроизошла ошибка: {e}"
            print(error_msg)
            self.save_console_output(error_msg)
            # Сохраняем traceback для дампа
            tb = traceback.format_exc()
            self.create_dump_file(f"{error_msg}\n{tb}")
        finally:
            # Автоматически создаем дамп при завершении игры
            if not self.game_won:
                self.create_dump_file("Игра завершена")
            
            self.clear_console()
            print("Игра завершена")
            if self.demo_mode and self.game_won:
                print(f"Демо-режим: лабиринт успешно пройден за {len(self.demo_path)} шагов!")
            if os.path.exists(DUMP_FILENAME):
                print(f"Дамп игры сохранен в: {DUMP_FILENAME}")

if __name__ == "__main__":
    game = MazeGame()
    game.run()