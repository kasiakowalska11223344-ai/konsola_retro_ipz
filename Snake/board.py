"""Functions for drawing and positioning the game board."""

import pygame

from settings import (
    BLACK,
    BOARD_COLUMNS,
    BOARD_ROWS,
    BOARD_X,
    BOARD_Y,
    BOARD_WIDTH,
    BOARD_HEIGHT,
    BOARD_LEFT,
    BOARD_TOP,
    CELL_SIZE,
    WALL_THICKNESS,
    WALL_COLOR,
    BOARD_LIGHT,
    BOARD_DARK,
)


def grid_to_pixel(position):
    """Convert a tile coordinate into the pixel coordinate of its center."""
    column, row = position
    return (
        BOARD_X + column * CELL_SIZE + CELL_SIZE // 2,
        BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2,
    )


def draw_board(screen):
    """Draw the checkerboard playfield and its surrounding wall."""
    # Keep the area outside the board and its border completely black.
    screen.fill(BLACK)

    pygame.draw.rect(
        screen,
        WALL_COLOR,
        (
            BOARD_LEFT,
            BOARD_TOP,
            BOARD_WIDTH + 2 * WALL_THICKNESS,
            BOARD_HEIGHT + 2 * WALL_THICKNESS,
        ),
    )

    for row in range(BOARD_ROWS):
        for column in range(BOARD_COLUMNS):
            tile_color = BOARD_LIGHT if (row + column) % 2 == 0 else BOARD_DARK

            pygame.draw.rect(
                screen,
                tile_color,
                (
                    BOARD_X + column * CELL_SIZE,
                    BOARD_Y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                ),
            )
