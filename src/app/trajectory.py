import pygame

from app import constants as const


def predict_trajectory(start_pos, initial_vel, steps=30, step_dt=0.06):
    points = []
    pos = pygame.Vector2(start_pos)
    vel = pygame.Vector2(initial_vel)
    for _ in range(steps):
        vel.y += const.GRAVITY * step_dt
        pos += vel * step_dt
        points.append((int(pos.x), int(pos.y)))
    return points
