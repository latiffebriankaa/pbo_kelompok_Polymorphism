import os
import sys
from collections import Counter
import pygame
from pokemon import KartuCommon, KartuEpic, KartuRare, gacha_satu_kartu

WIDTH = 1100
HEIGHT = 700
FPS = 60

GRID_COLS = 5
GRID_ROWS = 2
CARD_W = 186
CARD_H = 214
CARD_GAP_X = 16
CARD_GAP_Y = 16
FLIP_DURATION = 420
FLIP_STAGGER = 120

BG_COLOR = (24, 31, 44)
PANEL_COLOR = (17, 22, 33)
PANEL_EDGE = (44, 54, 74)
TEXT_COLOR = (240, 243, 248)
MUTED_TEXT = (170, 180, 200)
BUTTON_COLOR = (53, 84, 134)
BUTTON_HOVER = (70, 112, 176)
CARD_BORDER = (230, 230, 235)
CARD_FACE = (245, 246, 250)
CARD_BACK = (43, 52, 72)
CARD_BACK_HIGHLIGHT = (70, 88, 126)

ASSET_DIR = os.path.join(os.path.dirname(__file__), "asset")
IMAGE_BY_RARITY = {
    "COMMON": ["bulasaur.jpg", "pikacuu.jpg", "squirtle.jpg"],
    "RARE": ["charizard rare.jpg"],
    "EPIC": ["charizard ultra rare.jpg", "mew.jpg"],
}


