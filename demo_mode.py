# demo_mode.py - отдельный демо-режим
import os
import sys
import time
import traceback
from maze_generator import MazeGenerator
from demo_player import DemoPlayer
from raycasting import RayCaster
from config import *

class DemoGame:
    def __init__(self):
        self.maze_generator = MazeGenerator()
        self.player = None
        self.raycaster = RayCaster(CONSOLE_WIDTH, CONSOLE_HEIGHT)
        self.running = False
        self.game_won = False
        self.difficulty = "нормальная"
        
    def select_difficulty(self):
        """Выбор сложности"""
        self.clear_console()
        print("=== ДЕМО-РЕЖИМ: ВЫБОР СЛОЖНОСТИ ===")
        print()
        
        difficulties = list(DIFFICULTIES.keys())
        for i, diff in enumerate(difficulties, 1):
            size = DIFFICULTIES[diff]
            print(f"{i}. {diff.capitalize()} - {size['width']}x{size['height']}")
        
        print()
        print("Выберите сложность (1-5) или нажмите Enter для нормальной:")
        
        while True:
            try:
                choice = input().strip()
                if not choice:
                    self.difficulty = "нормальная"
                    break
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(difficulties):
                    self.difficulty = difficulties[choice_num - 1]
                    break
                else:
                    print(f"Пожалуйста, введите число от 1 до {len(difficulties)}:")
            except ValueError:
                print("Пожалуйста, введите число:")
        
        global MAP_WIDTH, MAP_HEIGHT, ROOM_SIZE
        MAP_WIDTH = DIFFICULTIES[self.difficulty]["width"]
        MAP_HEIGHT = DIFFICULTIES[self.difficulty]["height"]
        ROOM_SIZE = DIFFICULTIES[self.difficulty]["room_size"]
        
        print(f"Выбрана сложность: {self.difficulty.capitalize()}")
        print(f"Размер лабиринта: {MAP_WIDTH}x{MAP_HEIGHT}")
        print("Нажмите любую клавишу для начала демо...")
        input()
    
    def clear_console(self):
        """Очищает консоль"""
        clear()
    
    def setup_game(self):
        """Инициализация игры"""
        self.clear_console()
        print(f"ДЕМО-РЕЖИМ | Сложность: {self.difficulty.capitalize()}")
        print(f"Генерация лабиринта {MAP_WIDTH}x{MAP_HEIGHT}...")
        
        try:
            self.maze_generator = MazeGenerator(MAP_WIDTH, MAP_HEIGHT, ROOM_SIZE)
            
            if not self.maze_generator.generate_maze():
                print("Ошибка: не удалось сгенерировать лабиринт!")
                return False
            
            maze = self.maze_generator.get_maze()
            
            # Находим стартовую позицию
            start_x, start_y = 0, 0
            for y in range(min(100, len(maze))):
                for x in range(min(100, len(maze[0]))):
                    if maze[y][x] == PLAYER_START_SYMBOL:
                        start_x = x + 0.5
                        start_y = y + 0.5
                        break
            
            self.player = DemoPlayer(start_x, start_y)
            self.running = True
            self.game_won = False
            
            print("Лабиринт сгенерирован успешно!")
            print("Запуск автоматического прохождения...")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при инициализации: {e}")
            return False
    
    def render_ui(self):
        """Рендерит интерфейс"""
        ui = "\n" + "=" * CONSOLE_WIDTH + "\n"
        ui += f"ДЕМО-РЕЖИМ | Сложность: {self.difficulty.capitalize()} | Размер: {MAP_WIDTH}x{MAP_HEIGHT}\n"
        ui += f"Состояние: {self.player.state.upper()} | Прогресс: {self.player.get_progress()}%\n"
        ui += f"Позиция: ({self.player.x:.1f}, {self.player.y:.1f}) | Угол: {self.player.get_angle_degrees():.1f}°\n"
        ui += f"Шаг: {self.player.current_step}/{len(self.player.path)-1 if self.player.path else 0}\n"
        
        if self.game_won:
            ui += "*** ДЕМО ЗАВЕРШЕНО! ЛАБИРИНТ ПРОЙДЕН ***\n"
        
        ui += "=" * CONSOLE_WIDTH + "\n"
        return ui
    
    def run(self):
        """Главный игровой цикл"""
        print("=== ДЕМО-РЕЖИМ ЛАБИРИНТА ===")
        print("Автоматическое прохождение лабиринта")
        print()
        
        self.select_difficulty()
        
        if not self.setup_game():
            return
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                frame_count += 1
                
                # Обновляем демо-игрока
                self.player.update(self.maze_generator.get_maze())
                
                # Проверяем победу
                if self.player.check_exit(self.maze_generator.get_maze()):
                    self.game_won = True
                
                # Очищаем и рендерим
                self.clear_console()
                
                # Raycasting
                frame = self.raycaster.render_frame(self.player, self.maze_generator.get_maze())
                print(frame)
                
                # Интерфейс
                ui = self.render_ui()
                print(ui)
                
                # Мини-карта
                minimap = self.raycaster.render_minimap(self.player, self.maze_generator.get_maze())
                print("Мини-карта:")
                print(minimap)
                
                # Статистика
                elapsed_time = time.time() - start_time
                print(f"Время: {elapsed_time:.1f}с | Кадр: {frame_count}")
                
                # Завершаем демо если пройдено
                if self.game_won and self.player.state == "completed":
                    time.sleep(3)
                    break
                
                # Задержка для плавности
                time.sleep(0.03)
                
        except KeyboardInterrupt:
            print("\nДемо прервано пользователем")
        except Exception as e:
            print(f"\nОшибка в демо-режиме: {e}")
            traceback.print_exc()
        finally:
            self.clear_console()
            if self.game_won:
                total_time = time.time() - start_time
                print("=== ДЕМО ЗАВЕРШЕНО ===")
                print(f"Лабиринт пройден за {total_time:.1f} секунд")
                print(f"Пройдено шагов: {len(self.player.path) if self.player.path else 0}")
                print(f"Обработано кадров: {frame_count}")
            else:
                print("Демо прервано")
            
            print("\nНажмите любую клавишу для выхода...")
            input()

if __name__ == "__main__":
    game = DemoGame()
    game.run()