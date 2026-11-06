"""Score display and end-of-game screen."""

import pygame

from settings import BLACK, RED, WHITE, WINDOW_WIDTH, WINDOW_HEIGHT


def show_score(screen, score, font):
    """Display the current score in the top-left corner."""
    score_text = font.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(topleft=(20, 20))
    screen.blit(score_text, score_rect)


def show_end_screen(screen, score, message, font):
    """Display the game result and final score for two seconds."""
    screen.fill(BLACK)

    message_text = font.render(message, True, RED)
    score_text = font.render(f"Final score: {score}", True, WHITE)

    message_rect = message_text.get_rect(
        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)
    )
    score_rect = score_text.get_rect(
        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30)
    )

    screen.blit(message_text, message_rect)
    screen.blit(score_text, score_rect)
    pygame.display.flip()
    pygame.time.wait(2000)
