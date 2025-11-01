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
    
    def rotate_right(self):
        """Поворот камеры вправо"""
        self.angle += self.rotation_speed
    
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