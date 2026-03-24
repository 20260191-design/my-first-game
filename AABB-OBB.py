import pygame
import sys
import math
from sprites import load_sprite   # ✅ 추가

pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Collision Display: Circle / AABB / OBB")

clock = pygame.time.Clock()

# 색상
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# 폰트
font = pygame.font.SysFont(None, 30)

# 🔥 스프라이트 목록
sprite_names = ["adventurer", "rocket", "stone", "sword"]
sprite_index = 0

def get_sprite(size):
    return load_sprite(sprite_names[sprite_index], size)

# 이동 가능한 사각형
player = pygame.Rect(100, 100, 80, 80)
speed = 5

# 중앙 고정 사각형 (회전)
center_rect_size = 100
center_rect = pygame.Rect(WIDTH // 2 - center_rect_size // 2, HEIGHT // 2 - center_rect_size // 2,
                          center_rect_size, center_rect_size)
center_angle = 0
rotation_speed = 0.5

# ✅ 초기 스프라이트 (둘 다 동일)
player_img = get_sprite((80, 80))
center_img = get_sprite((100, 100))


# --- SAT 충돌 감지 함수 ---
def project_polygon(axis, polygon):
    dots = [axis[0]*p[0] + axis[1]*p[1] for p in polygon]
    return min(dots), max(dots)

def normalize(v):
    length = math.hypot(v[0], v[1])
    return (v[0]/length, v[1]/length) if length != 0 else (0,0)

def get_axes(polygon):
    axes = []
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i+1) % len(polygon)]
        edge = (p2[0]-p1[0], p2[1]-p1[1])
        normal = (-edge[1], edge[0])
        axes.append(normalize(normal))
    return axes

def sat_collision(poly1, poly2):
    axes1 = get_axes(poly1)
    axes2 = get_axes(poly2)
    for axis in axes1 + axes2:
        min1, max1 = project_polygon(axis, poly1)
        min2, max2 = project_polygon(axis, poly2)
        if max1 < min2 or max2 < min1:
            return False
    return True


# --- 메인 루프 ---
running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ✅ S 키로 스프라이트 변경
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                sprite_index = (sprite_index + 1) % len(sprite_names)
                player_img = get_sprite((80, 80))
                center_img = get_sprite((100, 100))

    # 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= speed
    if keys[pygame.K_RIGHT]:
        player.x += speed
    if keys[pygame.K_UP]:
        player.y -= speed
    if keys[pygame.K_DOWN]:
        player.y += speed

    # 회전
    current_rotation_speed = rotation_speed * (3 if keys[pygame.K_z] else 1)
    center_angle += current_rotation_speed
    center_angle %= 360

    # --- 원형 충돌 ---
    p_center = player.center
    c_center = center_rect.center
    p_radius = player.width // 2
    c_radius = center_rect.width // 2
    dx = p_center[0] - c_center[0]
    dy = p_center[1] - c_center[1]
    distance = math.sqrt(dx*dx + dy*dy)
    circle_collision = distance <= (p_radius + c_radius)

    # --- OBB 계산 ---
    def rotate_point(point, center, angle):
        rad = math.radians(angle)
        x, y = point
        cx, cy = center
        x -= cx
        y -= cy
        x_new = x * math.cos(rad) - y * math.sin(rad)
        y_new = x * math.sin(rad) + y * math.cos(rad)
        return (x_new + cx, y_new + cy)

    cx, cy = center_rect.center
    w, h = center_rect.width, center_rect.height
    center_corners = [
        (cx - w/2, cy - h/2),
        (cx + w/2, cy - h/2),
        (cx + w/2, cy + h/2),
        (cx - w/2, cy + h/2),
    ]
    rotated_center = [rotate_point(pt, (cx, cy), center_angle) for pt in center_corners]

    px, py = player.topleft
    pw, ph = player.width, player.height
    player_corners = [
        (px, py),
        (px+pw, py),
        (px+pw, py+ph),
        (px, py+ph),
    ]

    obb_collision = sat_collision(player_corners, rotated_center)

    # --- AABB 충돌 ---
    aabb_collision = player.colliderect(center_rect)

    # --- 배경 ---
    if obb_collision or circle_collision or aabb_collision:
        bg_color = YELLOW
    else:
        bg_color = WHITE
    screen.fill(bg_color)

    # --- 🔥 이미지로 그리기 ---
    # 플레이어
    screen.blit(player_img, player.topleft)

    # 회전 오브젝트
    rotated_image = pygame.transform.rotate(center_img, center_angle)
    rot_rect = rotated_image.get_rect(center=center_rect.center)
    screen.blit(rotated_image, rot_rect.topleft)

    # --- 디버그 히트박스 ---
    pygame.draw.rect(screen, RED, player, 2)
    pygame.draw.circle(screen, BLUE, p_center, p_radius, 2)
    pygame.draw.circle(screen, BLUE, c_center, c_radius, 2)
    pygame.draw.polygon(screen, GREEN, rotated_center, 2)

    # --- 텍스트 ---
    circle_text = "Circle: HIT" if circle_collision else "Circle: ---"
    aabb_text = "AABB: HIT" if aabb_collision else "AABB: ---"
    obb_text = "OBB: HIT" if obb_collision else "OBB: ---"
    sprite_text = f"Sprite: {sprite_names[sprite_index]}"

    screen.blit(font.render(circle_text, True, BLUE), (10, 10))
    screen.blit(font.render(aabb_text, True, RED), (10, 35))
    screen.blit(font.render(obb_text, True, GREEN), (10, 60))
    screen.blit(font.render(sprite_text, True, BLACK), (10, 85))

    pygame.display.flip()

pygame.quit()
sys.exit()