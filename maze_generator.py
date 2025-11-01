import random
from config import *

class MazeGenerator:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.maze = []
        
    def generate_maze(self):
        """Генерирует лабиринт с проверкой проходимости"""
        max_attempts = 10
        for attempt in range(max_attempts):
            print(f"Попытка генерации лабиринта {attempt + 1}/{max_attempts}")
            self._generate_base_maze()
            start_pos = self._place_player_start()
            exit_pos = self._place_exit()
            
            if self._is_maze_solvable(start_pos, exit_pos):
                print("Лабиринт сгенерирован успешно!")
                return True
            else:
                print("Лабиринт непроходим, перегенерируем...")
        
        print("Не удалось сгенерировать проходимый лабиринт!")
        return False
    
    def _generate_base_maze(self):
        """Генерирует базовую структуру лабиринта"""
        # Инициализируем карту стенами
        self.maze = [[WALL_SYMBOL for _ in range(self.width)] for _ in range(self.height)]
        
        # Используем алгоритм поиска в глубину для генерации лабиринта
        stack = []
        start_x, start_y = 1, 1
        
        self.maze[start_y][start_x] = EMPTY_SYMBOL
        stack.append((start_x, start_y))
        
        while stack:
            current_x, current_y = stack[-1]
            
            # Получаем возможные направления
            directions = []
            for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                nx, ny = current_x + dx, current_y + dy
                if (1 <= nx < self.width - 1 and 
                    1 <= ny < self.height - 1 and 
                    self.maze[ny][nx] == WALL_SYMBOL):
                    
                    # Проверяем, что вокруг нет слишком много пустого пространства
                    empty_count = 0
                    for check_dx, check_dy in [(0, 1), (1, 0), (0, -1), (-1, 0), 
                                              (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        cx, cy = nx + check_dx, ny + check_dy
                        if (0 <= cx < self.width and 0 <= cy < self.height and
                            self.maze[cy][cx] == EMPTY_SYMBOL):
                            empty_count += 1
                    
                    if empty_count <= 2:
                        directions.append((dx, dy, nx, ny))
            
            if directions:
                dx, dy, next_x, next_y = random.choice(directions)
                # Убираем стену между текущей и следующей клеткой
                self.maze[current_y + dy//2][current_x + dx//2] = EMPTY_SYMBOL
                self.maze[next_y][next_x] = EMPTY_SYMBOL
                stack.append((next_x, next_y))
            else:
                stack.pop()
        
        # Добавляем случайные проходы для увеличения связности
        self._add_random_paths()
    
    def _add_random_paths(self):
        """Добавляет случайные проходы для улучшения связности"""
        for _ in range(self.width * self.height // 50):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            if self.maze[y][x] == WALL_SYMBOL:
                # Проверяем, что вокруг есть пустые клетки
                empty_around = False
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and
                        self.maze[ny][nx] == EMPTY_SYMBOL):
                        empty_around = True
                        break
                
                if empty_around:
                    self.maze[y][x] = EMPTY_SYMBOL
    
    def _place_player_start(self):
        """Размещает стартовую позицию игрока"""
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if (self.maze[y][x] == EMPTY_SYMBOL and 
                    self._count_empty_around(x, y) >= 3):
                    self.maze[y][x] = PLAYER_START_SYMBOL
                    return (x, y)
        
        # Если не нашли подходящее место, используем первое пустое
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == EMPTY_SYMBOL:
                    self.maze[y][x] = PLAYER_START_SYMBOL
                    return (x, y)
        
        return (1, 1)
    
    def _place_exit(self):
        """Размещает выход как можно дальше от старта"""
        start_pos = None
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == PLAYER_START_SYMBOL:
                    start_pos = (x, y)
                    break
            if start_pos:
                break
        
        if not start_pos:
            start_pos = (1, 1)
        
        # Ищем самую дальнюю точку от старта
        max_distance = 0
        exit_pos = start_pos
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == EMPTY_SYMBOL:
                    distance = abs(x - start_pos[0]) + abs(y - start_pos[1])
                    if distance > max_distance:
                        max_distance = distance
                        exit_pos = (x, y)
        
        self.maze[exit_pos[1]][exit_pos[0]] = EXIT_SYMBOL
        return exit_pos
    
    def _count_empty_around(self, x, y):
        """Считает количество пустых клеток вокруг"""
        count = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height and
                self.maze[ny][nx] in (EMPTY_SYMBOL, PLAYER_START_SYMBOL, EXIT_SYMBOL)):
                count += 1
        return count
    
    def _is_maze_solvable(self, start_pos, exit_pos):
        """Проверяет, можно ли пройти от старта до выхода"""
        if not start_pos or not exit_pos:
            return False
        
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        stack = [start_pos]
        visited[start_pos[1]][start_pos[0]] = True
        
        while stack:
            x, y = stack.pop()
            
            if (x, y) == exit_pos:
                return True
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                    not visited[ny][nx] and 
                    self.maze[ny][nx] in (EMPTY_SYMBOL, EXIT_SYMBOL, PLAYER_START_SYMBOL)):
                    visited[ny][nx] = True
                    stack.append((nx, ny))
        
        return False
    
    def get_maze(self):
        return self.maze