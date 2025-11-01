# raycasting.py - с соотношением символов 2:1 и особым отображением выхода
import math
from config import *

class RayCaster:
    def __init__(self, console_width, console_height):
        self.console_width = console_width
        self.console_height = console_height
        self.fov = FOV
        self.max_distance = MAX_RENDER_DISTANCE
        self.num_rays = NUM_RAYS // 2  # Уменьшаем количество лучей для широких пикселей
        
        # Градиент символов от самого светлого к самому темному
        self.gradient_symbols = "@%#*+=-,. "
        self.gradient_length = len(self.gradient_symbols)
    
    def render_frame(self, player, maze):
        """Рендерит один кадр с помощью raycasting с соотношением 2:1"""
        frame = []
        ray_angle = player.angle - self.fov / 2
        
        for col in range(self.num_rays):
            # Бросаем луч
            distance, hit_type, hit_side, hit_exit = self._cast_ray(player.x, player.y, ray_angle, maze)
            
            # Вычисляем высоту стены с учетом соотношения 2:1
            wall_height = self._calculate_wall_height(distance)
            
            # Получаем символ для стены на основе расстояния
            wall_char = self._get_wall_symbol(distance, hit_side, hit_exit)
            
            # Создаем колонку для этого луча (учитываем соотношение 2:1)
            column = self._create_column(wall_height, distance, wall_char, hit_side, hit_exit)
            
            # Добавляем две одинаковые колонки для создания широкого пикселя (2:1)
            frame.append(column)
            frame.append(column)  # Дублируем колонку для ширины 2
            
            ray_angle += self.fov / self.num_rays
        
        return self._format_frame(frame)
    
    def _cast_ray(self, start_x, start_y, angle, maze):
        """Бросает луч и возвращает расстояние до стены/выхода и тип попадания"""
        # Нормализуем угол
        angle %= 2 * math.pi
        
        # Направление луча
        ray_dir_x = math.cos(angle)
        ray_dir_y = math.sin(angle)
        
        # Текущая позиция в карте
        map_x, map_y = int(start_x), int(start_y)
        
        # Длина луча от текущей позиции до следующей x или y-линии
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')
        
        # Направление шага и начальная длина side_dist
        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (start_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - start_x) * delta_dist_x
            
        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (start_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - start_y) * delta_dist_y
        
        # Алгоритм DDA
        hit = False
        side = 0  # 0 - вертикальная стена, 1 - горизонтальная
        distance = 0
        hit_exit = False
        
        while not hit and distance < self.max_distance:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            # Проверяем, не вышли ли за границы карты
            if (map_x < 0 or map_x >= len(maze[0]) or 
                map_y < 0 or map_y >= len(maze)):
                hit = True
                distance = self.max_distance
            elif maze[map_y][map_x] == WALL_SYMBOL:
                hit = True
                # Вычисляем расстояние
                if side == 0:
                    distance = (map_x - start_x + (1 - step_x) / 2) / ray_dir_x
                else:
                    distance = (map_y - start_y + (1 - step_y) / 2) / ray_dir_y
                
                # Абсолютное значение
                distance = abs(distance)
            elif maze[map_y][map_x] == EXIT_SYMBOL:
                hit = True
                hit_exit = True
                # Вычисляем расстояние
                if side == 0:
                    distance = (map_x - start_x + (1 - step_x) / 2) / ray_dir_x
                else:
                    distance = (map_y - start_y + (1 - step_y) / 2) / ray_dir_y
                
                # Абсолютное значение
                distance = abs(distance)
        
        hit_type = 'exit' if hit_exit else 'wall'
        return min(distance, self.max_distance), hit_type, side, hit_exit
    
    def _calculate_wall_height(self, distance):
        """Вычисляет высоту стены на экране с учетом соотношения 2:1"""
        if distance == 0:
            return self.console_height
        
        # Перспективная коррекция с учетом соотношения 2:1
        # Умножаем на 2 для компенсации широких пикселей
        wall_height = int(self.console_height / distance * 2)
        return min(wall_height, self.console_height)
    
    def _get_wall_symbol(self, distance, side, is_exit=False):
        """Возвращает символ для стены/выхода на основе расстояния"""
        if is_exit:
            # Особое отображение выхода - всегда яркий символ независимо от расстояния
            # Меняем символ в зависимости от расстояния для эффекта мерцания/пульсации
            pulse_factor = (math.sin(distance * 3) + 1) / 2  # Пульсация от 0 до 1
            if pulse_factor > 0.7:
                return '0'  # Яркий символ выхода
            else:
                return 'O'  # Немного менее яркий
        
        if distance >= self.max_distance:
            return ' '  # Слишком далеко - пробел (самый темный)
    
        # Усиливаем градиент на коротких расстояниях
        # Используем квадратный корень для смещения акцента на ближние дистанции
        normalized_distance = (distance / self.max_distance) ** 0.5
    
        # Ближе = светлые символы (@, %), дальше = темные символы (., )
        gradient_index = int(normalized_distance * (self.gradient_length - 1))
        gradient_index = max(0, min(self.gradient_length - 1, gradient_index))
    
        # Добавляем эффект для разных сторон стен
        if side == 1:  # Горизонтальная стена - делаем немного светлее
            gradient_index = max(0, gradient_index - 1)
    
        return self.gradient_symbols[gradient_index]
    
    def _create_column(self, wall_height, distance, wall_char, side, is_exit=False):
        """Создает одну колонку экрана с учетом соотношения 2:1"""
        column = []
        
        # Корректируем высоты для соотношения 2:1
        ceiling_height = (self.console_height - wall_height) // 2
        floor_height = self.console_height - ceiling_height - wall_height
        
        # Для выхода создаем особое отображение
        if is_exit:
            # Выход всегда отображается ярко, независимо от расстояния
            # Создаем градиент для выхода (яркий в центре, темнее к краям)
            for i in range(ceiling_height):
                column.append(' ')
            
            for i in range(wall_height):
                # Для выхода создаем вертикальный градиент
                if wall_height <= 1:
                    current_char = wall_char
                else:
                    # Центр выхода ярче, края темнее
                    pos = i / wall_height
                    if pos < 0.3 or pos > 0.7:
                        # Края - темнее
                        current_char = 'O' if wall_char == '0' else '0'
                    else:
                        # Центр - ярче
                        current_char = wall_char
                column.append(current_char)
            
            for i in range(floor_height):
                column.append(' ')
        else:
            # Обычная стена
            # Потолок - темный (используем темные символы из конца градиента)
            for i in range(ceiling_height):
                # Градиент для потолка (темнее к верху)
                ceiling_intensity = 1.0 - (i / ceiling_height) if ceiling_height > 0 else 0
                ceiling_index = int(ceiling_intensity * (self.gradient_length - 1))
                ceiling_index = max(0, min(self.gradient_length - 1, ceiling_index))
                column.append(self.gradient_symbols[ceiling_index])
            
            # Стены - используем вычисленный символ
            for i in range(wall_height):
                current_char = wall_char
                
                # Легкий вертикальный градиент для стен (светлее к центру)
                if wall_height > 1:
                    vertical_factor = abs(i / wall_height - 0.5) * 2  # 0 в центре, 1 по краям
                    current_index = self.gradient_symbols.find(current_char)
                    # Сделаем центр стены немного светлее
                    if vertical_factor < 0.5 and current_index > 0:
                        current_char = self.gradient_symbols[current_index - 1]
                
                column.append(current_char)
            
            # Пол - светлый (используем светлые символы из начала градиента)
            for i in range(floor_height):
                # Градиент для пола (светлее к низу)
                floor_intensity = (i / floor_height) if floor_height > 0 else 0
                floor_index = int(floor_intensity * (self.gradient_length - 1) * 0.5)
                floor_index = max(0, min(self.gradient_length - 1, floor_index))
                column.append(self.gradient_symbols[floor_index])
        
        return column
    
    def _format_frame(self, frame):
        """Форматирует frame для вывода в консоль"""
        if not frame:
            return ""
        
        # Транспонируем frame (превращаем колонки в строки)
        output_lines = []
        for row in range(len(frame[0])):
            line = ""
            for col in range(len(frame)):
                if row < len(frame[col]):
                    line += frame[col][row]
                else:
                    line += " "
            output_lines.append(line)
        
        return "\n".join(output_lines)
    
    def render_minimap(self, player, maze, size=10):
        """Рендерит мини-карту с учетом соотношения 2:1"""
        minimap = ""
        player_map_x = int(player.x)
        player_map_y = int(player.y)
        
        # Корректируем размер мини-карты для соотношения 2:1
        for y in range(player_map_y - size, player_map_y + size):
            line = ""
            for x in range(player_map_x - size * 2, player_map_x + size * 2):
                if (0 <= x < len(maze[0]) and 0 <= y < len(maze)):
                    if x == player_map_x and y == player_map_y:
                        # Игрок - стрелка, показывающая направление
                        angle_deg = math.degrees(player.angle)
                        if 45 <= angle_deg < 135:
                            line += "↓"  # смотрит вниз
                        elif 135 <= angle_deg < 225:
                            line += "←"  # смотрит влево
                        elif 225 <= angle_deg < 315:
                            line += "↑"  # смотрит вверх
                        else:
                            line += "→"  # смотрит вправо
                    elif maze[y][x] == WALL_SYMBOL:
                        line += "#"
                    elif maze[y][x] == EXIT_SYMBOL:
                        line += "E"  # Яркое отображение выхода на мини-карте
                    elif maze[y][x] == PLAYER_START_SYMBOL:
                        line += "S"
                    else:
                        line += " "
                else:
                    line += " "
            minimap += line + "\n"
        
        return minimap