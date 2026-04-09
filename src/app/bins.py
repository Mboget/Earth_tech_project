import pygame

from app import constants as const


def create_bins(width, height, bin_width=180, bin_height=120, gap=20, margin=40):
    total_width = 3 * bin_width + 2 * gap
    right_start_x = width - total_width - margin
    left_start_x = margin
    y = (height - bin_height) // 2

    bins = []
    for i, (name, color) in enumerate(const.TRASH_TYPES):
        rect = pygame.Rect(right_start_x + i * (bin_width + gap), y, bin_width, bin_height)
        bins.append({"name": name, "color": color, "rect": rect})
    for i, (name, color) in enumerate(const.TRASH_TYPES):
        rect = pygame.Rect(left_start_x + i * (bin_width + gap), y, bin_width, bin_height)
        bins.append({"name": name, "color": color, "rect": rect})
    return bins


def draw_bins(screen, bins, font):
    for b in bins:
        if const.BIN_IMAGE:
            # Draw bin image
            bin_img = pygame.transform.scale(const.BIN_IMAGE, (b["rect"].width, b["rect"].height))
            screen.blit(bin_img, b["rect"])
            # Draw subtle border instead of thick black border for transparency
            pygame.draw.rect(screen, const.BLACK, b["rect"], 1)
        else:
            # Fallback to colored rectangle
            pygame.draw.rect(screen, b["color"], b["rect"])
            # Draw border
            pygame.draw.rect(screen, const.BLACK, b["rect"], 2)
        
        # Draw label
        label = font.render(b["name"], True, const.BLACK)
        label_rect = label.get_rect(center=(b["rect"].centerx, b["rect"].centery))
        screen.blit(label, label_rect)

