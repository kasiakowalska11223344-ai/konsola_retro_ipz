# ghosts.py
import pygame
import random
from settings import *


class Ghost:
    def __init__(self, start_grid_x, start_grid_y, color, release_score, personality):
        self.start_grid_x = start_grid_x
        self.start_grid_y = start_grid_y

        pixel_x = start_grid_x * CELL_SIZE + CELL_SIZE // 2
        pixel_y = start_grid_y * CELL_SIZE + CELL_SIZE // 2

        self.pos = pygame.math.Vector2(pixel_x, pixel_y)
        self.color = color
        self.speed = 1.8
        self.release_score = release_score
        self.personality = personality

        self.frightened_timer = 0
        self.last_decision_tile = None

        self.rect = pygame.Rect(0, 0, CELL_SIZE - 4, CELL_SIZE - 4)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.directions = [
            pygame.math.Vector2(UP),
            pygame.math.Vector2(LEFT),
            pygame.math.Vector2(DOWN),
            pygame.math.Vector2(RIGHT)
        ]
        self.direction = pygame.math.Vector2(UP)

    def make_frightened(self, duration_frames):
        self.frightened_timer = duration_frames
        in_ghost_house = (10 * CELL_SIZE < self.pos.x < 18 * CELL_SIZE) and (
                    12 * CELL_SIZE < self.pos.y < 16 * CELL_SIZE)
        if not in_ghost_house:
            self.direction = -self.direction
            self.last_decision_tile = None

    def respawn(self):
        self.pos.x = self.start_grid_x * CELL_SIZE + CELL_SIZE // 2
        self.pos.y = self.start_grid_y * CELL_SIZE + CELL_SIZE // 2
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.direction = pygame.math.Vector2(UP)
        self.frightened_timer = 0
        self.last_decision_tile = None

    def get_target(self, player, blinky, mode):
        if mode == "scatter":
            if self.personality == "blinky":
                return pygame.math.Vector2(25 * CELL_SIZE, 0)
            elif self.personality == "pinky":
                return pygame.math.Vector2(2 * CELL_SIZE, 0)
            elif self.personality == "inky":
                return pygame.math.Vector2(27 * CELL_SIZE, 30 * CELL_SIZE)
            elif self.personality == "clyde":
                return pygame.math.Vector2(0, 30 * CELL_SIZE)

        if self.personality == "blinky":
            return pygame.math.Vector2(player.pos.x, player.pos.y)
        elif self.personality == "pinky":
            return player.pos + player.facing * (4 * CELL_SIZE)
        elif self.personality == "inky":
            pivot = player.pos + player.facing * (2 * CELL_SIZE)
            vec = pivot - blinky.pos
            return blinky.pos + vec * 2
        elif self.personality == "clyde":
            dist = self.pos.distance_to(player.pos)
            if dist > 8 * CELL_SIZE:
                return pygame.math.Vector2(player.pos.x, player.pos.y)
            else:
                return pygame.math.Vector2(0, 30 * CELL_SIZE)

    def update(self, walls, doors, score, player, blinky, mode):
        if self.frightened_timer > 0:
            self.frightened_timer -= 1

        grid_x = int(self.pos.x // CELL_SIZE)
        grid_y = int(self.pos.y // CELL_SIZE)
        current_tile = (grid_x, grid_y)

        in_tunnel = (grid_y == 14) and (grid_x < 6 or grid_x > 21)

        if self.frightened_timer > 0:
            current_speed = 1.0
        elif in_tunnel:
            current_speed = 0.8
        else:
            current_speed = self.speed

        cell_center_x = grid_x * CELL_SIZE + CELL_SIZE // 2
        cell_center_y = grid_y * CELL_SIZE + CELL_SIZE // 2

        is_centered_x = abs(self.pos.x - cell_center_x) <= current_speed
        is_centered_y = abs(self.pos.y - cell_center_y) <= current_speed

        if is_centered_x and is_centered_y and 0 < self.pos.x < WIDTH and self.last_decision_tile != current_tile:
            self.pos.x = cell_center_x
            self.pos.y = cell_center_y
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            self.last_decision_tile = current_tile

            valid_directions = []

            for dir_vec in self.directions:
                test_rect = self.rect.copy()
                test_rect.x += dir_vec.x * CELL_SIZE
                test_rect.y += dir_vec.y * CELL_SIZE

                current_obstacles = walls.copy()
                if score < self.release_score or dir_vec != pygame.math.Vector2(UP):
                    current_obstacles.extend(doors)

                if not any(test_rect.colliderect(wall) for wall in current_obstacles):
                    if dir_vec != -self.direction:
                        valid_directions.append(dir_vec)

            if len(valid_directions) == 0:
                valid_directions.append(-self.direction)

            in_ghost_house = (10 * CELL_SIZE < self.pos.x < 18 * CELL_SIZE) and (
                        12 * CELL_SIZE < self.pos.y < 16 * CELL_SIZE)

            if in_ghost_house:
                if score >= self.release_score:
                    target = pygame.math.Vector2(13.5 * CELL_SIZE, 11 * CELL_SIZE)
                else:
                    target = self.pos + self.direction * CELL_SIZE

                best_dir = min(valid_directions, key=lambda d: (self.pos + d * CELL_SIZE).distance_to(target))
                self.direction = best_dir

            elif self.frightened_timer > 0:
                self.direction = random.choice(valid_directions)
            else:
                target = self.get_target(player, blinky, mode)
                best_dir = min(valid_directions, key=lambda d: (self.pos + d * CELL_SIZE).distance_to(target))
                self.direction = best_dir

        active_walls = walls.copy()
        if score < self.release_score or self.direction != pygame.math.Vector2(UP):
            active_walls.extend(doors)

        self.pos.x += self.direction.x * current_speed
        self.rect.centerx = int(self.pos.x)
        for wall in active_walls:
            if self.rect.colliderect(wall):
                if self.direction.x > 0:
                    self.rect.right = wall.left
                elif self.direction.x < 0:
                    self.rect.left = wall.right
                self.pos.x = self.rect.centerx
                self.last_decision_tile = None

        self.pos.y += self.direction.y * current_speed
        self.rect.centery = int(self.pos.y)
        for wall in active_walls:
            if self.rect.colliderect(wall):
                if self.direction.y > 0:
                    self.rect.bottom = wall.top
                elif self.direction.y < 0:
                    self.rect.top = wall.bottom
                self.pos.y = self.rect.centery
                self.last_decision_tile = None

        if self.pos.x < -CELL_SIZE // 2:
            self.pos.x = WIDTH + CELL_SIZE // 2
        elif self.pos.x > WIDTH + CELL_SIZE // 2:
            self.pos.x = -CELL_SIZE // 2
        self.rect.centerx = int(self.pos.x)

    def draw(self, screen):
        cx, cy = int(self.pos.x), int(self.pos.y)
        r = CELL_SIZE // 2 - 2

        if self.frightened_timer > 0:
            if self.frightened_timer < 120 and (self.frightened_timer // 10) % 2 == 0:
                draw_color = WHITE
                feature_color = (255, 0, 0)
            else:
                draw_color = (33, 33, 255)
                feature_color = (255, 184, 174)
        else:
            draw_color = self.color

        pygame.draw.circle(screen, draw_color, (cx, cy - 2), r)
        body_rect = pygame.Rect(cx - r, cy - 2, r * 2, r + 2)
        pygame.draw.rect(screen, draw_color, body_rect)

        wave_width = (r * 2) // 3
        for i in range(3):
            wx = (cx - r) + i * wave_width
            wy = cy + r
            points = [
                (wx, wy),
                (wx + wave_width // 2, wy - 4),
                (wx + wave_width, wy)
            ]
            pygame.draw.polygon(screen, BLACK, points)

        if self.frightened_timer > 0:
            pygame.draw.circle(screen, feature_color, (cx - 3, cy - 3), 2)
            pygame.draw.circle(screen, feature_color, (cx + 3, cy - 3), 2)

            mouth_points = [
                (cx - 6, cy + 4),
                (cx - 3, cy + 2),
                (cx, cy + 4),
                (cx + 3, cy + 2),
                (cx + 6, cy + 4)
            ]
            pygame.draw.lines(screen, feature_color, False, mouth_points, 1)
        else:
            look_x = int(self.direction.x * 2)
            look_y = int(self.direction.y * 2)

            for offset_x in (-4, 4):
                eye_x = cx + offset_x
                eye_y = cy - 3
                pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 3)
                pygame.draw.circle(screen, (0, 0, 255), (eye_x + look_x, eye_y + look_y), 1)