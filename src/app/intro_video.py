import os
import sys

import pygame


def _show_message(screen, text, seconds=1.8):
    width, height = screen.get_size()
    font = pygame.font.SysFont("arial", 22, bold=True)
    screen.fill((10, 10, 10))
    label = font.render(text, True, (240, 240, 240))
    screen.blit(label, (width // 2 - label.get_width() // 2, height // 2 - 10))
    pygame.display.flip()
    pygame.time.delay(int(seconds * 1000))


def play_intro(screen, video_path, show_missing=False):
    if not os.path.exists(video_path):
        if show_missing:
            _show_message(screen, f"Intro absente: {os.path.basename(video_path)}")
        return
    try:
        import cv2
    except Exception:
        if show_missing:
            _show_message(screen, "OpenCV manquant, intro ignoree.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        if show_missing:
            _show_message(screen, "Impossible d'ouvrir la video d'intro.")
        return

    clock = pygame.time.Clock()
    width, height = screen.get_size()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                cap.release()
                return

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    cap.release()
