"""Food placement and rendering."""

import random
import pygame

from board import grid_to_pixel
from settings import (
    BOARD_COLUMNS,
    BOARD_ROWS,
    CELL_SIZE,
    FOOD_COLOR,
    FOOD_LEAF_COLOR,
)


def spawn_food(snake_body):
    """Choose a random unoccupied tile, or return None if the board is full."""
    occupied_positions = set(snake_body)
    available_positions = [
        (column, row)
        for column in range(BOARD_COLUMNS)
        for row in range(BOARD_ROWS)
        if (column, row) not in occupied_positions
    ]

    return random.choice(available_positions) if available_positions else None


def draw_food(screen, food_position):
    """Draw the food as a red apple with a small green leaf."""
    if food_position is None:
        return

    center_x, center_y = grid_to_pixel(food_position)

    pygame.draw.circle(
        screen,
        FOOD_COLOR,
        (center_x, center_y),
        CELL_SIZE // 2 - 3,
    )
    pygame.draw.ellipse(
        screen,
        FOOD_LEAF_COLOR,
        (center_x + 1, center_y - 19, 10, 6),
    )
