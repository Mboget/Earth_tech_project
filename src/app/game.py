import math
import sys

import pygame

from app import constants as const
from app.bins import create_bins, draw_bins
from app.space_game import run as run_space_game
from app.trajectory import predict_trajectory
from app.ui import create_close_rect, draw_close_button, draw_button
from app.waste_item import WasteItem


def _level_config(level):
    bin_width = max(120, 180 - (level - 1) * 10)
    bin_height = max(80, 120 - (level - 1) * 6)
    preview_steps = max(10, 30 - (level - 1) * 2)
    points_needed = 5 + (level - 1) * 3
    return bin_width, bin_height, preview_steps, points_needed


def run(screen, start_level=1, max_level=6, controls="wasd", two_players=False):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)
    big_font = pygame.font.SysFont("arial", 28, bold=True)
    win_font = pygame.font.SysFont("arial", 34, bold=True)

    width, height = screen.get_size()
    level = start_level
    level_points = 0
    bin_width, bin_height, preview_steps, points_needed = _level_config(level)
    bins = create_bins(width, height, bin_width=bin_width, bin_height=bin_height)
    left_bins = bins[3:]
    right_bins = bins[:3]
    left_cluster_right = max(b["rect"].right for b in left_bins)
    spawn_x = width // 2
    spawn_y = height // 2
    item = WasteItem(width, height, (spawn_x, spawn_y))
    score = 0
    aiming = False
    aim_start = pygame.Vector2(0, 0)
    aim_current = pygame.Vector2(0, 0)
    paused = False
    full_preview = False
    completed_level = start_level - 1
    level_stars = {}
    time_acc = 0.0
    base_bin_ys = [b["rect"].y for b in bins]
    bin_phases = [i * 0.8 for i in range(len(bins))]
    player_turn = 1

    while True:
        dt = clock.tick(const.FPS) / 1000.0
        if not paused:
            time_acc += dt
        width, height = screen.get_size()
        close_rect = create_close_rect(width, height)
        resume_rect = pygame.Rect(0, 0, 260, 60)
        quit_rect = pygame.Rect(0, 0, 260, 60)
        resume_rect.center = (width // 2, height // 2 - 20)
        quit_rect.center = (width // 2, height // 2 + 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused

            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                full_preview = not full_preview

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                if paused:
                    if resume_rect.collidepoint(event.pos):
                        paused = False
                    elif quit_rect.collidepoint(event.pos):
                        return completed_level, level_stars
                    continue
                if not item.launched:
                    mouse = pygame.Vector2(event.pos)
                    if mouse.distance_to(item.pos) <= item.radius + 8:
                        aiming = True
                        aim_start = mouse
                        aim_current = mouse

            if event.type == pygame.MOUSEMOTION and aiming:
                aim_current = pygame.Vector2(event.pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and aiming:
                aiming = False
                drag = aim_start - aim_current
                item.vel = drag * const.POWER
                item.launched = True

        if not paused:
            item.update(dt)

        # Check collision with bins
        if item.launched and not paused:
            for b in bins:
                if b["rect"].collidepoint(item.pos.x + item.radius, item.pos.y):
                    if item.kind == b["name"]:
                        score += 1
                        level_points += 1
                    else:
                        score -= 1
                        level_points = max(0, level_points - 1)
                    item.reset()
                    if two_players:
                        player_turn = 2 if player_turn == 1 else 1
                    break

        # Missed: hits the ground without any bin
        if item.launched and not paused and item.pos.y + item.radius >= height:
            score -= 1
            level_points = max(0, level_points - 1)
            item.reset()
            if two_players:
                player_turn = 2 if player_turn == 1 else 1

        # Reappear on the descending trajectory when leaving the top
        if item.launched and not paused and item.pos.y + item.radius < 0:
            a = 0.5 * const.GRAVITY
            b = item.vel.y
            c = item.pos.y
            disc = b * b - 4 * a * c
            if disc >= 0:
                sqrt_disc = math.sqrt(disc)
                t1 = (-b - sqrt_disc) / (2 * a)
                t2 = (-b + sqrt_disc) / (2 * a)
                t_candidates = [t for t in (t1, t2) if t > 0]
                if t_candidates:
                    t = max(t_candidates)
                    item.pos.x += item.vel.x * t
                    item.pos.y = 0
                    item.vel.y += const.GRAVITY * t
                else:
                    item.reset()
            else:
                item.reset()
                if two_players:
                    player_turn = 2 if player_turn == 1 else 1

        # Reset if out of bounds
        if item.pos.x < -50 or item.pos.x > width + 50 or item.pos.y > height + 50:
            item.reset()
            if two_players:
                player_turn = 2 if player_turn == 1 else 1

        # Level up
        if level_points >= points_needed:
            space_result, stars_collected = run_space_game(screen, level=level, controls=controls, two_players=two_players)
            if space_result != "completed":
                return completed_level, level_stars
            level_stars[level] = max(level_stars.get(level, 0), stars_collected)
            completed_level = max(completed_level, level)
            level += 1
            level_points = 0
            if level > max_level:
                # End of levels
                screen.fill(const.WHITE)
                msg = win_font.render("Bravo ! Tous les niveaux sont termines.", True, const.BLACK)
                screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 20))
                pygame.display.flip()
                pygame.time.delay(1500)
                return max_level, level_stars
            bin_width, bin_height, preview_steps, points_needed = _level_config(level)
            bins = create_bins(width, height, bin_width=bin_width, bin_height=bin_height)
            left_bins = bins[3:]
            right_bins = bins[:3]
            left_cluster_right = max(b["rect"].right for b in left_bins)
            spawn_x = width // 2
            spawn_y = height // 2
            item = WasteItem(width, height, (spawn_x, spawn_y))
            base_bin_ys = [b["rect"].y for b in bins]
            bin_phases = [i * 0.8 for i in range(len(bins))]
            player_turn = 1

        # Draw background or fill with white
        if const.BACKGROUND_IMAGE:
            bg_img = pygame.transform.scale(const.BACKGROUND_IMAGE, (width, height))
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(const.WHITE)

        # Moving bins on specific levels (example: from level 3)
        if level >= 3:
            amplitude = 60 + (level - 3) * 8
            speed = 1.6 + (level - 3) * 0.2
            for i, b in enumerate(bins):
                offset = int(amplitude * math.sin(time_acc * speed + bin_phases[i]))
                b["rect"].y = base_bin_ys[i] + offset

        # Trajectory preview (only up to first bin)
        if aiming and not paused:
            preview_vel = (aim_start - aim_current) * const.POWER
            points = predict_trajectory(item.pos, preview_vel, steps=preview_steps)
            if not full_preview:
                cutoff_left = max(b["rect"].right for b in left_bins)
                cutoff_x = min(b["rect"].left for b in right_bins)
                for p in points:
                    if p[0] <= cutoff_left or p[0] >= cutoff_x:
                        break
                    pygame.draw.circle(screen, const.GRAY, p, 3)
            else:
                for p in points:
                    pygame.draw.circle(screen, const.GRAY, p, 3)

        draw_bins(screen, bins, font)
        item.draw(screen)

        title = big_font.render("Sort the waste into the right bin!", True, const.BLACK)
        screen.blit(title, (20, 15))
        score_text = font.render(f"Score: {score}", True, const.BLACK)
        screen.blit(score_text, (20, 50))
        level_text = font.render(f"Level: {level} ({level_points}/{points_needed})", True, const.BLACK)
        screen.blit(level_text, (20, 80))
        if two_players:
            turn_text = big_font.render(f"Tour: Joueur {player_turn}", True, const.BLACK)
            screen.blit(turn_text, (width // 2 - turn_text.get_width() // 2, 15))
        hint = font.render("Click + drag the waste to launch it to the right (trajectory shown).", True, const.BLACK)
        screen.blit(hint, (20, height - 40))

        draw_close_button(screen, close_rect)

        # Pause overlay
        if paused:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            pause_title = big_font.render("Pause", True, const.WHITE)
            screen.blit(pause_title, (width // 2 - pause_title.get_width() // 2, height // 2 - 120))
            mouse_pos = pygame.mouse.get_pos()
            draw_button(screen, resume_rect, "Reprendre", font, hover=resume_rect.collidepoint(mouse_pos))
            draw_button(screen, quit_rect, "Quitter au menu", font, hover=quit_rect.collidepoint(mouse_pos))

        pygame.display.flip()
