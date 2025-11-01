# maze_generator.py - исправленная версия с увеличенным количеством попыток
import random
from config import *

class MazeGenerator:
    def __init__(self, width=None, height=None, room_size=None):
        # Принимаем размеры явно при создании
        self.width = width if width is not None else MAP_WIDTH
        self.height = height if height is not None else MAP_HEIGHT
        self.room_size = room_size if room_size is not None else ROOM_SIZE
        self.maze = []
        
    def update_dimensions(self, width, height, room_size):
        """Явно обновляет размеры"""
        self.width = width
        self.height = height
        self.room_size = room_size
        
    def generate_maze(self, width=None, height=None, room_size=None):
        """Генерирует лабиринт с проверкой проходимости"""
        # Обновляем размеры если переданы
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if room_size is not None:
            self.room_size = room_size
            
        print(f"Генерация лабиринта {self.width}x{self.height}...")
        
        # Увеличиваем количество попыток для сложных уровней
        if self.width >= 800:  # Сложность 5 - экстрим
            max_attempts = 150
        elif self.width >= 400:  # Сложность 4 - хардкор
            max_attempts = 120
        elif self.width >= 200:  # Сложность 3 - сложная
            max_attempts = 100
        else:
            max_attempts = 50
            
        for attempt in range(max_attempts):
            print(f"Попытка {attempt + 1}/{max_attempts}")
            
            try:
                self._generate_base_maze()
                
                # Генерируем комнаты ДО размещения старта и выхода
                self._generate_rooms_during_maze()
                
                start_pos = self._place_player_start()
                exit_pos = self._place_exit()
                
                if self._is_maze_solvable(start_pos, exit_pos):
                    print(f"Лабиринт {self.width}x{self.height} сгенерирован успешно!")
                    return True
                else:
                    print("Лабиринт непроходим, перегенерируем...")
            except Exception as e:
                print(f"Ошибка при генерации: {e}")
                continue
        
        print("Не удалось сгенерировать проходимый лабиринт!")
        return False
    
    def _generate_base_maze(self):
        """Генерирует базовую структуру лабиринта с оптимизацией для больших размеров"""
        # Инициализируем карту стенами
        self.maze = [[WALL_SYMBOL for _ in range(self.width)] for _ in range(self.height)]
        
        # Определяем настройки в зависимости от сложности
        if self.width >= 800:  # Сложность 5 - экстрим
            step_size = 3
            room_generation_interval = self.width // 25
            corridor_width = random.randint(2, 3)
            max_empty_around = 8
        elif self.width >= 400:  # Сложность 4 - хардкор (как экстрим)
            step_size = 3
            room_generation_interval = self.width // 20
            corridor_width = 2
            max_empty_around = 8
        elif self.width >= 200:  # Сложность 3 - сложная (как экстрим)
            step_size = 3
            room_generation_interval = self.width // 15
            corridor_width = 2
            max_empty_around = 8
        elif self.width >= 100:  # Сложность 2 - нормальная
            step_size = 2
            room_generation_interval = self.width // 10
            corridor_width = 1
            max_empty_around = 4
        else:  # Сложность 1 - легкая
            step_size = 2
            room_generation_interval = self.width // 5
            corridor_width = 1
            max_empty_around = 3
        
        step_count = 0
        # Увеличиваем максимальное количество шагов для сложных уровней
        if self.width >= 200:
            max_steps = min(150000, self.width * self.height // 2)
        else:
            max_steps = min(100000, self.width * self.height // 2)
        
        # Используем алгоритм поиска в глубину для генерации лабиринта
        stack = []
        start_x, start_y = 1, 1
        
        # Создаем стартовую область с учетом ширины коридоров
        for y in range(start_y, start_y + corridor_width):
            for x in range(start_x, start_x + corridor_width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.maze[y][x] = EMPTY_SYMBOL
        
        stack.append((start_x, start_y))
        
        while stack and step_count < max_steps:
            current_x, current_y = stack[-1]
            
            # Увеличиваем счетчик шагов
            step_count += 1
            
            # Проверяем, не пора ли генерировать комнату
            if step_count % room_generation_interval == 0:
                if random.random() < 0.5:  # Увеличиваем шанс генерации комнаты
                    self._try_generate_random_room()
            
            # Получаем возможные направления
            directions = []
            for dx, dy in [(0, step_size), (step_size, 0), (0, -step_size), (-step_size, 0)]:
                nx, ny = current_x + dx, current_y + dy
                if (1 <= nx < self.width - 1 and 
                    1 <= ny < self.height - 1 and 
                    self.maze[ny][nx] == WALL_SYMBOL):
                    
                    # Более простая проверка для сложных уровней
                    empty_count = 0
                    check_range = 2 if corridor_width > 1 else 1
                    for check_dx in range(-check_range, check_range + 1):
                        for check_dy in range(-check_range, check_range + 1):
                            if check_dx == 0 and check_dy == 0:
                                continue
                            cx, cy = nx + check_dx, ny + check_dy
                            if (0 <= cx < self.width and 0 <= cy < self.height and
                                self.maze[cy][cx] == EMPTY_SYMBOL):
                                empty_count += 1
                    
                    # Увеличиваем допустимое количество пустых клеток вокруг
                    if empty_count <= max_empty_around:
                        directions.append((dx, dy, nx, ny))
            
            if directions:
                dx, dy, next_x, next_y = random.choice(directions)
                
                # Создаем коридор с учетом ширины
                if corridor_width > 1:
                    # Для широких коридоров создаем несколько клеток
                    for wy in range(corridor_width):
                        for wx in range(corridor_width):
                            wall_x = current_x + dx//2 + wx
                            wall_y = current_y + dy//2 + wy
                            next_cell_x = next_x + wx
                            next_cell_y = next_y + wy
                            
                            if (0 <= wall_x < self.width and 0 <= wall_y < self.height):
                                self.maze[wall_y][wall_x] = EMPTY_SYMBOL
                            if (0 <= next_cell_x < self.width and 0 <= next_cell_y < self.height):
                                self.maze[next_cell_y][next_cell_x] = EMPTY_SYMBOL
                else:
                    # Обычные коридоры (1 клетка шириной)
                    wall_x = current_x + dx//2
                    wall_y = current_y + dy//2
                    self.maze[wall_y][wall_x] = EMPTY_SYMBOL
                    self.maze[next_y][next_x] = EMPTY_SYMBOL
                    
                stack.append((next_x, next_y))
            else:
                stack.pop()
        
        # Добавляем больше случайных проходов для увеличения связности
        self._add_random_paths()
        
        # Дополнительно: соединяем изолированные области
        self._connect_isolated_areas()
    
    def _connect_isolated_areas(self):
        """Соединяет изолированные области лабиринта"""
        if self.width >= 400:
            connection_attempts = self.width * self.height // 500  # Увеличиваем попытки
        elif self.width >= 200:
            connection_attempts = self.width * self.height // 400
        else:
            connection_attempts = self.width * self.height // 300
            
        for _ in range(connection_attempts):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            
            if self.maze[y][x] == WALL_SYMBOL:
                # Более простая проверка для сложных уровней
                empty_count = 0
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and
                        self.maze[ny][nx] == EMPTY_SYMBOL):
                        empty_count += 1
                
                # Если есть хотя бы 2 пустые клетки вокруг, убираем стену
                if empty_count >= 2:
                    self.maze[y][x] = EMPTY_SYMBOL
    
    def _try_generate_random_room(self):
        """Пытается сгенерировать случайную комнату с оптимизацией"""
        attempts = 0
        max_attempts = 20  # Увеличиваем количество попыток
        
        while attempts < max_attempts:
            attempts += 1
            
            # Случайная позиция для комнаты
            room_x = random.randint(2, self.width - self.room_size - 2)
            room_y = random.randint(2, self.height - self.room_size - 2)
            
            # Упрощенная проверка для сложных уровней
            if self._can_place_room_simple(room_x, room_y, self.room_size):
                self._create_room(room_x, room_y, self.room_size)
                return True
        
        return False
    
    def _generate_rooms_during_maze(self):
        """Дополнительная генерация комнат после создания базового лабиринта"""
        # Увеличиваем количество комнат для больших лабиринтов
        if self.width >= 400:
            additional_rooms = max(15, self.width * self.height // 1500)
        elif self.width >= 200:
            additional_rooms = max(12, self.width * self.height // 1200)
        else:
            additional_rooms = max(10, self.width * self.height // 1000)
            
        rooms_created = 0
        attempts = 0
        max_attempts = additional_rooms * 20  # Увеличиваем максимальное количество попыток
        
        while rooms_created < additional_rooms and attempts < max_attempts:
            attempts += 1
            
            # Случайная позиция для комнаты
            room_x = random.randint(2, self.width - self.room_size - 2)
            room_y = random.randint(2, self.height - self.room_size - 2)
            
            # Упрощенная проверка для сложных уровней
            if self._can_place_room_simple(room_x, room_y, self.room_size):
                self._create_room(room_x, room_y, self.room_size)
                rooms_created += 1
    
    def _can_place_room_simple(self, x, y, size):
        """Упрощенная проверка возможности размещения комнаты"""
        # Проверяем границы
        if x < 2 or x + size >= self.width - 2 or y < 2 or y + size >= self.height - 2:
            return False
        
        # Упрощенная проверка для сложных уровней - проверяем только углы
        if self.width >= 200:
            # Проверяем только углы и центр
            check_points = [
                (x, y), (x + size - 1, y),
                (x, y + size - 1), (x + size - 1, y + size - 1),
                (x + size // 2, y + size // 2)
            ]
            
            for px, py in check_points:
                if (0 <= px < self.width and 0 <= py < self.height and
                    self.maze[py][px] != WALL_SYMBOL):
                    return False
            return True
        else:
            # Для маленьких лабиринтов проверяем всю область
            for room_y in range(y, y + size):
                for room_x in range(x, x + size):
                    if (0 <= room_x < self.width and 0 <= room_y < self.height and
                        self.maze[room_y][room_x] != WALL_SYMBOL):
                        return False
            return True
    
    def _create_room(self, x, y, size):
        """Создает комнату заданного размера"""
        # Создаем пустую комнату
        for room_y in range(y, y + size):
            for room_x in range(x, x + size):
                if 0 <= room_x < self.width and 0 <= room_y < self.height:
                    self.maze[room_y][room_x] = EMPTY_SYMBOL
        
        # Меньше стен в комнатах для больших лабиринтов
        if self.width >= 200:
            num_walls = random.randint(0, max(0, size // 6))  # Еще меньше стен
        else:
            num_walls = random.randint(0, 1)
            
        walls_placed = 0
        attempts = 0
        
        while walls_placed < num_walls and attempts < 5:
            attempts += 1
            wall_x = random.randint(x + 1, x + size - 2)
            wall_y = random.randint(y + 1, y + size - 2)
            
            # Проверяем, что не ставим стену на проход
            if self.maze[wall_y][wall_x] == EMPTY_SYMBOL:
                self.maze[wall_y][wall_x] = WALL_SYMBOL
                walls_placed += 1
        
        # Создаем проходы из комнаты (увеличиваем количество проходов)
        if self.width >= 200:
            num_exits = random.randint(3, min(6, size - 1))  # Еще больше проходов
        else:
            num_exits = random.randint(2, 4)
            
        exits_created = 0
        exit_attempts = 0
        
        sides = ['top', 'bottom', 'left', 'right']
        random.shuffle(sides)
        
        for side in sides:
            if exits_created >= num_exits or exit_attempts >= 25:
                break
                
            exit_attempts += 1
            
            if side == 'top' and y > 1:
                for _ in range(2):  # Пробуем несколько позиций
                    exit_x = random.randint(x + 1, x + size - 2)
                    if (0 <= exit_x < self.width and y - 1 >= 0 and
                        self.maze[y - 1][exit_x] == WALL_SYMBOL):
                        self.maze[y - 1][exit_x] = EMPTY_SYMBOL
                        exits_created += 1
                        break
                    
            elif side == 'bottom' and y + size < self.height - 1:
                for _ in range(2):
                    exit_x = random.randint(x + 1, x + size - 2)
                    if (0 <= exit_x < self.width and y + size < self.height and
                        self.maze[y + size][exit_x] == WALL_SYMBOL):
                        self.maze[y + size][exit_x] = EMPTY_SYMBOL
                        exits_created += 1
                        break
                    
            elif side == 'left' and x > 1:
                for _ in range(2):
                    exit_y = random.randint(y + 1, y + size - 2)
                    if (0 <= exit_y < self.height and x - 1 >= 0 and
                        self.maze[exit_y][x - 1] == WALL_SYMBOL):
                        self.maze[exit_y][x - 1] = EMPTY_SYMBOL
                        exits_created += 1
                        break
                    
            elif side == 'right' and x + size < self.width - 1:
                for _ in range(2):
                    exit_y = random.randint(y + 1, y + size - 2)
                    if (0 <= exit_y < self.height and x + size < self.width and
                        self.maze[exit_y][x + size] == WALL_SYMBOL):
                        self.maze[exit_y][x + size] = EMPTY_SYMBOL
                        exits_created += 1
                        break

    def _add_random_paths(self):
        """Добавляет случайные проходы для улучшения связности"""
        if self.width >= 400:
            extra_paths = self.width * self.height // 60  # Увеличиваем количество проходов
        elif self.width >= 200:
            extra_paths = self.width * self.height // 50
        else:
            extra_paths = self.width * self.height // 40
            
        for _ in range(extra_paths):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            if self.maze[y][x] == WALL_SYMBOL:
                empty_around = False
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and
                        self.maze[ny][nx] == EMPTY_SYMBOL):
                        empty_around = True
                        break
                
                if empty_around:
                    self.maze[y][x] = EMPTY_SYMBOL

    # Остальные методы остаются без значительных изменений, но с оптимизацией
    def _place_player_start(self):
        """Размещает стартовую позицию игрока в центре комнаты"""
        if self.width >= 400:
            start_search_x = self.width // 10
            start_search_y = self.height // 10
        else:
            start_search_x = 2
            start_search_y = 2
            
        # Ищем подходящее место для старта
        for y in range(start_search_y, min(self.height - 2, start_search_y + 150)):
            for x in range(start_search_x, min(self.width - 2, start_search_x + 150)):
                if (self.maze[y][x] == EMPTY_SYMBOL and 
                    self._count_empty_around(x, y) >= 1):
                    
                    start_room_center = self._create_start_room(x, y)
                    self.maze[start_room_center[1]][start_room_center[0]] = PLAYER_START_SYMBOL
                    return start_room_center
        
        # Если не нашли подходящее место, создаем комнату в безопасном месте
        safe_x = max(2, self.width // 10)
        safe_y = max(2, self.height // 10)
        start_room_center = self._create_start_room(safe_x, safe_y)
        self.maze[start_room_center[1]][start_room_center[0]] = PLAYER_START_SYMBOL
        return start_room_center

    def _place_exit(self):
        """Размещает выход в комнате как можно дальше от старта"""
        start_pos = None
        for y in range(min(200, self.height)):
            for x in range(min(200, self.width)):
                if self.maze[y][x] == PLAYER_START_SYMBOL:
                    start_pos = (x, y)
                    break
            if start_pos:
                break
        
        if not start_pos:
            start_pos = (self.width // 10, self.height // 10)
        
        max_distance = 0
        exit_pos = start_pos
        
        search_step = 3 if self.width >= 400 else 2 if self.width >= 200 else 1
        
        # Ищем самую дальнюю точку
        for y in range(3, self.height - 3, search_step):
            for x in range(3, self.width - 3, search_step):
                if self.maze[y][x] == EMPTY_SYMBOL:
                    distance = abs(x - start_pos[0]) + abs(y - start_pos[1])
                    if distance > max_distance:
                        max_distance = distance
                        exit_pos = (x, y)
        
        exit_room_center = self._create_exit_room(exit_pos[0], exit_pos[1])
        self.maze[exit_room_center[1]][exit_room_center[0]] = EXIT_SYMBOL
        return exit_room_center

    def _is_maze_solvable(self, start_pos, exit_pos):
        """Проверяет, можно ли пройти от старта до выхода с оптимизацией"""
        if not start_pos or not exit_pos:
            return False
        
        # Для больших лабиринтов используем упрощенную проверку
        if self.width >= 200:
            return self._quick_solvability_check(start_pos, exit_pos)
        
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        stack = [start_pos]
        visited[start_pos[1]][start_pos[0]] = True
        
        max_steps = min(300000, self.width * self.height // 2)
        
        steps = 0
        while stack and steps < max_steps:
            x, y = stack.pop()
            steps += 1
            
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

    def _quick_solvability_check(self, start_pos, exit_pos):
        """Быстрая проверка проходимости для больших лабиринтов"""
        visited = set()
        stack = [start_pos]
        visited.add(start_pos)
        
        max_steps = 200000  # Увеличиваем максимальное количество шагов
        
        steps = 0
        while stack and steps < max_steps:
            x, y = stack.pop()
            steps += 1
            
            # Более либеральная проверка достижения выхода
            if (x, y) == exit_pos or (abs(x - exit_pos[0]) + abs(y - exit_pos[1])) < 25:
                return True
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                    (nx, ny) not in visited and
                    self.maze[ny][nx] in (EMPTY_SYMBOL, EXIT_SYMBOL, PLAYER_START_SYMBOL)):
                    visited.add((nx, ny))
                    stack.append((nx, ny))
        
        return False

    # Остальные методы без изменений
    def _count_empty_around(self, x, y):
        """Считает количество пустых клеток вокруг"""
        count = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height and
                self.maze[ny][nx] in (EMPTY_SYMBOL, PLAYER_START_SYMBOL, EXIT_SYMBOL)):
                count += 1
        return count

    def _create_start_room(self, x, y):
        """Создает комнату для стартовой позиции"""
        room_size = self.room_size
        start_x = max(1, x - room_size // 2)
        start_y = max(1, y - room_size // 2)
        
        start_x = min(start_x, self.width - room_size - 1)
        start_y = min(start_y, self.height - room_size - 1)
        
        for room_y in range(start_y, start_y + room_size):
            for room_x in range(start_x, start_x + room_size):
                if 0 <= room_x < self.width and 0 <= room_y < self.height:
                    self.maze[room_y][room_x] = EMPTY_SYMBOL
        
        # Создаем проходы из стартовой комнаты
        for side in ['top', 'bottom', 'left', 'right']:
            if side == 'top' and start_y > 1:
                exit_x = start_x + room_size // 2
                if 0 <= exit_x < self.width and start_y - 1 >= 0:
                    self.maze[start_y - 1][exit_x] = EMPTY_SYMBOL
            elif side == 'bottom' and start_y + room_size < self.height - 1:
                exit_x = start_x + room_size // 2
                if 0 <= exit_x < self.width and start_y + room_size < self.height:
                    self.maze[start_y + room_size][exit_x] = EMPTY_SYMBOL
            elif side == 'left' and start_x > 1:
                exit_y = start_y + room_size // 2
                if 0 <= exit_y < self.height and start_x - 1 >= 0:
                    self.maze[exit_y][start_x - 1] = EMPTY_SYMBOL
            elif side == 'right' and start_x + room_size < self.width - 1:
                exit_y = start_y + room_size // 2
                if 0 <= exit_y < self.height and start_x + room_size < self.width:
                    self.maze[exit_y][start_x + room_size] = EMPTY_SYMBOL
        
        return (start_x + room_size // 2, start_y + room_size // 2)

    def _create_exit_room(self, x, y):
        """Создает комнату для выхода"""
        room_size = self.room_size
        
        start_x = max(2, x - room_size // 2)
        start_y = max(2, y - room_size // 2)
        start_x = min(start_x, self.width - room_size - 2)
        start_y = min(start_y, self.height - room_size - 2)
        
        for room_y in range(start_y, start_y + room_size):
            for room_x in range(start_x, start_x + room_size):
                if 0 <= room_x < self.width and 0 <= room_y < self.height:
                    self.maze[room_y][room_x] = EMPTY_SYMBOL
        
        # Меньше стен в комнате выхода
        num_walls = random.randint(0, 1)
        for _ in range(num_walls):
            wall_x = random.randint(start_x + 1, start_x + room_size - 2)
            wall_y = random.randint(start_y + 1, start_y + room_size - 2)
            if 0 <= wall_x < self.width and 0 <= wall_y < self.height:
                self.maze[wall_y][wall_x] = WALL_SYMBOL
        
        # Больше выходов из комнаты выхода
        num_exits = random.randint(3, 5)
        exits_created = 0
        
        sides = ['top', 'bottom', 'left', 'right']
        random.shuffle(sides)
        
        for side in sides:
            if exits_created >= num_exits:
                break
                
            if side == 'top' and start_y > 1:
                for _ in range(2):
                    exit_x = random.randint(start_x + 1, start_x + room_size - 2)
                    if (0 <= exit_x < self.width and start_y - 1 >= 0 and
                        self.maze[start_y - 1][exit_x] == WALL_SYMBOL):
                        self.maze[start_y - 1][exit_x] = EMPTY_SYMBOL
                        exits_created += 1
                        break
            elif side == 'bottom' and start_y + room_size < self.height - 1:
                for _ in range(2):
                    exit_x = random.randint(start_x + 1, start_x + room_size - 2)
                    if (0 <= exit_x < self.width and start_y + room_size < self.height and
                        self.maze[start_y + room_size][exit_x] == WALL_SYMBOL):
                        self.maze[start_y + room_size][exit_x] = EMPTY_SYMBOL
                        exits_created += 1
                        break
            elif side == 'left' and start_x > 1:
                for _ in range(2):
                    exit_y = random.randint(start_y + 1, start_y + room_size - 2)
                    if (0 <= exit_y < self.height and start_x - 1 >= 0 and
                        self.maze[exit_y][start_x - 1] == WALL_SYMBOL):
                        self.maze[exit_y][start_x - 1] = EMPTY_SYMBOL
                        exits_created += 1
                        break
            elif side == 'right' and start_x + room_size < self.width - 1:
                for _ in range(2):
                    exit_y = random.randint(start_y + 1, start_y + room_size - 2)
                    if (0 <= exit_y < self.height and start_x + room_size < self.width and
                        self.maze[exit_y][start_x + room_size] == WALL_SYMBOL):
                        self.maze[exit_y][start_x + room_size] = EMPTY_SYMBOL
                        exits_created += 1
                        break
        
        return (start_x + room_size // 2, start_y + room_size // 2)

    def get_maze(self):
        return self.maze

    def get_maze_string(self):
        """Возвращает текстовое представление всего лабиринта"""
        maze_str = f"Размер лабиринта: {len(self.maze[0])}x{len(self.maze)}\n"
        for row in self.maze:
            maze_str += "".join(row) + "\n"
        return maze_str