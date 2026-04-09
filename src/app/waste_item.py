import random
import math

import pygame

from app import constants as const


class WasteItem:
    def __init__(self, width, height, spawn_pos):
        self.width = width
        self.height = height
        self.spawn_pos = pygame.Vector2(spawn_pos)
        self.rotation_angle = 0
        self.reset()

    def reset(self):
        self.kind, self.color = random.choice(const.TRASH_TYPES)
        self.radius = 18
        self.pos = pygame.Vector2(self.spawn_pos)
        self.vel = pygame.Vector2(0, 0)
        self.launched = False
        self.rotation_angle = 0
        self.image = const.WASTE_IMAGES.get(self.kind)

    def update(self, dt):
        if self.launched:
            self.vel.y += const.GRAVITY * dt
            self.pos += self.vel * dt
            
            # Rotate based on velocity
            if self.vel.length() > 0:
                self.rotation_angle += self.vel.length() * dt * 0.3

    def draw(self, screen):
        if self.image:
            # Draw image with rotation, preserving transparency
            try:
                rotated_img = pygame.transform.rotate(self.image, -self.rotation_angle)
                rect = rotated_img.get_rect(center=self.pos)
                screen.blit(rotated_img, rect)
            except Exception as e:
                # Fallback to circle if rotation fails
                print(f"Error rotating image: {e}")
                pygame.draw.circle(screen, self.color, self.pos, self.radius)
                pygame.draw.circle(screen, const.BLACK, self.pos, self.radius, 2)
        else:
            # Fallback to circle if image not loaded
            pygame.draw.circle(screen, self.color, self.pos, self.radius)
            pygame.draw.circle(screen, const.BLACK, self.pos, self.radius, 2)

