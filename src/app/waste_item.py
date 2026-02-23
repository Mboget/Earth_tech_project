import random

import pygame

from app import constants as const


class WasteItem:
    def __init__(self, width, height, spawn_pos):
        self.width = width
        self.height = height
        self.spawn_pos = pygame.Vector2(spawn_pos)
        self.reset()

    def reset(self):
        self.kind, self.color = random.choice(const.TRASH_TYPES)
        self.radius = 18
        self.pos = pygame.Vector2(self.spawn_pos)
        self.vel = pygame.Vector2(0, 0)
        self.launched = False

    def update(self, dt):
        if self.launched:
            self.vel.y += const.GRAVITY * dt
            self.pos += self.vel * dt

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        pygame.draw.circle(screen, const.BLACK, self.pos, self.radius, 2)
