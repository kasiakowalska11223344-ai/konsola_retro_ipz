"""Shared settings and constants for the Snake game."""

import pygame

# Window and display settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Board dimensions, measured in tiles
BOARD_COLUMNS = 17
BOARD_ROWS = 15
CELL_SIZE = 40
WALL_THICKNESS = CELL_SIZE

BOARD_WIDTH = BOARD_COLUMNS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE

# Center the board inside the window
BOARD_LEFT = (WINDOW_WIDTH - BOARD_WIDTH - 2 * WALL_THICKNESS) // 2
BOARD_TOP = (WINDOW_HEIGHT - BOARD_HEIGHT - 2 * WALL_THICKNESS) // 2
BOARD_X = BOARD_LEFT + WALL_THICKNESS
BOARD_Y = BOARD_TOP + WALL_THICKNESS

# Movement settings
SNAKE_SPEED = 8  # Tiles per second
MOVEMENT_SPEED = SNAKE_SPEED * CELL_SIZE  # Pixels per second
MAX_QUEUED_TURNS = 2

# Late-turn forgiveness: after passing a tile center, accept a turn for 60 ms.
# At the current speed this is about 19 pixels (less than half a tile).
TURN_GRACE_TIME = 0.06
TURN_GRACE_DISTANCE = MOVEMENT_SPEED * TURN_GRACE_TIME

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (235, 65, 40)

BOARD_LIGHT = (176, 176, 176)  # Light gray
BOARD_DARK = (128, 128, 128)  # Gray
WALL_COLOR = (64, 64, 64)  # Dark gray border around the board

SNAKE_COLOR = (57, 108, 232)
FOOD_COLOR = RED
FOOD_LEAF_COLOR = (70, 190, 65)

# Direction vectors are measured in tiles.
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

OPPOSITE_DIRECTIONS = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

KEY_DIRECTIONS = {
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
}
