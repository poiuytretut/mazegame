# main2.py - добавим функцию создания дампа
import os
import sys
import math
import time
import msvcrt  # Для Windows input
import traceback  # Для сохранения ошибок

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
        
    def clear_console(self):
        """Очищает консоль"""
        clear()
    
    def save_console_output(self, text):
        """Сохраняет вывод консоли для дампа"""
        self.console_output.append(text)
    
    def create_dump_file(self, error_info=None):
        """Создает файл дампа с содержимым консоли"""
        try:
            with open(DUMP_FILENAME, 'w', encoding='utf-8') as f:
                f.write("=== ДАМП ИГРЫ ЛАБИРИНТ ===\n")
                f.write(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Статус: {'ПОБЕДА' if self.game_won else 'В ПРОЦЕССЕ'}\n")
                
                if error_info:
                    f.write(f"Ошибка: {error_info}\n")
                
                f.write("\n=== ПОСЛЕДНИЙ ВЫВОД КОНСОЛИ ===\n")
                
                # Сохраняем последние 100 строк вывода
                for line in self.console_output[-100:]:
                    f.write(line + '\n')
                
                # Добавляем информацию о игроке и лабиринте
                if self.player:
                    f.write(f"\n=== ИНФОРМАЦИЯ О ИГРОКЕ ===\n")
                    f.write(f"Позиция: ({self.player.x:.2f}, {self.player.y:.2f})\n")
                    f.write(f"Угол: {math.degrees(self.player.angle):.1f}°\n")
                    f.write(f"Нашел выход: {self.game_won}\n")
                
                if hasattr(self, 'maze_generator') and self.maze_generator.get_maze():
                    f.write(f"\n=== МИНИ-КАРТА ===\n")
                    minimap = self.raycaster.render_minimap(self.player, self.maze_generator.get_maze())
                    f.write(minimap)
                
                f.write(f"\n=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===\n")
                f.write(f"Размер лабиринта: {MAP_WIDTH}x{MAP_HEIGHT}\n")
                f.write(f"FOV: {math.degrees(FOV):.1f}°\n")
                f.write(f"Макс. дистанция рендера: {MAX_RENDER_DISTANCE}\n")
                
            print(f"\nДамп игры сохранен в файл: {DUMP_FILENAME}")
        except Exception as e:
            print(f"Ошибка при создании дампа: {e}")
    
    def setup_game(self):
        """Инициализация игры"""
        self.clear_console()
        self.console_output = []  # Очищаем историю вывода
        print("Генерация лабиринта...")
        self.save_console_output("Генерация лабиринта...")
        
        if not self.maze_generator.generate_maze():
            error_msg = "Ошибка: не удалось сгенерировать проходимый лабиринт!"
            print(error_msg)
            self.save_console_output(error_msg)
            self.create_dump_file(error_msg)
            return False
        
        maze = self.maze_generator.get_maze()
        
        # Находим стартовую позицию игрока
        start_x, start_y = 0, 0
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == PLAYER_START_SYMBOL:
                    start_x = x + 0.5
                    start_y = y + 0.5
                    break
        
        self.player = Player(start_x, start_y)
        self.running = True
        self.game_won = False
        
        success_msg = "Лабиринт сгенерирован успешно! Игра началась."
        print(success_msg)
        self.save_console_output(success_msg)
        return True
    
    def handle_input(self):
        """Обработка пользовательского ввода для Windows"""
        try:
            # Неблокирующая проверка нажатия клавиши
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                maze = self.maze_generator.get_maze()
                
                # Обработка клавиш управления
                if key == 'w':
                    self.player.move_forward(maze)
                elif key == 's':
                    self.player.move_backward(maze)
                elif key == 'a':
                    self.player.rotate_left()
                elif key == 'd':
                    self.player.rotate_right()
                elif key == 'q':
                    self.running = False
                    print("Выход из игры...")
                    self.save_console_output("Выход из игры...")
                elif key == 'e':
                    self.player.strafe_right(maze)
                elif key == 'z':
                    self.player.strafe_left(maze)
                elif key == 'r':  # Рестарт игры
                    print("Рестарт игры...")
                    self.save_console_output("Рестарт игры...")
                    return self.setup_game()
                elif key == 'l':  # Сохранение дампа по команде
                    print("Создание дампа игры...")
                    self.save_console_output("Создание дампа игры...")
                    self.create_dump_file()
                    
        except Exception as e:
            # Игнорируем ошибки декодирования (специальные клавиши)
            pass
    
    def render_ui(self):
        """Рендерит интерфейс пользователя"""
        ui = "\n" + "=" * CONSOLE_WIDTH + "\n"
        ui += "ЛАБИРИНТ | Управление: W/S - вперед/назад, A/D - поворот, Q - выход\n"
        ui += "E/Z - стрейф, R - рестарт, L - сохранить дамп игры\n"
        ui += f"Позиция: ({self.player.x:.1f}, {self.player.y:.1f}) | "
        ui += f"Угол: {math.degrees(self.player.angle):.1f}°\n"
        
        if self.player.check_exit(self.maze_generator.get_maze()):
            ui += "*** ВЫ НАШЛИ ВЫХОД! Нажмите R для рестарта ***\n"
            self.game_won = True
        
        ui += "=" * CONSOLE_WIDTH + "\n"
        return ui
    
    def run(self):
        """Главный игровой цикл"""
        if not self.setup_game():
            return
        
        frame_count = 0
        try:
            while self.running:
                frame_count += 1
                
                # Обработка ввода
                self.handle_input()
                
                # Проверка победы
                if self.player.check_exit(self.maze_generator.get_maze()):
                    self.game_won = True
                
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
                
                # Мини-карта
                minimap = self.raycaster.render_minimap(
                    self.player, 
                    self.maze_generator.get_maze()
                )
                print("Мини-карта:")
                print(minimap)
                self.save_console_output("Мини-карта:")
                self.save_console_output(minimap)
                
                # Отладочная информация
                debug_info = f"Кадр: {frame_count}"
                print(debug_info)
                self.save_console_output(debug_info)
                
                # Задержка между кадрами 0.05 секунды
                time.sleep(0.05)
                
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
            if os.path.exists(DUMP_FILENAME):
                print(f"Дамп игры сохранен в: {DUMP_FILENAME}")

if __name__ == "__main__":
    game = MazeGame()
    game.run()