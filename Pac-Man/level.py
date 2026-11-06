# level.py
import pygame
from settings import *


class Level:
    def __init__(self, filename, bg_image_path):
        self.walls = []
        self.doors = []
        self.pellets = []
        self.power_pellets = []
        self.load_map(filename)

        self.bg_image = pygame.image.load(bg_image_path).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))

    def load_map(self, filename):
        with open(filename, 'r') as file:
            for y, line in enumerate(file):
                for x, char in enumerate(line.rstrip('\r\n')):
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    if char == 'X':
                        self.walls.append(rect)
                    elif char == '-':
                        self.doors.append(rect)
                    elif char == '.':
                        pellet_size = 4
                        pellet_rect = pygame.Rect(
                            x * CELL_SIZE + CELL_SIZE // 2 - pellet_size // 2,
                            y * CELL_SIZE + CELL_SIZE // 2 - pellet_size // 2,
                            pellet_size, pellet_size
                        )
                        self.pellets.append(pellet_rect)
                    elif char == 'o':
                        power_size = 12
                        power_rect = pygame.Rect(
                            x * CELL_SIZE + CELL_SIZE // 2 - power_size // 2,
                            y * CELL_SIZE + CELL_SIZE // 2 - power_size // 2,
                            power_size, power_size
                        )
                        self.power_pellets.append(power_rect)

    def draw(self, screen):
        screen.blit(self.bg_image, (0, 0))

        for door in self.doors:
            pygame.draw.rect(screen, (255, 184, 255), door)

        for pellet in self.pellets:
            pygame.draw.rect(screen, WHITE, pellet)

        for power_pellet in self.power_pellets:
            pygame.draw.circle(screen, WHITE, power_pellet.center, 6)