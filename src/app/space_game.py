import math
import random
import sys

import pygame

from app import constants as const
from app.ui import create_close_rect, draw_button, draw_close_button


def _spawn_star(width, height, rng, wastes=None):
    """Spawn a star on the right side of the screen, avoiding overlaps with waste."""
    if wastes is None:
        wastes = []
    
    # Try up to 10 times to find a safe spawn position
    for _ in range(10):
        y = rng.randint(70, height - 70)
        x = width + rng.randint(40, 180)
        star_pos = pygame.Vector2(x, y)
        
        # Check distance from all existing waste (star radius 16 + waste radius ~24 = ~40 minimum)
        safe = True
        for waste in wastes:
            if star_pos.distance_to(waste["pos"]) < 70:
                safe = False
                break
        
        if safe:
            return {"pos": star_pos, "radius": 16}
    
    # Fallback: spawn at top if no safe position found
    return {"pos": pygame.Vector2(width + 100, 70), "radius": 16}


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

    # Timer-based level: survive for increasing time
    level_duration = 45 + level * 30  # 45s base + 30s per level
    elapsed_time = 0.0
    
    current_strength = 90 + level * 30
    current_variation = 20 + level * 10
    current_speed = current_strength
    current_timer = 0.0
    current_update_every = max(0.8, 2.5 - level * 0.2)
    max_waste_on_screen = min(10 + level * 2, 24)
    rng = random.Random()
    wastes = []
    for _ in range(max_waste_on_screen):
        wastes.append(_spawn_waste(width, height, rng))

    star_collected = 0
    star_spawned = [False, False, False]
    # Stars appear at specific time intervals
    star_times = [
        level_duration * 0.3,  # 30% of level time
        level_duration * 0.6,  # 60% of level time
        level_duration * 0.8,  # 80% of level time
    ]
    stars = []  # Will be populated when stars appear

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
            # Update timer and current speed
            elapsed_time += dt
            current_timer += dt
            if current_timer >= current_update_every:
                current_timer = 0.0
                target = current_strength + rng.uniform(-current_variation, current_variation)
                current_speed = max(40.0, min(220.0 + level * 25, target))

            # Update wastes - just maintain continuous flow
            remaining_wastes = []
            for waste in wastes:
                waste["pos"].x -= current_speed * dt
                if waste["pos"].x < -60:
                    # Replace with new waste
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

            if failed:
                screen.fill(const.SPACE_BG)
                if const.BACKGROUND_IMAGE:
                    bg = pygame.transform.scale(const.BACKGROUND_IMAGE, (width, height))
                    screen.blit(bg, (0, 0))
                msg = big_font.render("Collision ! Niveau rate.", True, const.SHIP_COLOR)
                screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 10))
                pygame.display.flip()
                pygame.time.delay(900)
                return "failed", star_collected

            # Keep enough waste on screen
            while len(wastes) < max_waste_on_screen:
                wastes.append(_spawn_waste(width, height, rng))

            # Check star appearances based on time
            for i, star_time in enumerate(star_times):
                if elapsed_time >= star_time and not star_spawned[i]:
                    star_spawned[i] = True
                    # Spawn star on the right side like waste, avoiding waste overlap
                    stars.append(_spawn_star(width, height, rng, wastes))

            # Update stars
            remaining_stars = []
            for star in stars:
                star["pos"].x -= current_speed * dt
                if star["pos"].x < -80:
                    # Star left the screen without being collected, it's lost
                    continue
                if any(
                    ship_pos.distance_to(star["pos"]) <= ship_radius + star["radius"]
                    for ship_pos in ship_positions
                ):
                    # Star was collected!
                    star_collected += 1
                else:
                    remaining_stars.append(star)
            stars = remaining_stars

            # Check level completion
            if elapsed_time >= level_duration:
                screen.fill(const.SPACE_BG)
                if const.BACKGROUND_IMAGE:
                    bg = pygame.transform.scale(const.BACKGROUND_IMAGE, (width, height))
                    screen.blit(bg, (0, 0))
                msg = big_font.render("Niveau spatial termine !", True, const.SHIP_COLOR)
                screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 10))
                pygame.display.flip()
                pygame.time.delay(900)
                return "completed", star_collected

        screen.fill(const.SPACE_BG)
        if const.BACKGROUND_IMAGE:
            bg = pygame.transform.scale(const.BACKGROUND_IMAGE, (width, height))
            screen.blit(bg, (0, 0))

        for waste in wastes:
            waste_img = const.WASTE_IMAGES.get(waste["kind"])
            if waste_img:
                rect = waste_img.get_rect(center=waste["pos"])
                screen.blit(waste_img, rect)
            else:
                # Fallback: draw circle if image not available
                pygame.draw.circle(screen, waste["color"], waste["pos"], waste["radius"])
                pygame.draw.circle(screen, const.SHIP_COLOR, waste["pos"], waste["radius"], 2)

        for star in stars:
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
            angle_degrees = math.degrees(angle)
            
            # Draw turtle if available, otherwise fallback to triangle
            if const.TURTLE_IMAGE is not None:
                rotated_turtle = pygame.transform.rotate(const.TURTLE_IMAGE, -angle_degrees)
                turtle_rect = rotated_turtle.get_rect(center=ship_pos)
                screen.blit(rotated_turtle, turtle_rect)
            else:
                # Fallback: draw triangle ship
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
        time_remaining = max(0, level_duration - elapsed_time)
        time_text = font.render(f"Temps restant: {int(time_remaining)}s", True, const.SHIP_COLOR)
        screen.blit(time_text, (20, 50))
        star_count = min(max(0, star_collected), 3)
        stars_text = font.render(f"Etoiles collectees: {star_count}/3", True, const.SHIP_COLOR)
        screen.blit(stars_text, (20, 80))
        layout = "WASD" if controls == "wasd" else "ZQSD"
        if two_players:
            hint = font.render("J1: " + layout + " | J2: fleches", True, const.SHIP_COLOR)
        else:
            hint = font.render(f"Deplace le vaisseau avec {layout} ou fleches.", True, const.SHIP_COLOR)
        screen.blit(hint, (20, height - 40))

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
