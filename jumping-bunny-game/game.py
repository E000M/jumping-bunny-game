import pygame
import sys
import os
import random

# Window & game config
SCREEN_W, SCREEN_H = 1024, 576
FPS = 60

# Image paths
BG_PATH = r"C:\Users\AG\Desktop\HOPA HOPA GAME\9259344.jpg"
BUNNY_PATH = r"C:\Users\AG\Desktop\HOPA HOPA GAME\pixelated-bunny-cute-and-friendly-png.png"
YOU_LOST_PATH = r"C:\Users\AG\Desktop\HOPA HOPA GAME\youlost_banner.png"

# Init
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Endless Jump Game")
clock = pygame.time.Clock()

# Image loading
def load_image(path, fallback_size=None):
    if not os.path.exists(path):
        s = pygame.Surface(fallback_size or (64, 64))
        s.fill((255, 0, 255))
        return s.convert_alpha()
    return pygame.image.load(path).convert_alpha()

def load_optional_image(path):
    if not os.path.exists(path):
        return None
    return pygame.image.load(path).convert_alpha()

bg_img = load_image(BG_PATH)
bg_img = pygame.transform.smoothscale(bg_img, (SCREEN_W, SCREEN_H))

bunny_img = load_image(BUNNY_PATH)
bunny_img = pygame.transform.smoothscale(bunny_img, (64, 64))

youlost_img_raw = load_optional_image(YOU_LOST_PATH)
youlost_img = None
if youlost_img_raw:
    iw, ih = youlost_img_raw.get_size()
    scale = min((SCREEN_W * 0.8) / iw, (SCREEN_H * 0.6) / ih)
    youlost_img = pygame.transform.scale(
        youlost_img_raw, (int(iw * scale), int(ih * scale))
    ).convert_alpha()

# Fonts
HUD_FONT = pygame.font.SysFont("arial", 28, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 22, bold=True)
BIG_LOSE_FONT = pygame.font.SysFont("arial", 80, bold=True)


# Player class (movement, jumping, gravity)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bunny_img
        self.rect = self.image.get_rect(centerx=x, bottom=y)

        self.vel_y = 0
        self.gravity = 2000
        self.jump_power = -750

        self.jumps_left = 2
        self.jump_key_released = True

        self.current_platform = None
        self.last_platform = None

    def update(self, dt, keys, skip_gravity=False):
        jump_input = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

        if jump_input:
            if self.jump_key_released and self.jumps_left > 0:
                if self.current_platform:
                    self.last_platform = self.current_platform
                    self.current_platform = None
                self.vel_y = self.jump_power
                self.jumps_left -= 1
            self.jump_key_released = False
        else:
            self.jump_key_released = True

        if not skip_gravity:
            self.vel_y += self.gravity * dt
            self.rect.y += int(self.vel_y * dt)
        else:
            self.vel_y = 0

    def landed(self, platform_top, p):
        self.rect.bottom = platform_top
        self.vel_y = 0
        self.jumps_left = 2
        self.current_platform = p

    def draw(self, surf):
        surf.blit(self.image, self.rect)


# Platform class
class Platform:
    def __init__(self, x, y, w=180, h=28):
        self.rect = pygame.Rect(x, y, w, h)

    def move_left(self, speed):
        self.rect.x -= speed

    def draw(self, surf):
        pygame.draw.rect(surf, (120, 75, 15), self.rect)
        pygame.draw.rect(surf, (80, 160, 60), (self.rect.x, self.rect.y, self.rect.w, 12))


# Platform generation rules
MAX_DOUBLE_JUMP_HEIGHT = 200
MIN_PLATFORM_Y = 240
MAX_PLATFORM_Y = SCREEN_H - 140
MIN_GAP = 120
MAX_GAP = 240

# Starting platforms
def make_start_platforms():
    return [
        Platform(80, SCREEN_H - 120, 220, 28),
        Platform(350, 420, 200, 28),
        Platform(650, 380, 200, 28),
        Platform(900, 450, 200, 28),
    ]

platforms = make_start_platforms()
start_plat = platforms[0]
player = Player(start_plat.rect.centerx, start_plat.rect.top)
player.current_platform = start_plat

