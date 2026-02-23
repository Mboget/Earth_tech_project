import math
import random
import sys

import pygame

from app import constants as const
from app.ui import create_close_rect, draw_button, draw_close_button


def _star_positions(width, height):
    return [
        pygame.Vector2(width * 0.18, height * 0.2),
        pygame.Vector2(width * 0.82, height * 0.3),
        pygame.Vector2(width * 0.6, height * 0.85),
    ]


def _spawn_waste(width, height, rng):
    kind, color = rng.choice(const.TRASH_TYPES)
    y = rng.randint(70, height - 70)
    x = width + rng.randint(40, 180)
    return {"pos": pygame.Vector2(x, y), "color": color, "radius": 24, "kind": kind}


def run(screen, level, controls="wasd", two_players=False):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)
    big_font = pygame.font.SysFont("arial", 28, bold=True)

    width, height = screen.get_size()
    ship_radius = 18
    thrust = 820.0
    drag = 2.4
    max_speed = 380.0
    if two_players:
        ship_positions = [
            pygame.Vector2(70, height // 3),
            pygame.Vector2(70, (height * 2) // 3),
        ]
        ship_velocities = [pygame.Vector2(0, 0), pygame.Vector2(0, 0)]
        ship_colors = [const.SHIP_COLOR, const.SPACE_ACCENT]
    else:
        ship_positions = [pygame.Vector2(70, height // 2)]
        ship_velocities = [pygame.Vector2(0, 0)]
        ship_colors = [const.SHIP_COLOR]

    waste_target = 12 + level * 4
    current_strength = 90 + level * 30
    current_variation = 20 + level * 10
    current_speed = current_strength
    current_timer = 0.0
    current_update_every = max(0.8, 2.5 - level * 0.2)
    max_waste_on_screen = min(10 + level * 2, 24)
    rng = random.Random()
    wastes = []
    for _ in range(min(max_waste_on_screen, waste_target)):
        wastes.append(_spawn_waste(width, height, rng))

    star_positions = _star_positions(width, height)
    star_collected = [False, False, False]
    star_visible = [False, False, False]
    thresholds = [
        max(1, math.ceil(waste_target * 0.3)),
        max(2, math.ceil(waste_target * 0.6)),
        max(3, math.ceil(waste_target * 0.75)),
    ]
    stars = [
        {"pos": pygame.Vector2(pos), "radius": 16}
        for pos in star_positions
    ]

    dodged_waste = 0
    paused = False
    failed = False

    while True:
        dt = clock.tick(const.FPS) / 1000.0
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                if paused:
                    if resume_rect.collidepoint(event.pos):
                        paused = False
                    elif quit_rect.collidepoint(event.pos):
                        return "quit"

        if not paused:
            keys = pygame.key.get_pressed()
            left_key = pygame.K_a if controls == "wasd" else pygame.K_q
            right_key = pygame.K_d
            up_key = pygame.K_w if controls == "wasd" else pygame.K_z
            down_key = pygame.K_s
            if two_players:
                acc1 = pygame.Vector2(0, 0)
                if keys[left_key]:
                    acc1.x -= thrust
                if keys[right_key]:
                    acc1.x += thrust
                if keys[up_key]:
                    acc1.y -= thrust
                if keys[down_key]:
                    acc1.y += thrust

                acc2 = pygame.Vector2(0, 0)
                if keys[pygame.K_LEFT]:
                    acc2.x -= thrust
                if keys[pygame.K_RIGHT]:
                    acc2.x += thrust
                if keys[pygame.K_UP]:
                    acc2.y -= thrust
                if keys[pygame.K_DOWN]:
                    acc2.y += thrust

                accs = [acc1, acc2]
            else:
                acc = pygame.Vector2(0, 0)
                if keys[pygame.K_LEFT] or keys[left_key]:
                    acc.x -= thrust
                if keys[pygame.K_RIGHT] or keys[right_key]:
                    acc.x += thrust
                if keys[pygame.K_UP] or keys[up_key]:
                    acc.y -= thrust
                if keys[pygame.K_DOWN] or keys[down_key]:
                    acc.y += thrust
                accs = [acc]

            for i, acc in enumerate(accs):
                ship_velocities[i] += acc * dt
                ship_velocities[i] *= max(0.0, 1.0 - drag * dt)
                if ship_velocities[i].length() > max_speed:
                    ship_velocities[i].scale_to_length(max_speed)
                ship_positions[i] += ship_velocities[i] * dt
                ship_positions[i].x = max(ship_radius, min(width - ship_radius, ship_positions[i].x))
                ship_positions[i].y = max(ship_radius, min(height - ship_radius, ship_positions[i].y))
            current_timer += dt
            if current_timer >= current_update_every:
                current_timer = 0.0
                target = current_strength + rng.uniform(-current_variation, current_variation)
                current_speed = max(40.0, min(220.0 + level * 25, target))

            remaining_wastes = []
            for waste in wastes:
                waste["pos"].x -= current_speed * dt
                if waste["pos"].x < -60:
                    dodged_waste += 1
                    if dodged_waste + len(remaining_wastes) < waste_target:
                        remaining_wastes.append(_spawn_waste(width, height, rng))
                    continue
                if any(
                    ship_pos.distance_to(waste["pos"]) <= ship_radius + waste["radius"]
                    for ship_pos in ship_positions
                ):
                    failed = True
                    break
                remaining_wastes.append(waste)
            wastes = remaining_wastes

            while len(wastes) < max_waste_on_screen and dodged_waste + len(wastes) < waste_target:
                wastes.append(_spawn_waste(width, height, rng))

            for i, threshold in enumerate(thresholds):
                if dodged_waste >= threshold:
                    star_visible[i] = True

            for i, star in enumerate(stars):
                if not star_visible[i] or star_collected[i]:
                    continue
                star["pos"].x -= current_speed * dt
                if star["pos"].x < -80:
                    if not star_collected[i]:
                        star_collected[i] = True
                    continue
                if any(
                    ship_pos.distance_to(star["pos"]) <= ship_radius + star["radius"]
                    for ship_pos in ship_positions
                ):
                    star_collected[i] = True

            if failed:
                screen.fill(const.SPACE_BG)
                msg = big_font.render("Collision ! Niveau rate.", True, const.SHIP_COLOR)
                screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 10))
                pygame.display.flip()
                pygame.time.delay(900)
                return "failed"

            if dodged_waste >= waste_target:
                screen.fill(const.SPACE_BG)
                msg = big_font.render("Niveau spatial termine !", True, const.SHIP_COLOR)
                screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 10))
                pygame.display.flip()
                pygame.time.delay(900)
                return "completed"

        screen.fill(const.SPACE_BG)

        for waste in wastes:
            pygame.draw.circle(screen, waste["color"], waste["pos"], waste["radius"])
            pygame.draw.circle(screen, const.SHIP_COLOR, waste["pos"], waste["radius"], 2)

        for i, star in enumerate(stars):
            if not star_visible[i] or star_collected[i]:
                continue
            points = []
            outer = 14
            inner = 6
            for p in range(10):
                angle = math.radians(p * 36 - 90)
                radius = outer if p % 2 == 0 else inner
                x = star["pos"].x + math.cos(angle) * radius
                y = star["pos"].y + math.sin(angle) * radius
                points.append((x, y))
            pygame.draw.polygon(screen, const.STAR_COLOR, points)
            pygame.draw.polygon(screen, const.SHIP_COLOR, points, 2)

        for ship_pos, ship_vel, ship_color in zip(ship_positions, ship_velocities, ship_colors):
            direction = ship_vel if ship_vel.length() > 1 else pygame.Vector2(1, 0)
            angle = math.atan2(direction.y, direction.x)
            tip = pygame.Vector2(
                ship_pos.x + math.cos(angle) * (ship_radius + 6),
                ship_pos.y + math.sin(angle) * (ship_radius + 6),
            )
            left = pygame.Vector2(
                ship_pos.x + math.cos(angle + 2.4) * ship_radius * 0.8,
                ship_pos.y + math.sin(angle + 2.4) * ship_radius * 0.8,
            )
            right = pygame.Vector2(
                ship_pos.x + math.cos(angle - 2.4) * ship_radius * 0.8,
                ship_pos.y + math.sin(angle - 2.4) * ship_radius * 0.8,
            )
            pygame.draw.polygon(screen, ship_color, [tip, left, right])
            pygame.draw.circle(screen, const.SPACE_BG, ship_pos, ship_radius - 6)
            pygame.draw.circle(screen, ship_color, ship_pos, ship_radius, 2)

        title = big_font.render(f"Vaisseau - Niveau {level}", True, const.SHIP_COLOR)
        screen.blit(title, (20, 15))
        waste_text = font.render(f"Dechets esquives: {dodged_waste}/{waste_target}", True, const.SHIP_COLOR)
        screen.blit(waste_text, (20, 50))
        star_count = sum(1 for s in star_collected if s)
        stars_text = font.render(f"Etoiles: {star_count}/3", True, const.SHIP_COLOR)
        screen.blit(stars_text, (20, 80))
        layout = "WASD" if controls == "wasd" else "ZQSD"
        if two_players:
            hint = font.render("J1: " + layout + " | J2: fleches", True, const.SHIP_COLOR)
        else:
            hint = font.render(f"Deplace le vaisseau avec {layout} ou fleches.", True, const.SHIP_COLOR)
        screen.blit(hint, (20, height - 40))
        current_text = font.render(f"Courant: {int(current_speed)}", True, const.SHIP_COLOR)
        screen.blit(current_text, (20, 110))

        draw_close_button(screen, close_rect)

        if paused:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            pause_title = big_font.render("Pause", True, const.SHIP_COLOR)
            screen.blit(pause_title, (width // 2 - pause_title.get_width() // 2, height // 2 - 120))
            mouse_pos = pygame.mouse.get_pos()
            draw_button(screen, resume_rect, "Reprendre", font, hover=resume_rect.collidepoint(mouse_pos))
            draw_button(screen, quit_rect, "Quitter au menu", font, hover=quit_rect.collidepoint(mouse_pos))

        pygame.display.flip()
