import math
from config import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Направление взгляда в радианах
        self.height = PLAYER_HEIGHT
        self.move_speed = MOVE_SPEED
        self.rotation_speed = ROTATION_SPEED
        self.target_x = x  # Целевая позиция для демо-режима
        self.target_y = y
        self.target_angle = 0  # Целевой угол для демо-режима
        self.is_moving = False  # Флаг движения для демо-режима
        self.is_rotating = False  # Флаг поворота для демо-режима
        
    def move_forward(self, maze):
        """Движение вперед с проверкой столкновений"""
        new_x = self.x + math.cos(self.angle) * self.move_speed
        new_y = self.y + math.sin(self.angle) * self.move_speed
        
        if not self._check_collision(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
    
    def move_backward(self, maze):
        """Движение назад с проверкой столкновений"""
        new_x = self.x - math.cos(self.angle) * self.move_speed
        new_y = self.y - math.sin(self.angle) * self.move_speed
        
        if not self._check_collision(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
    
    def strafe_left(self, maze):
        """Движение влево с проверкой столкновений"""
        new_x = self.x + math.cos(self.angle - math.pi/2) * self.move_speed
        new_y = self.y + math.sin(self.angle - math.pi/2) * self.move_speed
        
        if not self._check_collision(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
    
    def strafe_right(self, maze):
        """Движение вправо с проверкой столкновений"""
        new_x = self.x + math.cos(self.angle + math.pi/2) * self.move_speed
        new_y = self.y + math.sin(self.angle + math.pi/2) * self.move_speed
        
        if not self._check_collision(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
    
    def rotate_left(self):
        """Поворот камеры влево"""
        self.angle -= self.rotation_speed
        self._normalize_angle()
    
    def rotate_right(self):
        """Поворот камеры вправо"""
        self.angle += self.rotation_speed
        self._normalize_angle()
    
    def _normalize_angle(self):
        """Нормализует угол в диапазон [0, 2π]"""
        self.angle %= 2 * math.pi
        if self.angle < 0:
            self.angle += 2 * math.pi
    
    def get_angle_degrees(self):
        """Возвращает угол в градусах [0, 360)"""
        degrees = math.degrees(self.angle) % 360
        if degrees < 0:
            degrees += 360
        return degrees
    
    # Методы для демо-режима
    def set_target_position(self, target_x, target_y):
        """Устанавливает целевую позицию для движения в демо-режиме"""
        self.target_x = target_x
        self.target_y = target_y
        self.is_moving = True
    
    def set_target_angle(self, target_angle):
        """Устанавливает целевой угол для поворота в демо-режиме"""
        self.target_angle = target_angle
        self.is_rotating = True
    
    def update_demo_movement(self):
        """Обновляет движение и поворот для демо-режима"""
        # Поворот к целевому углу
        if self.is_rotating:
            angle_diff = self.target_angle - self.angle
            # Нормализуем разницу углов
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            if abs(angle_diff) < self.rotation_speed:
                self.angle = self.target_angle
                self.is_rotating = False
            else:
                if angle_diff > 0:
                    self.angle += self.rotation_speed
                else:
                    self.angle -= self.rotation_speed
                self._normalize_angle()
        
        # Движение к целевой позиции
        if self.is_moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.move_speed:
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
            else:
                # Двигаемся в направлении цели
                move_x = dx / distance * self.move_speed
                move_y = dy / distance * self.move_speed
                self.x += move_x
                self.y += move_y
    
    def _check_collision(self, x, y, maze):
        """Проверка столкновения со стенами"""
        map_x, map_y = int(x), int(y)
        
        # Проверяем клетку, в которой находимся
        if (0 <= map_x < len(maze[0]) and 0 <= map_y < len(maze)):
            if maze[map_y][map_x] == WALL_SYMBOL:
                return True
        
        # Дополнительная проверка соседних клеток для плавности
        for dx, dy in [(0.2, 0), (-0.2, 0), (0, 0.2), (0, -0.2)]:
            check_x, check_y = int(x + dx), int(y + dy)
            if (0 <= check_x < len(maze[0]) and 0 <= check_y < len(maze)):
                if maze[check_y][check_x] == WALL_SYMBOL:
                    return True
        
        return False
    
    def check_exit(self, maze):
        """Проверяет, достиг ли игрок выхода"""
        map_x, map_y = int(self.x), int(self.y)
        if (0 <= map_x < len(maze[0]) and 0 <= map_y < len(maze)):
            return maze[map_y][map_x] == EXIT_SYMBOL
        return False