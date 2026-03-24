import pygame
from sprites import load_sprite

pygame.init()

# 화면 크기
WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("스프라이트 일렬 출력")

clock = pygame.time.Clock()

# 스프라이트 로드 (크기 통일)
sprites = [
    load_sprite("rocket", (60, 160)),
    load_sprite("adventurer", (80, 110)),
    load_sprite("stone", (70, 70)),
    load_sprite("sword", (70, 70)),
]

# 위치 설정
spacing = 150  # 간격
start_x = 50   # 시작 위치

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 🔥 검정 배경
    screen.fill((0, 0, 0))

    # 🔥 일렬로 출력
    for i, sprite in enumerate(sprites):
        x = start_x + i * spacing
        y = HEIGHT // 2 - sprite.get_height() // 2
        screen.blit(sprite, (x, y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()