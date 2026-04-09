import sys

import pygame

from app import constants as const
from app.ui import create_close_rect, draw_button, draw_close_button


def run(screen):
    width, height = screen.get_size()
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("arial", 36, bold=True)
    button_font = pygame.font.SysFont("arial", 26, bold=True)

    play_rect = pygame.Rect(0, 0, 260, 60)
    duo_rect = pygame.Rect(0, 0, 260, 60)
    levels_rect = pygame.Rect(0, 0, 260, 60)
    controls_rect = pygame.Rect(0, 0, 260, 60)
    quit_rect = pygame.Rect(0, 0, 260, 60)
    play_rect.center = (width // 2, height // 2 - 105)
    duo_rect.center = (width // 2, height // 2 - 35)
    levels_rect.center = (width // 2, height // 2 + 35)
    controls_rect.center = (width // 2, height // 2 + 105)
    quit_rect.center = (width // 2, height // 2 + 175)

    while True:
        dt = clock.tick(const.FPS) / 1000.0
        _ = dt
        width, height = screen.get_size()
        close_rect = create_close_rect(width, height)

        mouse_pos = pygame.mouse.get_pos()
        hover_play = play_rect.collidepoint(mouse_pos)
        hover_duo = duo_rect.collidepoint(mouse_pos)
        hover_levels = levels_rect.collidepoint(mouse_pos)
        hover_controls = controls_rect.collidepoint(mouse_pos)
        hover_quit = quit_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                if play_rect.collidepoint(event.pos):
                    return "play_solo"
                if duo_rect.collidepoint(event.pos):
                    return "play_duo"
                if levels_rect.collidepoint(event.pos):
                    return "levels"
                if controls_rect.collidepoint(event.pos):
                    return "controls"
                if quit_rect.collidepoint(event.pos):
                    return "quit"

        # Draw background or fill with white
        if const.BACKGROUND_IMAGE:
            bg_img = pygame.transform.scale(const.BACKGROUND_IMAGE, (width, height))
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(const.WHITE)

        title = title_font.render("Waste Sorter", True, const.BLACK)
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 140))

        draw_button(screen, play_rect, "Jouer Solo", button_font, hover=hover_play)
        draw_button(screen, duo_rect, "Jouer a 2", button_font, hover=hover_duo)
        draw_button(screen, levels_rect, "Niveaux", button_font, hover=hover_levels)
        draw_button(screen, controls_rect, "Controles", button_font, hover=hover_controls)
        draw_button(screen, quit_rect, "Quitter", button_font, hover=hover_quit)
        draw_close_button(screen, close_rect)

        pygame.display.flip()


def run_level_select(screen, max_level, unlocked_level, level_stars=None):
    if level_stars is None:
        level_stars = {}
    width, height = screen.get_size()
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("arial", 32, bold=True)
    button_font = pygame.font.SysFont("arial", 22, bold=True)

    cols = 3
    button_w = 140
    button_h = 50
    gap = 20
    total_w = cols * button_w + (cols - 1) * gap
    start_x = (width - total_w) // 2
    start_y = height // 2 - 60

    back_rect = pygame.Rect(0, 0, 180, 50)
    back_rect.center = (width // 2, height // 2 + 120)

    level_rects = []
    for i in range(max_level):
        row = i // cols
        col = i % cols
        x = start_x + col * (button_w + gap)
        y = start_y + row * (button_h + gap)
        rect = pygame.Rect(x, y, button_w, button_h)
        level_rects.append(rect)

    while True:
        dt = clock.tick(const.FPS) / 1000.0
        _ = dt
        width, height = screen.get_size()
        close_rect = create_close_rect(width, height)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                if back_rect.collidepoint(event.pos):
                    return "back"
                for i, rect in enumerate(level_rects, start=1):
                    if rect.collidepoint(event.pos):
                        if i <= unlocked_level:
                            return i

        # Draw background or fill with white
        if const.BACKGROUND_IMAGE:
            bg_img = pygame.transform.scale(const.BACKGROUND_IMAGE, (width, height))
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(const.WHITE)

        title = title_font.render("Choisir un niveau", True, const.BLACK)
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 140))

        for i, rect in enumerate(level_rects, start=1):
            locked = i > unlocked_level
            hover = rect.collidepoint(mouse_pos) and not locked
            stars = level_stars.get(str(i), level_stars.get(i, 0))
            label = f"Niveau {i}"
            if stars > 0 and not locked:
                label = f"Niveau {i} ({stars}★)"
            if locked:
                label = f"Niveau {i} (lock)"
            draw_button(screen, rect, label, button_font, hover=hover)
            if locked:
                pygame.draw.rect(screen, (120, 120, 120), rect, 3, border_radius=6)

        draw_button(screen, back_rect, "Retour", button_font, hover=back_rect.collidepoint(mouse_pos))
        draw_close_button(screen, close_rect)

        pygame.display.flip()


def run_controls(screen, current_controls="wasd"):
    width, height = screen.get_size()
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("arial", 32, bold=True)
    button_font = pygame.font.SysFont("arial", 22, bold=True)
    info_font = pygame.font.SysFont("arial", 20)

    wasd_rect = pygame.Rect(0, 0, 260, 60)
    zqsd_rect = pygame.Rect(0, 0, 260, 60)
    back_rect = pygame.Rect(0, 0, 180, 50)
    wasd_rect.center = (width // 2, height // 2 - 40)
    zqsd_rect.center = (width // 2, height // 2 + 30)
    back_rect.center = (width // 2, height // 2 + 120)

    while True:
        dt = clock.tick(const.FPS) / 1000.0
        _ = dt
        width, height = screen.get_size()
        close_rect = create_close_rect(width, height)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                if back_rect.collidepoint(event.pos):
                    return "back"
                if wasd_rect.collidepoint(event.pos):
                    return "wasd"
                if zqsd_rect.collidepoint(event.pos):
                    return "zqsd"

        # Draw background or fill with white
        if const.BACKGROUND_IMAGE:
            bg_img = pygame.transform.scale(const.BACKGROUND_IMAGE, (width, height))
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(const.WHITE)

        title = title_font.render("Choix des controles", True, const.BLACK)
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 140))

        wasd_label = "WASD (QWERTY)"
        zqsd_label = "ZQSD (AZERTY)"
        draw_button(screen, wasd_rect, wasd_label, button_font, hover=wasd_rect.collidepoint(mouse_pos))
        draw_button(screen, zqsd_rect, zqsd_label, button_font, hover=zqsd_rect.collidepoint(mouse_pos))
        draw_button(screen, back_rect, "Retour", button_font, hover=back_rect.collidepoint(mouse_pos))
        draw_close_button(screen, close_rect)

        current = "WASD" if current_controls == "wasd" else "ZQSD"
        info = info_font.render(f"Actuel: {current}", True, const.BLACK)
        screen.blit(info, (width // 2 - info.get_width() // 2, height // 2 - 90))

        pygame.display.flip()