# Game state
bg_x = 0
SCROLL_SPEED = 4
first_frame = True

score = 0
high_score = 0
lost = False
show_instructions = True


def reset_game():
    global platforms, player, bg_x, first_frame, lost, score, show_instructions

    platforms = make_start_platforms()
    s = platforms[0]
    player = Player(s.rect.centerx, s.rect.top)
    player.current_platform = s

    bg_x = 0
    first_frame = True
    lost = False
    score = 0
    show_instructions = True
    return player


# Main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000
    prev_bottom = player.rect.bottom
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if lost and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player = reset_game()

    # Lost screen
    if lost:
        screen.blit(bg_img, (bg_x, 0))
        screen.blit(bg_img, (bg_x + SCREEN_W, 0))

        for p in platforms: 
            p.draw(screen)
        player.draw(screen)

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        if youlost_img:
            r = youlost_img.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 20))
            screen.blit(youlost_img, r)
        else:
            txt = BIG_LOSE_FONT.render("YOU LOST", True, (0,0,0))
            screen.blit(txt, txt.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))

        restart = SMALL_FONT.render("Press space to restart", True, (255,255,255))
        screen.blit(restart, restart.get_rect(center=(SCREEN_W//2, SCREEN_H - 40)))
        pygame.display.flip()
        continue

    # Player logic
    player.update(dt, keys, skip_gravity=first_frame)

    # World scrolling
    if not first_frame:
        bg_x -= SCROLL_SPEED
        if bg_x <= -SCREEN_W:
            bg_x = 0

        for p in platforms:
            p.move_left(SCROLL_SPEED)

            if p.rect.right < 0:
                rightmost = max(platforms, key=lambda plat: plat.rect.right)

                new_x = rightmost.rect.right + random.randint(MIN_GAP, MAX_GAP)
                new_y = random.randint(MIN_PLATFORM_Y, MAX_PLATFORM_Y)

                if abs(new_y - rightmost.rect.y) > MAX_DOUBLE_JUMP_HEIGHT:
                    new_y = rightmost.rect.y + MAX_DOUBLE_JUMP_HEIGHT * (
                        1 if new_y > rightmost.rect.y else -1
                    )

                p.rect.x, p.rect.y = new_x, new_y

    first_frame = False

    # Platform collision
    landed_this_frame = False
    for p in platforms:
        plat_top = p.rect.top
        horiz = (player.rect.right > p.rect.left and player.rect.left < p.rect.right)
        crossed = (prev_bottom <= plat_top and player.rect.bottom >= plat_top)

        if player.vel_y >= 0 and horiz and crossed:
            if player.last_platform and player.last_platform is not p:
                score += 1
            player.last_platform = None
            player.landed(p.rect.top, p)
            landed_this_frame = True
            break

    if not landed_this_frame:
        if not any(player.rect.colliderect(p.rect) for p in platforms):
            player.current_platform = None

    # Fall off screen
    if player.rect.top > SCREEN_H:
        high_score = max(high_score, score)
        lost = True
        show_instructions = False
        continue

    # Draw world
    screen.blit(bg_img, (bg_x, 0))
    screen.blit(bg_img, (bg_x + SCREEN_W, 0))

    for p in platforms:
        p.draw(screen)
    player.draw(screen)

    # HUD
    screen.blit(HUD_FONT.render(f"Score: {score}", True, (0, 0, 0)), (10, 10))
    screen.blit(HUD_FONT.render(f"High Score: {high_score}", True, (0, 0, 0)), (10, 40))

    # Controls info
    if show_instructions:
        line1 = SMALL_FONT.render("Controls:", True, (0,0,0))
        line2 = SMALL_FONT.render("Space / W / Up = Jump", True, (0,0,0))
        r1 = line1.get_rect(topright=(SCREEN_W - 10, 10))
        r2 = line2.get_rect(topright=(SCREEN_W - 10, r1.bottom + 4))
        screen.blit(line1, r1)
        screen.blit(line2, r2)

    pygame.display.flip()

pygame.quit()
sys.exit()