class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label

    def draw(self, surface, font, mouse_pos):
        color = BUTTON_HOVER if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, CARD_BORDER, self.rect, width=2, border_radius=10)

        text_surf = font.render(self.label, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def card_label(card):
    if isinstance(card, KartuCommon):
        return "COMMON"
    if isinstance(card, KartuRare):
        return "RARE"
    return "EPIC"


def load_image_library():
    image_library = {"COMMON": [], "RARE": [], "EPIC": []}

    for rarity, filenames in IMAGE_BY_RARITY.items():
        for filename in filenames:
            path = os.path.join(ASSET_DIR, filename)
            if os.path.exists(path):
                try:
                    image = pygame.image.load(path).convert()
                    image_library[rarity].append(image)
                except pygame.error:
                    pass

    return image_library


def stable_index(text, length):
    total = 0
    for char in text:
        total += ord(char)
    return total % length if length else 0


def prepare_card_image(card, image_library, size):
    rarity = card_label(card)
    choices = image_library.get(rarity, [])

    if not choices:
        return None

    selected = getattr(card, "_image_surface", None)
    if selected is None:
        selected = choices[stable_index(card.nama, len(choices))]
        setattr(card, "_image_surface", selected)

    return pygame.transform.smoothscale(selected, size)


def draw_card_frame(surface, rect, active=False):
    base_color = CARD_FACE if active else (234, 236, 241)
    pygame.draw.rect(surface, base_color, rect, border_radius=16)
    pygame.draw.rect(surface, CARD_BORDER, rect, width=2, border_radius=16)


def draw_card_back(surface, rect, scale=1.0):
    width = max(10, int(rect.width * scale))
    back_rect = pygame.Rect(0, 0, width, rect.height - 12)
    back_rect.center = rect.center
    pygame.draw.rect(surface, CARD_BACK, back_rect, border_radius=12)
    pygame.draw.rect(surface, CARD_BACK_HIGHLIGHT, back_rect.inflate(-12, -12), width=2, border_radius=10)


def draw_card_image(surface, card, rect, image_library, scale=1.0):
    image = prepare_card_image(card, image_library, (rect.width - 16, rect.height - 16))
    if image is None:
        fallback = pygame.Rect(0, 0, max(8, int(rect.width * scale)), rect.height - 16)
        fallback.center = rect.center
        pygame.draw.rect(surface, (60, 60, 70), fallback, border_radius=10)
        return

    draw_width = max(6, int(image.get_width() * scale))
    if draw_width <= 6:
        return

    scaled = pygame.transform.smoothscale(image, (draw_width, image.get_height()))
    image_rect = scaled.get_rect(center=rect.center)
    surface.blit(scaled, image_rect)


def draw_flip_card(surface, card, rect, image_library, now_ms, started_at_ms):
    elapsed = clamp(now_ms - started_at_ms, 0, FLIP_DURATION)
    progress = elapsed / FLIP_DURATION

    if progress < 0.5:
        scale = 1.0 - (progress / 0.5)
        draw_card_frame(surface, rect, active=True)
        draw_card_back(surface, rect, scale=scale)
    else:
        scale = (progress - 0.5) / 0.5
        draw_card_frame(surface, rect, active=False)
        draw_card_image(surface, card, rect, image_library, scale=scale)


def draw_static_card(surface, card, rect, image_library):
    draw_card_frame(surface, rect, active=False)
    draw_card_image(surface, card, rect, image_library, scale=1.0)


def draw_empty_slot(surface, rect):
    pygame.draw.rect(surface, (28, 35, 48), rect, border_radius=16)
    pygame.draw.rect(surface, (55, 67, 89), rect, width=2, border_radius=16)


def summarize(cards):
    rarity_count = Counter(card_label(c) for c in cards)
    return rarity_count["COMMON"], rarity_count["RARE"], rarity_count["EPIC"]


def run_app():
    pygame.init()
    pygame.display.set_caption("Gacha Kartu Pokemon - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("consolas", 30, bold=True)
    font_button = pygame.font.SysFont("consolas", 22, bold=True)
    font_body = pygame.font.SysFont("consolas", 18)
    font_caption = pygame.font.SysFont("consolas", 16)
    font_empty = pygame.font.SysFont("consolas", 18, bold=True)

    image_library = load_image_library()

    btn_single = Button((30, 84, 176, 44), "Single Pull")
    btn_multi = Button((220, 84, 176, 44), "Multi Pull")
    btn_clear = Button((410, 84, 160, 44), "Clear")
    btn_exit = Button((584, 84, 160, 44), "Keluar")

    cards = []
    flip_started_at = None
    status = "Tekan tombol atau keyboard: 1, 2, C, Esc"

    grid_width = GRID_COLS * CARD_W + (GRID_COLS - 1) * CARD_GAP_X
    grid_x = 45 + (1040 - grid_width) // 2
    grid_y = 230

    def start_pull(count):
        nonlocal cards, flip_started_at, status
        cards = [gacha_satu_kartu() for _ in range(count)]
        flip_started_at = pygame.time.get_ticks()
        status = f"Membuka {count} kartu..."

    def clear_cards():
        nonlocal cards, flip_started_at, status
        cards = []
        flip_started_at = None
        status = "Daftar kartu dibersihkan."

    running = True
    while running:
        now_ms = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    start_pull(1)
                elif event.key == pygame.K_2:
                    start_pull(10)
                elif event.key == pygame.K_c:
                    clear_cards()
                elif event.key == pygame.K_ESCAPE:
                    running = False

            if btn_single.clicked(event):
                start_pull(1)
            elif btn_multi.clicked(event):
                start_pull(10)
            elif btn_clear.clicked(event):
                clear_cards()
            elif btn_exit.clicked(event):
                running = False

        if cards and flip_started_at is not None:
            total_flip_time = FLIP_DURATION + FLIP_STAGGER * max(0, len(cards) - 1)
            if now_ms - flip_started_at >= total_flip_time:
                status = "Kartu berhasil dibuka."

        screen.fill(BG_COLOR)
        pygame.draw.circle(screen, (35, 45, 67), (980, 110), 110)
        pygame.draw.circle(screen, (27, 36, 55), (1000, 520), 120)

        title = font_title.render("GACHA KARTU POKEMON (POLYMORPHISM)", True, TEXT_COLOR)
        screen.blit(title, (30, 25))
        subtitle = font_caption.render("Image-only cards with sequential flip reveal", True, MUTED_TEXT)
        screen.blit(subtitle, (30, 57))

        btn_single.draw(screen, font_button, mouse_pos)
        btn_multi.draw(screen, font_button, mouse_pos)
        btn_clear.draw(screen, font_button, mouse_pos)
        btn_exit.draw(screen, font_button, mouse_pos)

        panel_rect = pygame.Rect(30, 145, 1040, 525)
        pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=18)
        pygame.draw.rect(screen, PANEL_EDGE, panel_rect, width=2, border_radius=18)

        status_surf = font_body.render(status, True, MUTED_TEXT)
        screen.blit(status_surf, (45, 160))

        c, r, e = summarize(cards)
        summary = f"Ringkasan: Common={c} | Rare={r} | Epic={e}"
        summary_surf = font_body.render(summary, True, TEXT_COLOR)
        screen.blit(summary_surf, (45, 185))

        hint_surf = font_caption.render("1 = single pull | 2 = multi pull | C = clear | Esc = keluar", True, MUTED_TEXT)
        screen.blit(hint_surf, (45, 206))

        shown_cards = cards[: GRID_COLS * GRID_ROWS]
        for idx in range(GRID_COLS * GRID_ROWS):
            row = idx // GRID_COLS
            col = idx % GRID_COLS
            rect = pygame.Rect(
                grid_x + col * (CARD_W + CARD_GAP_X),
                grid_y + row * (CARD_H + CARD_GAP_Y),
                CARD_W,
                CARD_H,
            )

            if idx >= len(shown_cards):
                draw_empty_slot(screen, rect)
                empty_label = font_empty.render("EMPTY", True, (98, 108, 125))
                screen.blit(empty_label, empty_label.get_rect(center=rect.center))
                continue

            card = shown_cards[idx]
            draw_delay_start = flip_started_at if flip_started_at is not None else now_ms
            card_started_at = draw_delay_start + idx * FLIP_STAGGER

            if now_ms < card_started_at:
                draw_empty_slot(screen, rect)
            elif now_ms < card_started_at + FLIP_DURATION:
                draw_flip_card(screen, card, rect, image_library, now_ms, card_started_at)
            else:
                draw_static_card(screen, card, rect, image_library)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_app()
