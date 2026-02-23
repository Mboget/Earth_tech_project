import pygame

from app import constants as const


def create_close_rect(width, height, size=28, margin=12):
    return pygame.Rect(width - margin - size, margin, size, size)


def draw_close_button(screen, rect):
    pygame.draw.rect(screen, (220, 60, 60), rect, border_radius=4)
    pygame.draw.line(screen, const.WHITE, rect.topleft, rect.bottomright, 3)
    pygame.draw.line(screen, const.WHITE, rect.topright, rect.bottomleft, 3)


def draw_button(screen, rect, text, font, hover=False):
    bg = (60, 120, 190) if not hover else (80, 150, 220)
    fg = const.WHITE
    pygame.draw.rect(screen, bg, rect, border_radius=6)
    pygame.draw.rect(screen, const.BLACK, rect, 2, border_radius=6)
    label = font.render(text, True, fg)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
