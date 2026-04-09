import pygame
from pathlib import Path

FPS = 60
GRAVITY = 900.0  # pixels/s^2
POWER = 3.0

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
SPACE_BG = (14, 18, 30)
SPACE_ACCENT = (70, 90, 130)
STAR_COLOR = (255, 230, 120)
SHIP_COLOR = (240, 240, 240)

TRASH_TYPES = [
    ("bottles", (255, 200, 130)),
    ("plastic", (120, 200, 255)),
    ("bags", (200, 140, 220)),
]

# Asset paths
ASSET_DIR = Path(__file__).resolve().parent.parent.parent / "asset" / "images"

# ===== CONFIGURATION DES ASSETS =====
# Modifie simplement les chemins des fichiers ici pour chaque type de déchet
WASTE_FILES = {
    "bottles": "bottle.jpg",
    "plastic": "plastic bag.jpg",
    "bags": "trash bag.jpg",
}

BIN_FILE = "coubelle ouverte.jpg"
BACKGROUND_FILE = "background.jpg"
TURTLE_FILE = "turtlee.jpg"
# ===== FIN CONFIGURATION =====

# Load waste item images
WASTE_IMAGES = {}
for waste_type, filename in WASTE_FILES.items():
    path = ASSET_DIR / filename
    if path.exists():
        img = pygame.image.load(path)
        # Resize to width=36, keeping aspect ratio
        current_width, current_height = img.get_size()
        new_height = int(current_height * 36 / current_width)
        WASTE_IMAGES[waste_type] = pygame.transform.scale(img, (36, new_height))
    else:
        print(f"Warning: Waste image not found: {path}")
        WASTE_IMAGES[waste_type] = None

# Load bin image
bin_path = ASSET_DIR / BIN_FILE
if bin_path.exists():
    bin_img = pygame.image.load(bin_path)
    BIN_IMAGE = pygame.transform.scale(bin_img, (180, 120))
else:
    print(f"Warning: Bin image not found: {bin_path}")
    BIN_IMAGE = None

# Load background image
bg_path = ASSET_DIR / BACKGROUND_FILE
if bg_path.exists():
    BACKGROUND_IMAGE = pygame.image.load(bg_path)
else:
    print(f"Warning: Background image not found: {bg_path}")
    BACKGROUND_IMAGE = None

# Load turtle image for space game
turtle_path = ASSET_DIR / TURTLE_FILE
if turtle_path.exists():
    turtle_img = pygame.image.load(turtle_path)
    TURTLE_IMAGE = pygame.transform.scale(turtle_img, (48, 48))
else:
    print(f"Warning: Turtle image not found: {turtle_path}")
    TURTLE_IMAGE = None

