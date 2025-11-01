# Конфигурационные параметры игры
import os

# Размеры карты
MAP_WIDTH = 50
MAP_HEIGHT = 50

# Символы для отображения (теперь от светлого к темному)
WALL_SYMBOLS = " .,-=+*#%@"  # Градиент от самого светлого к самому темному
EMPTY_SYMBOL = ' '
PLAYER_START_SYMBOL = 'S'
EXIT_SYMBOL = '0'
WALL_SYMBOL = '#'

# Настройки игрока
PLAYER_HEIGHT = 0.5
MOVE_SPEED = 0.1
ROTATION_SPEED = 0.05

# Настройки raycasting
FOV = 3.14159 / 3  # 60 градусов
MAX_RENDER_DISTANCE = 10
NUM_RAYS = 60

# Настройки консоли
CONSOLE_WIDTH = 120
CONSOLE_HEIGHT = 40

# Функция очистки консоли
clear = lambda: os.system('cls')

# config.py - добавим константу для имени файла дампа
DUMP_FILENAME = "lastgame_dump.txt"