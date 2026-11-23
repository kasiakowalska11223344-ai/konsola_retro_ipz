"""Text-only game UI: score, results, leaderboard, and initials entry."""

import pygame

from settings import BLACK, RED, WHITE, WINDOW_WIDTH, WINDOW_HEIGHT, FPS

ACCENT = (255, 205, 70)
MUTED = (170, 170, 170)


def _draw_centered(screen, text, font, color, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y))
    screen.blit(surface, rect)


def show_score(screen, score, font):
    """Display the current score in the top-left corner."""
    score_text = font.render(f"SCORE: {score}", True, WHITE)
    screen.blit(score_text, score_text.get_rect(topleft=(20, 20)))


def draw_game_over(screen, score, message, title_font, body_font):
    """Draw the short result screen shown immediately after a round ends."""
    screen.fill(BLACK)
    _draw_centered(screen, message.upper(), title_font, RED, WINDOW_HEIGHT // 2 - 45)
    _draw_centered(
        screen,
        f"FINAL SCORE: {score}",
        body_font,
        WHITE,
        WINDOW_HEIGHT // 2 + 25,
    )
    pygame.display.flip()


def draw_leaderboard_rows(screen, entries, font, top=145):
    """Draw the current top ten, aligned in a centered column."""
    if not entries:
        _draw_centered(screen, "NO SCORES YET", font, MUTED, top + 12)
        return

    row_height = 32
    for rank, entry in enumerate(entries[:10], start=1):
        line = f"{rank:02d}.  {entry['initials']}  {entry['score']:06d}"
        _draw_centered(screen, line, font, WHITE, top + (rank - 1) * row_height)


def draw_save_prompt(screen, entries, score, selection, qualifies, title_font, body_font):
    """Draw leaderboard and the yes/no save prompt."""
    screen.fill(BLACK)
    _draw_centered(screen, "HIGH SCORES", title_font, ACCENT, 55)
    draw_leaderboard_rows(screen, entries, body_font, top=125)

    _draw_centered(screen, f"YOUR SCORE: {score}", body_font, WHITE, 490)
    qualification = "TOP 10: YOU QUALIFY" if qualifies else "TOP 10: SCORE TOO LOW"
    _draw_centered(screen, qualification, body_font, MUTED, 530)
    _draw_centered(screen, "SAVE YOUR SCORE?", body_font, WHITE, 575)

    yes_color = ACCENT if selection == "YES" else MUTED
    no_color = ACCENT if selection == "NO" else MUTED
    gap = 110
    center_x = WINDOW_WIDTH // 2
    yes_surface = body_font.render("YES", True, yes_color)
    no_surface = body_font.render("NO", True, no_color)
    screen.blit(yes_surface, yes_surface.get_rect(center=(center_x - gap, 620)))
    screen.blit(no_surface, no_surface.get_rect(center=(center_x + gap, 620)))
    _draw_centered(screen, "LEFT/RIGHT: CHOOSE   SPACE: CONFIRM", body_font, MUTED, 675)
    pygame.display.flip()


def draw_initials_entry(screen, entries, score, initials, selected_index, title_font, body_font):
    """Draw the leaderboard and three-letter initials selector."""
    screen.fill(BLACK)
    _draw_centered(screen, "NEW HIGH SCORE!", title_font, ACCENT, 55)
    draw_leaderboard_rows(screen, entries, body_font, top=125)
    _draw_centered(screen, f"YOUR SCORE: {score}", body_font, WHITE, 490)
    _draw_centered(screen, "ENTER YOUR INITIALS", body_font, WHITE, 535)

    letter_font = title_font
    spacing = 75
    center_x = WINDOW_WIDTH // 2
    for index, letter in enumerate(initials):
        color = ACCENT if index == selected_index else WHITE
        surface = letter_font.render(letter, True, color)
        x = center_x + (index - 1) * spacing
        screen.blit(surface, surface.get_rect(center=(x, 590)))

    _draw_centered(screen, "UP/DOWN: LETTER   LEFT/RIGHT: SLOT", body_font, MUTED, 640)
    _draw_centered(screen, "SPACE: SAVE   RETURN: QUIT", body_font, MUTED, 680)
    pygame.display.flip()


def draw_leaderboard_result(screen, entries, heading, title_font, body_font):
    """Draw the updated leaderboard after saving or declining a score."""
    screen.fill(BLACK)
    _draw_centered(screen, heading, title_font, ACCENT, 65)
    draw_leaderboard_rows(screen, entries, body_font, top=145)
    _draw_centered(screen, "BUTTON 1_2 / RETURN: QUIT", body_font, WHITE, 650)
    pygame.display.flip()
