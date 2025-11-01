# config.py - обновленный файл конфигурации
# Конфигурационные параметры игры
import os

# Сложности и размеры карты
DIFFICULTIES = {
    "легкая": {"width": 50, "height": 50, "room_size": 3},
    "нормальная": {"width": 100, "height": 100, "room_size": 5},
    "сложная": {"width": 200, "height": 200, "room_size": 7},
    "хардкор": {"width": 400, "height": 400, "room_size": 9},
    "экстрим": {"width": 800, "height": 800, "room_size": 11}
}

# Размеры карты по умолчанию (будут переопределены после выбора сложности)
MAP_WIDTH = 50
MAP_HEIGHT = 50
ROOM_SIZE = 3

# Символы для отображения (теперь от светлого к темному)
WALL_SYMBOLS = " .,-=+*#%@"  # Градиент от самого светлого к самому темному
EMPTY_SYMBOL = ' '
PLAYER_START_SYMBOL = 'S'
EXIT_SYMBOL = '0'
WALL_SYMBOL = '#'

# Настройки игрока
PLAYER_HEIGHT = 0.25
MOVE_SPEED = 0.2
ROTATION_SPEED = 0.1

# Настройки raycasting
FOV = 3.14159 / 3  # 60 градусов
MAX_RENDER_DISTANCE = 10
NUM_RAYS = 120  # Увеличиваем количество лучей для лучшего качества

# Настройки консоли (соотношение 2:1)
CONSOLE_WIDTH = 120
CONSOLE_HEIGHT = 40  # 120:40 = 3:1, но символы примерно 2:1 по размеру

# Функция очистки консоли
clear = lambda: os.system('cls')

# config.py - добавим константу для имени файла дампа
DUMP_FILENAME = "lastgame_dump.txt"