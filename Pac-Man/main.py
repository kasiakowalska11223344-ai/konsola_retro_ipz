# main.py
import pygame
import sys
from settings import *
from player import Player
from level import Level
from ghosts import Ghost
from sounds import SoundManager


class Game:
    def __init__(self):
        pygame.init()
        self.sounds = SoundManager()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.board_surface = pygame.Surface((WIDTH, HEIGHT))

        pygame.display.set_caption("Pac-Man w Pygame-CE")
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 56, bold=True)

        self.reset_game()

    def reset_game(self):
        self.level = Level("map.txt", "maze.png")
        self.player = Player(14, 23)

        self.blinky = Ghost(13, 14, (255, 0, 0), 0, "blinky")
        self.pinky = Ghost(14, 14, (255, 184, 255), 100, "pinky")
        self.inky = Ghost(12, 14, (0, 255, 255), 300, "inky")
        self.clyde = Ghost(15, 14, (255, 184, 82), 500, "clyde")

        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

        self.mode_schedule = [
            (7 * FPS, "scatter"),
            (20 * FPS, "chase"),
            (7 * FPS, "scatter"),
            (20 * FPS, "chase"),
            (5 * FPS, "scatter"),
            (999999, "chase")
        ]
        self.current_phase = 0
        self.mode_timer = 0
        self.ghost_mode = "scatter"

        self.game_over = False
        self.win = False

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                else:
                    if event.key == pygame.K_UP:
                        self.player.next_direction = pygame.math.Vector2(UP)
                    elif event.key == pygame.K_DOWN:
                        self.player.next_direction = pygame.math.Vector2(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.player.next_direction = pygame.math.Vector2(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.player.next_direction = pygame.math.Vector2(RIGHT)

    def update(self):
        if not self.game_over:
            any_frightened = any(g.frightened_timer > 0 for g in self.ghosts)
            if not any_frightened:
                self.mode_timer += 1
                duration, mode = self.mode_schedule[self.current_phase]
                if self.mode_timer >= duration:
                    self.mode_timer = 0
                    self.current_phase += 1
                    new_mode = self.mode_schedule[self.current_phase][1]

                    if new_mode != self.ghost_mode:
                        self.ghost_mode = new_mode
                        for ghost in self.ghosts:
                            ghost.direction = -ghost.direction

            pellets_before = len(self.level.pellets)

            ate_power = self.player.update(
                self.level.walls,
                self.level.doors,
                self.level.pellets,
                self.level.power_pellets
            )

            if len(self.level.pellets) < pellets_before:
                self.sounds.play_waka()

            if ate_power:
                self.sounds.play_power()
                self.ghost_eat_combo = 0
                for ghost in self.ghosts:
                    ghost.make_frightened(7 * FPS)

            for ghost in self.ghosts:
                ghost.update(
                    self.level.walls,
                    self.level.doors,
                    self.player.score,
                    self.player,
                    self.blinky,
                    self.ghost_mode
                )

                if self.player.rect.colliderect(ghost.rect):
                    if ghost.frightened_timer > 0:
                        self.sounds.play_eat_ghost()
                        self.ghost_eat_combo += 1
                        self.player.score += 200 * (2 ** (self.ghost_eat_combo - 1))
                        ghost.respawn()
                    else:
                        self.sounds.play_death()
                        self.game_over = True
                        self.win = False
                        break

            if len(self.level.pellets) == 0 and len(self.level.power_pellets) == 0:
                self.game_over = True
                self.win = True

    def draw(self):
        self.screen.fill(BLACK)

        self.board_surface.fill(BLACK)
        self.level.draw(self.board_surface)
        self.player.draw(self.board_surface)

        for ghost in self.ghosts:
            ghost.draw(self.board_surface)

        self.screen.blit(self.board_surface, (OFFSET_X, OFFSET_Y))
        pygame.draw.rect(self.screen, BLUE, (OFFSET_X - 2, OFFSET_Y - 2, WIDTH + 4, HEIGHT + 4), 2)

        score_text = self.font.render(f"WYNIK: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (40, 40))

        mode_str = "POŚCIG" if self.ghost_mode == "chase" else "ROZPROSZENIE"
        mode_color = (255, 80, 80) if self.ghost_mode == "chase" else (100, 255, 100)
        mode_text = self.font_small.render(f"TRYB: {mode_str}", True, mode_color)
        self.screen.blit(mode_text, (40, 80))

        if self.game_over:
            if self.win:
                text_str = "WYGRANA!"
                color = YELLOW
            else:
                text_str = "GAME OVER"
                color = (255, 0, 0)

            text = self.font_big.render(text_str, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))

            restart_text = self.font.render("SPACE aby zresetować", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35))

            bg_rect = text_rect.union(restart_rect).inflate(40, 40)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, color, bg_rect, 3)

            self.screen.blit(text, text_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()