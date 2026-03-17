import pygame
import sys

pygame.init()
sx = 1280
sy = 720
screen = pygame.display.set_mode((sx, sy))
pygame.display.set_caption("My First Pygame")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# 원의 초기 위치
x, y = 400, 300
radius = 50
speed = 15  # 프레임당 이동 거리

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed
        
    x = max(radius, min(sx - radius, x))
    y = max(radius, min(sy - radius, y))

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (x, y), 50)

    # FPS 표시
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, (0, 0, 0))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()