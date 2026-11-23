"""Entry point for the Snake arcade game."""

import pygame

from board import draw_board
from fonts import load_game_font
from food import draw_food, spawn_food
from leaderboard import (
    load_leaderboard,
    qualifies_for_leaderboard,
    save_score,
)
from settings import FPS, KEY_DIRECTIONS, WINDOW_WIDTH, WINDOW_HEIGHT
from snake import Snake
from sounds import SoundEffects
from ui import (
    draw_game_over,
    draw_initials_entry,
    draw_leaderboard_result,
    draw_save_prompt,
    show_score,
)

QUIT_KEYS = (pygame.K_ESCAPE, pygame.K_RETURN)
CONFIRM_KEY = pygame.K_SPACE
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def wait_for_game_over(screen, score, message, title_font, body_font, clock):
    """Show the result for two seconds, while still allowing an immediate quit."""
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < 2000:
        clock.tick(FPS)
        draw_game_over(screen, score, message, title_font, body_font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key in QUIT_KEYS:
                return False

    return True


def ask_to_save_score(screen, entries, score, qualifies, title_font, body_font, clock):
    """Let the player choose YES or NO with the joystick, then confirm with SPACE."""
    selection = "YES"

    while True:
        clock.tick(FPS)
        draw_save_prompt(
            screen, entries, score, selection, qualifies, title_font, body_font
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type != pygame.KEYDOWN:
                continue

            if event.key in QUIT_KEYS:
                return "QUIT"

            if event.key == CONFIRM_KEY:
                return selection

            direction = KEY_DIRECTIONS.get(event.key)
            if direction in ("LEFT", "RIGHT"):
                selection = "NO" if selection == "YES" else "YES"


def enter_initials(screen, entries, score, title_font, body_font, clock):
    """Use joystick directions to select three letters; SPACE saves them."""
    initials = ["A", "A", "A"]
    selected_index = 0

    while True:
        clock.tick(FPS)
        draw_initials_entry(
            screen,
            entries,
            score,
            initials,
            selected_index,
            title_font,
            body_font,
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type != pygame.KEYDOWN:
                continue

            if event.key in QUIT_KEYS:
                return None

            if event.key == CONFIRM_KEY:
                return "".join(initials)

            direction = KEY_DIRECTIONS.get(event.key)
            if direction == "LEFT":
                selected_index = max(0, selected_index - 1)
            elif direction == "RIGHT":
                selected_index = min(2, selected_index + 1)
            elif direction == "UP":
                current = ALPHABET.index(initials[selected_index])
                initials[selected_index] = ALPHABET[(current + 1) % len(ALPHABET)]
            elif direction == "DOWN":
                current = ALPHABET.index(initials[selected_index])
                initials[selected_index] = ALPHABET[(current - 1) % len(ALPHABET)]


def wait_for_quit(screen, entries, heading, title_font, body_font, clock):
    """Keep the final leaderboard visible until the player quits."""
    while True:
        clock.tick(FPS)
        draw_leaderboard_result(screen, entries, heading, title_font, body_font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key in QUIT_KEYS:
                return


def run_round(screen, clock, sound_effects, score_font):
    """Run one round and return (score, end_message, quit_requested)."""
    snake = Snake(sound_effects)
    food_position = spawn_food(snake.body)
    score = 0

    while True:
        delta_time = min(clock.tick(FPS) / 1000.0, 0.1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, None, True

            if event.type == pygame.KEYDOWN:
                # BUTTON_1_2 is mapped to RETURN and always quits.
                if event.key in QUIT_KEYS:
                    return score, None, True

                # Joystick/keyboard directions are handled by the Snake class.
                if event.key in KEY_DIRECTIONS:
                    snake.request_direction(KEY_DIRECTIONS[event.key])

        ate_food, end_message = snake.update(delta_time, food_position)
        if end_message is not None:
            return score, end_message, False

        if ate_food:
            score += 10
            sound_effects.play_eat_fruit()
            food_position = spawn_food(snake.body)

            if food_position is None:
                return score, "You Win!", False

        draw_board(screen)
        snake.draw(screen)
        draw_food(screen, food_position)
        show_score(screen, score, score_font)
        pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("Snake")

    score_font = load_game_font(16)
    title_font = load_game_font(18)
    body_font = load_game_font(12)

    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.FULLSCREEN,
    )
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    sound_effects = SoundEffects()
    running = True

    try:
        # Run one round. After the leaderboard, the only available action
        # is quitting back to the arcade launcher.
        while running:
            score, end_message, quit_requested = run_round(
                screen, clock, sound_effects, score_font
            )

            if quit_requested:
                break

            if end_message is None:
                break

            if end_message == "Game Over!":
                sound_effects.play_game_over()

            if not wait_for_game_over(
                    screen, score, end_message, title_font, body_font, clock
            ):
                break

            entries = load_leaderboard()
            qualifies = qualifies_for_leaderboard(score, entries)

            choice = ask_to_save_score(
                screen,
                entries,
                score,
                qualifies,
                title_font,
                body_font,
                clock,
            )
            if choice == "QUIT":
                break

            heading = "SCORE NOT SAVED"

            if choice == "YES":
                if qualifies:
                    initials = enter_initials(
                        screen,
                        entries,
                        score,
                        title_font,
                        body_font,
                        clock,
                    )
                    if initials is None:
                        break

                    try:
                        saved, entries = save_score(initials, score)
                        heading = "SCORE SAVED!" if saved else "SCORE NOT SAVED"
                    except OSError as error:
                        print(f"Could not save leaderboard: {error}")
                        heading = "SAVE FAILED"
                else:
                    heading = "SCORE DID NOT QUALIFY"

            # Keep the final leaderboard on screen. The player can only quit.
            wait_for_quit(
                screen, entries, heading, title_font, body_font, clock
            )
            running = False

    finally:
        pygame.mouse.set_visible(True)
        pygame.quit()


if __name__ == "__main__":
    main()
