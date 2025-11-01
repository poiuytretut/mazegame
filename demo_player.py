# demo_player.py - автоматический игрок для демо-режима с предпочтением поворотов
import math
import time
from collections import deque
from config import *

class DemoPlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.move_speed = MOVE_SPEED
        self.rotation_speed = ROTATION_SPEED
        self.path = []
        self.current_step = 0
        self.state = "finding_path"  # finding_path, rotating, moving, completed
        self.last_action_time = 0
        self.action_delay = 0.05
    
    def _normalize_angle(self, angle):
        """Нормализует угол в диапазон [0, 2π]"""
        angle %= 2 * math.pi
        if angle < 0:
            angle += 2 * math.pi
        return angle
    
    def get_angle_degrees(self):
        """Возвращает угол в градусах [0, 360)"""
        degrees = math.degrees(self.angle) % 360
        if degrees < 0:
            degrees += 360
        return degrees
    
    def find_path_to_exit(self, maze):
        """Находит путь до выхода с помощью BFS"""
        print("Поиск пути до выхода...")
        
        # Находим стартовую позицию и выход
        start_pos = (int(self.x), int(self.y))
        exit_pos = None
        
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == EXIT_SYMBOL:
                    exit_pos = (x, y)
                    break
            if exit_pos:
                break
        
        if not exit_pos:
            print("Выход не найден!")
            return False
        
        print(f"Старт: {start_pos}, Выход: {exit_pos}")
        
        # BFS поиск пути
        queue = deque()
        queue.append((start_pos, []))
        visited = set([start_pos])
        
        while queue:
            (x, y), path = queue.popleft()
            
            # Проверяем, достигли ли выхода
            if (x, y) == exit_pos:
                self.path = path + [(x, y)]
                print(f"Путь найден! Длина: {len(self.path)} шагов")
                return True
            
            # Проверяем соседние клетки
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and
                    (nx, ny) not in visited and
                    maze[ny][nx] in (EMPTY_SYMBOL, EXIT_SYMBOL, PLAYER_START_SYMBOL)):
                    
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(x, y)]))
        
        print("Путь до выхода не найден!")
        return False
    
    def _get_direction_angle(self, current_pos, next_pos):
        """Определяет угол направления к следующей позиции"""
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        if dx == 1:  # Вправо
            return 0
        elif dx == -1:  # Влево
            return math.pi
        elif dy == 1:  # Вниз
            return math.pi / 2
        elif dy == -1:  # Вверх
            return 3 * math.pi / 2
        
        return self.angle  # Если направление неопределено, оставляем текущий угол
    
    def _move_towards(self, target_x, target_y):
        """Двигается к целевой позиции"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.move_speed:
            self.x = target_x
            self.y = target_y
            return True
        else:
            # Двигаемся в направлении цели (только вперед, не боком)
            move_x = math.cos(self.angle) * self.move_speed
            move_y = math.sin(self.angle) * self.move_speed
            self.x += move_x
            self.y += move_y
            return False
    
    def _rotate_towards(self, target_angle):
        """Поворачивается к целевому углу"""
        # Нормализуем углы
        current_angle = self._normalize_angle(self.angle)
        target_angle = self._normalize_angle(target_angle)
        
        # Вычисляем разницу углов
        angle_diff = target_angle - current_angle
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        if abs(angle_diff) < self.rotation_speed:
            self.angle = target_angle
            return True
        else:
            # Поворачиваемся в нужном направлении
            if angle_diff > 0:
                self.angle += self.rotation_speed
            else:
                self.angle -= self.rotation_speed
            self.angle = self._normalize_angle(self.angle)
            return False
    
    def update(self, maze):
        """Обновляет состояние демо-игрока"""
        current_time = time.time()
        
        if current_time - self.last_action_time < self.action_delay:
            return
        
        self.last_action_time = current_time
        
        if self.state == "finding_path":
            if self.find_path_to_exit(maze):
                self.state = "rotating"
                self.current_step = 0
            else:
                self.state = "completed"
            return
        
        if self.state == "completed" or self.current_step >= len(self.path) - 1:
            self.state = "completed"
            return
        
        current_pos = (int(self.x), int(self.y))
        next_pos = self.path[self.current_step + 1]
        
        # Если мы уже достигли следующей точки, переходим к следующему шагу
        if current_pos == next_pos:
            self.current_step += 1
            if self.current_step >= len(self.path) - 1:
                self.state = "completed"
                return
            next_pos = self.path[self.current_step + 1]
        
        target_x = next_pos[0] + 0.5
        target_y = next_pos[1] + 0.5
        
        # Всегда сначала поворачиваемся, потом двигаемся вперед
        if self.state == "rotating":
            target_angle = self._get_direction_angle(current_pos, next_pos)
            if self._rotate_towards(target_angle):
                self.state = "moving"
        
        elif self.state == "moving":
            # Проверяем, правильно ли мы направлены
            current_angle = self._normalize_angle(self.angle)
            target_angle = self._get_direction_angle(current_pos, next_pos)
            angle_diff = abs(current_angle - target_angle)
            
            # Если угол отклонения слишком большой, снова поворачиваемся
            if angle_diff > math.pi / 8:  # ~22.5 градусов
                self.state = "rotating"
            elif self._move_towards(target_x, target_y):
                self.current_step += 1
                if self.current_step >= len(self.path) - 1:
                    self.state = "completed"
                else:
                    self.state = "rotating"
    
    def check_exit(self, maze):
        """Проверяет, достиг ли игрок выхода"""
        map_x, map_y = int(self.x), int(self.y)
        if (0 <= map_x < len(maze[0]) and 0 <= map_y < len(maze)):
            return maze[map_y][map_x] == EXIT_SYMBOL
        return False
    
    def get_progress(self):
        """Возвращает прогресс прохождения"""
        if not self.path:
            return 0
        return min(100, int((self.current_step / (len(self.path) - 1)) * 100))