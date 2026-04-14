import pygame
import random
import sys
import math

pygame.init()


def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)


WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GRAY    = (20,  20,  40)
BLUE    = (50,  150, 255)
RED     = (220, 50,  50)
YELLOW  = (240, 220, 0)
GREEN   = (50,  220, 80)
ORANGE  = (240, 140, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 레벨 설정 ---
LEVELS = [
    {"enemy_speed": 2, "spawn": 60, "label": "Lv.1"},
    {"enemy_speed": 3, "spawn": 40, "label": "Lv.2"},
    {"enemy_speed": 5, "spawn": 25, "label": "Lv.3"},
]

# --- 사운드 자리 ---
# shoot_sound    = pygame.mixer.Sound("shoot.wav")
# explosion_sound= pygame.mixer.Sound("explosion.wav")
# hit_sound      = pygame.mixer.Sound("hit.wav")

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 44, 44
BULLET_W, BULLET_H = 6,  14

def draw_player(surf, rect, angle):
    cx, cy = rect.center

    # 삼각형 기본 좌표 (위쪽을 바라보는 기준)
    points = [
        (0, -20),
        (-15, 15),
        (0, 8),
        (15, 15),
    ]

    rotated = []
    for x, y in points:
        rx = x * math.cos(angle) - y * math.sin(angle)
        ry = x * math.sin(angle) + y * math.cos(angle)
        rotated.append((cx + rx, cy + ry))

    pygame.draw.polygon(surf, BLUE, rotated)

    # 🔥 엔진 불꽃 (직사각형)
    flame_w = 6
    flame_h = 14

    flame_surf = pygame.Surface((flame_w, flame_h), pygame.SRCALPHA)

    # 불꽃 색 (겉/속 이중으로 하면 더 예쁨)
    pygame.draw.rect(flame_surf, ORANGE, (0, 0, flame_w, flame_h))
    pygame.draw.rect(flame_surf, YELLOW, (1, 1, flame_w-2, flame_h-2))
    
    angle_corrected = angle + math.pi / 2

    # 플레이어 반대 방향으로 회전
    rotated_flame = pygame.transform.rotate(
        flame_surf,
        -math.degrees(angle_corrected) + 90
    )

    # 플레이어 뒤쪽 위치 계산
    offset = 18
    fx = cx + math.cos(angle_corrected) * offset
    fy = cy + math.sin(angle_corrected) * offset

    rect = rotated_flame.get_rect(center=(fx, fy))
    surf.blit(rotated_flame, rect)

def draw_enemy(surf, en):
    rect = en["rect"]
    angle = en["angle"] + math.pi / 2

    # 기본 삼각형 (위쪽 기준)
    points = [
        (0, -28),
        (-18, 18),
        (0, 10),
        (18, 18),
    ]

    cx, cy = rect.center
    rotated = []

    for x, y in points:
        rx = x * math.cos(angle) - y * math.sin(angle)
        ry = x * math.sin(angle) + y * math.cos(angle)
        rotated.append((cx + rx, cy + ry))

    pygame.draw.polygon(surf, RED, rotated)
    

def spawn_enemy(level_cfg, player):
    side = random.choice(["top", "bottom", "left", "right"])

    if side == "top":
        x = random.randint(0, WIDTH - ENEMY_W)
        y = -ENEMY_H

    elif side == "bottom":
        x = random.randint(0, WIDTH - ENEMY_W)
        y = HEIGHT

    elif side == "left":
        x = -ENEMY_W
        y = random.randint(0, HEIGHT - ENEMY_H)

    else:  # right
        x = WIDTH
        y = random.randint(0, HEIGHT - ENEMY_H)
    
    # 🔥 플레이어 방향 계산
    dx = player.centerx - (x + ENEMY_W // 2)
    dy = player.centery - (y + ENEMY_H // 2)
    angle = math.atan2(dy, dx)

    speed = level_cfg["enemy_speed"]
    
    return {
        "rect": pygame.Rect(x, y, ENEMY_W, ENEMY_H),
        "dx": math.cos(angle) * speed,
        "dy": math.sin(angle) * speed,
        "angle": angle
    }

def draw_stars(stars):
    for s in stars:
        pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2])

def draw_hud(score, lives, level_cfg):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))
    screen.blit(font.render(level_cfg["label"], True, YELLOW), (WIDTH // 2 - 25, 10))

def game_over_screen(score):
    screen.fill((10, 10, 30))
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

def get_bullet_radius(score):
    return 3 + score // 100

def get_bullet_radius(score):
    return min(12, 3 + score // 100)

def get_bullet_speed(score):
    return min(20, 8 + score // 80)

def get_shoot_delay(score):
    return max(3, 15 - score // 100)

def main():
    player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 70, PLAYER_W, PLAYER_H)
    bullets  = []
    enemies  = []
    score    = 0
    lives    = 3
    shoot_cd = 0
    spawn_timer = 0
    level_idx = 0
    level_cfg = LEVELS[level_idx]
    invincible = 0

    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2))
             for _ in range(80)]
    
    
    while True:
        clock.tick(FPS)
        
        mx, my = pygame.mouse.get_pos()
        dx = mx - player.centerx
        dy = my - player.centery
        angle = math.atan2(dy, dx)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.left > 0:
            player.x -= 6
        if keys[pygame.K_d] and player.right < WIDTH:
            player.x += 6
        if keys[pygame.K_w] and player.top > 0:
            player.y -= 6
        if keys[pygame.K_s] and player.bottom < HEIGHT:
            player.y += 6

        shoot_cd -= 1
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            
            speed = get_bullet_speed(score)
            
            tip_offset = 20  # 삼각형 끝까지 거리 (draw_player에서 쓴 값과 비슷하게)

            bx = player.centerx + math.cos(angle) * tip_offset
            by = player.centery + math.sin(angle) * tip_offset
            # shoot_sound.play()
            b = {
                "x": bx,
                "y": by,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "angle": angle
            }
            bullets.append(b)
            shoot_cd = get_shoot_delay(score)

        bullets = [b for b in bullets if 0 < b["x"] < WIDTH and 0 < b["y"] < HEIGHT]
        for b in bullets:
            b["x"] += b["dx"]
            b["y"] += b["dy"]

        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            enemies.append(spawn_enemy(level_cfg, player))

        alive_enemies = []
        for en in enemies:
            en["rect"].x += en["dx"]
            en["rect"].y += en["dy"]

            if (-ENEMY_W < en["rect"].x < WIDTH + ENEMY_W and
                -ENEMY_H < en["rect"].y < HEIGHT + ENEMY_H):
                alive_enemies.append(en)
            
        enemies = alive_enemies

        hit_bullets = set()
        hit_enemies = set()
        for bi, b in enumerate(bullets):
            for ei, en in enumerate(enemies):
                bw = 6 + score // 50
                bh = 14 + score // 30
                bullet_rect = pygame.Rect(
                    b["x"] - bw // 2,
                    b["y"] - bh // 2,
                    bw,
                    bh
                )
                
                if bullet_rect.colliderect(en["rect"]):
                    # explosion_sound.play()
                    hit_bullets.add(bi)
                    hit_enemies.add(ei)
                    score += 10
        bullets  = [b  for i, b  in enumerate(bullets)  if i not in hit_bullets]
        enemies  = [en for i, en in enumerate(enemies)   if i not in hit_enemies]

        level_idx = min(score // 50, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]

        if invincible > 0:
            invincible -= 1
        else:
            for en in enemies:
                if player.colliderect(en["rect"]):
                    # hit_sound.play()
                    lives -= 1
                    invincible = 90
                    enemies.clear()
                    if lives <= 0:
                        if game_over_screen(score):
                            main()
                        return
                    break

        for s in stars:
            s = list(s)

        screen.fill(GRAY)
        draw_stars(stars)

        for b in bullets:
            w = 6 + score // 50   # 너비 (점점 커짐)
            h = 14 + score // 30  # 높이 (점점 커짐)

            bullet_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(bullet_surf, YELLOW, (0, 0, w, h))

            rotated = pygame.transform.rotate(bullet_surf, -math.degrees(b["angle"]+80.1))

            rect = rotated.get_rect(center=(b["x"], b["y"]))
            screen.blit(rotated, rect)

        for en in enemies:
            draw_enemy(screen, en)

        blink = (invincible // 10) % 2 == 0
        if blink:
            draw_player(screen, player, angle + math.pi / 2)

        draw_hud(score, lives, level_cfg)
        pygame.display.flip()
    

main()