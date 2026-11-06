# settings.py
import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

CELL_SIZE = 22
COLS = 28
ROWS = 31
WIDTH = COLS * CELL_SIZE    # 616 px
HEIGHT = ROWS * CELL_SIZE   # 682 px

OFFSET_X = (SCREEN_WIDTH - WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - HEIGHT) // 2

FPS = 60
PLAYER_SPEED = 2

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)