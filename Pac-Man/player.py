# player.py
import pygame
import math
from settings import *


class Player:
    def __init__(self, start_grid_x, start_grid_y):
        pixel_x = start_grid_x * CELL_SIZE + CELL_SIZE / 2
        pixel_y = start_grid_y * CELL_SIZE + CELL_SIZE / 2

        self.pos = pygame.math.Vector2(pixel_x, pixel_y)
        self.direction = pygame.math.Vector2(0, 0)
        self.next_direction = pygame.math.Vector2(0, 0)
        self.facing = pygame.math.Vector2(LEFT)

        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(0, 0, CELL_SIZE - 4, CELL_SIZE - 4)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.score = 0

        self.mouth_angle = 0
        self.mouth_speed = 4

    def update(self, walls, doors, pellets, power_pellets):
        all_walls = walls + doors
        ate_power_pellet = False

        if self.next_direction != self.direction and self.next_direction.length() > 0:
            cell_center_x = (self.rect.centerx // CELL_SIZE) * CELL_SIZE + CELL_SIZE / 2
            cell_center_y = (self.rect.centery // CELL_SIZE) * CELL_SIZE + CELL_SIZE / 2
            turned = False

            if 0 < self.pos.x < WIDTH:
                if self.next_direction.y != 0 and abs(self.rect.centerx - cell_center_x) <= 3:
                    test_rect = self.rect.copy()
                    test_rect.centerx = cell_center_x
                    test_rect.y += self.next_direction.y * CELL_SIZE
                    if not any(test_rect.colliderect(wall) for wall in all_walls):
                        self.pos.x = cell_center_x
                        self.direction = self.next_direction
                        turned = True

                elif self.next_direction.x != 0 and abs(self.rect.centery - cell_center_y) <= 3:
                    test_rect = self.rect.copy()
                    test_rect.centery = cell_center_y
                    test_rect.x += self.next_direction.x * CELL_SIZE
                    if not any(test_rect.colliderect(wall) for wall in all_walls):
                        self.pos.y = cell_center_y
                        self.direction = self.next_direction
                        turned = True

            if not turned and self.direction.length() > 0 and self.next_direction == -self.direction:
                self.direction = self.next_direction

        old_pos = self.pos.copy()

        self.pos.x += self.direction.x * self.speed
        self.rect.centerx = int(self.pos.x)
        for wall in all_walls:
            if self.rect.colliderect(wall):
                if self.direction.x > 0:
                    self.rect.right = wall.left
                elif self.direction.x < 0:
                    self.rect.left = wall.right
                self.pos.x = self.rect.centerx

        self.pos.y += self.direction.y * self.speed
        self.rect.centery = int(self.pos.y)
        for wall in all_walls:
            if self.rect.colliderect(wall):
                if self.direction.y > 0:
                    self.rect.bottom = wall.top
                elif self.direction.y < 0:
                    self.rect.top = wall.bottom
                self.pos.y = self.rect.centery

        if self.pos.x < -CELL_SIZE // 2:
            self.pos.x = WIDTH + CELL_SIZE // 2
        elif self.pos.x > WIDTH + CELL_SIZE // 2:
            self.pos.x = -CELL_SIZE // 2
        self.rect.centerx = int(self.pos.x)

        collided_indices = self.rect.collidelistall(pellets)
        for i in sorted(collided_indices, reverse=True):
            del pellets[i]
            self.score += 10

        power_indices = self.rect.collidelistall(power_pellets)
        for i in sorted(power_indices, reverse=True):
            del power_pellets[i]
            self.score += 50
            ate_power_pellet = True

        if self.direction.length() > 0:
            self.facing = self.direction

        if self.pos != old_pos:
            self.mouth_angle += self.mouth_speed
            if self.mouth_angle >= 45 or self.mouth_angle <= 0:
                self.mouth_speed = -self.mouth_speed

        return ate_power_pellet

    def draw(self, screen):
        cx, cy = int(self.pos.x), int(self.pos.y)
        r = CELL_SIZE // 2 - 2

        pygame.draw.circle(screen, YELLOW, (cx, cy), r)

        if self.mouth_angle > 0:
            if self.facing == pygame.math.Vector2(RIGHT):
                base_angle = 0
            elif self.facing == pygame.math.Vector2(DOWN):
                base_angle = 90
            elif self.facing == pygame.math.Vector2(LEFT):
                base_angle = 180
            else:  # UP
                base_angle = 270

            rad1 = math.radians(base_angle - self.mouth_angle)
            rad2 = math.radians(base_angle + self.mouth_angle)

            p1 = (cx + (r + 2) * math.cos(rad1), cy + (r + 2) * math.sin(rad1))
            p2 = (cx + (r + 2) * math.cos(rad2), cy + (r + 2) * math.sin(rad2))

            pygame.draw.polygon(screen, BLACK, [(cx, cy), p1, p2])