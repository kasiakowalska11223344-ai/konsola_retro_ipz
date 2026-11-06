"""Entry point for the Snake game."""

import pygame

from board import draw_board
from fonts import load_game_font
from food import draw_food, spawn_food
from settings import (
    FPS,
    KEY_DIRECTIONS,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)
from snake import Snake
from sounds import SoundEffects
from ui import show_end_screen, show_score


def main():
    pygame.init()
    pygame.display.set_caption("Snake")

    # Create fullscreen window at the original resolution
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.FULLSCREEN,
    )

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()

    # Initialize fonts
    score_font = load_game_font(16)
    end_font = load_game_font(28)

    # Initialize sound effects
    sound_effects = SoundEffects()

    # Create the snake and pass it the sound manager
    snake = Snake(sound_effects)

    # Spawn the first fruit
    food_position = spawn_food(snake.body)

    # Game variables
    score = 0
    running = True
    end_message = None

    try:

        # -------------------- Main Game Loop --------------------

        while running:

            # Calculate elapsed time since the previous frame
            delta_time = min(
                clock.tick(FPS) / 1000.0,
                0.1
            )

            # -------------------- Event Handling --------------------

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:

                    # ESC closes the game
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Handle arrow key input
                    elif event.key in KEY_DIRECTIONS:
                        snake.request_direction(
                            KEY_DIRECTIONS[event.key]
                        )

            if not running:
                break

            # -------------------- Update Game --------------------

            ate_food, end_message = snake.update(
                delta_time,
                food_position
            )

            # Stop the game if a collision occurred
            if end_message is not None:
                running = False
                break

            # Handle fruit consumption
            if ate_food:

                score += 10

                # Play the fruit eating sound
                sound_effects.play_eat_fruit()

                # Spawn replacement food
                food_position = spawn_food(snake.body)

                # Check whether the board is completely filled
                if food_position is None:
                    end_message = "You Win!"
                    running = False
                    break

            # -------------------- Draw Game --------------------

            draw_board(screen)

            snake.draw(screen)

            draw_food(screen, food_position)

            show_score(screen, score, score_font)

            pygame.display.flip()

        # -------------------- Game Over --------------------

        if end_message is not None:

            # Play game-over sound only when the player loses
            if end_message == "Game Over!":
                sound_effects.play_game_over()

            show_end_screen(
                screen,
                score,
                end_message,
                end_font
            )

    finally:

        # Restore the mouse cursor
        pygame.mouse.set_visible(True)

        # Close Pygame properly
        pygame.quit()


# -------------------- Start the Game --------------------

if __name__ == "__main__":
    main()
