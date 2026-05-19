import pygame
import random
import math
from collections import deque

# =====================================================
# 설정
# =====================================================
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

TILE_SIZE = 32
MAP_COLS = 90
MAP_ROWS = 60

MAP_WIDTH = MAP_COLS * TILE_SIZE
MAP_HEIGHT = MAP_ROWS * TILE_SIZE

# 타일
EMPTY = 0
WALL = 1
FLOOR = 2
HALL = 3

# 색상
COLOR_BG = (20, 20, 30)
COLOR_WALL = (60, 60, 80)
COLOR_FLOOR = (170, 150, 110)
COLOR_HALL = (140, 120, 90)
COLOR_PLAYER = (80, 220, 120)
COLOR_ENEMY = (220, 80, 80)
COLOR_BULLET = (255, 240, 120)
COLOR_TEXT = (255, 255, 255)

# BSP
MIN_LEAF_SIZE = 16
HALL_WIDTH = 1

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Isaac Style Roguelike")
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 20)


# =====================================================
# 유틸
# =====================================================
def clamp(v, mn, mx):
    return max(mn, min(mx, v))


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


# =====================================================
# BSP 노드
# =====================================================
class BSPNode:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.left = None
        self.right = None
        self.room = None

    def is_leaf(self):
        return self.left is None and self.right is None

    def split(self):
        can_split_h = self.h >= MIN_LEAF_SIZE * 2
        can_split_v = self.w >= MIN_LEAF_SIZE * 2

        if not can_split_h and not can_split_v:
            return False

        if can_split_h and can_split_v:
            horizontal = random.random() < 0.5
        else:
            horizontal = can_split_h

        if horizontal:
            split = random.randint(MIN_LEAF_SIZE, self.h - MIN_LEAF_SIZE)

            self.left = BSPNode(self.x, self.y, self.w, split)
            self.right = BSPNode(self.x, self.y + split, self.w, self.h - split)

        else:
            split = random.randint(MIN_LEAF_SIZE, self.w - MIN_LEAF_SIZE)

            self.left = BSPNode(self.x, self.y, split, self.h)
            self.right = BSPNode(self.x + split, self.y, self.w - split, self.h)

        return True


# =====================================================
# 던전
# =====================================================
class Dungeon:
    def __init__(self):
        self.tilemap = [[WALL for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.rooms = []

    def generate(self):
        self.tilemap = [[WALL for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
        self.rooms.clear()

        root = BSPNode(1, 1, MAP_COLS - 2, MAP_ROWS - 2)

        queue = deque([root])

        MAX_ROOMS = 12

        while queue and len(queue) < MAX_ROOMS:
            node = queue.popleft()

            # 일정 확률로만 분할
            if random.random() < 0.75:
                if node.split():
                    queue.append(node.left)
                    queue.append(node.right)

        leaves = []
        self.collect_leaves(root, leaves)

        for leaf in leaves:
            self.create_room(leaf)

        self.connect_rooms(root)

    def collect_leaves(self, node, out):
        if node is None:
            return

        if node.is_leaf():
            out.append(node)
        else:
            self.collect_leaves(node.left, out)
            self.collect_leaves(node.right, out)

    def create_room(self, leaf):
        padding = 1

        max_room_size = 40

        room_w = random.randint(8, min(max_room_size, leaf.w - padding * 2))
        room_h = random.randint(8, min(max_room_size, leaf.h - padding * 2))

        room_x = leaf.x + random.randint(padding, leaf.w - room_w - padding)
        room_y = leaf.y + random.randint(padding, leaf.h - room_h - padding)

        leaf.room = (room_x, room_y, room_w, room_h)
        self.rooms.append(leaf.room)

        for y in range(room_y, room_y + room_h):
            for x in range(room_x, room_x + room_w):
                self.tilemap[y][x] = FLOOR

    def connect_rooms(self, node):
        if node is None or node.is_leaf():
            return

        self.connect_rooms(node.left)
        self.connect_rooms(node.right)

        room_a = self.get_room(node.left)
        room_b = self.get_room(node.right)

        if room_a and room_b:
            self.create_hall(room_a, room_b)

    def get_room(self, node):
        if node is None:
            return None

        if node.room:
            return node.room

        left_room = self.get_room(node.left)
        right_room = self.get_room(node.right)

        if left_room:
            return left_room

        return right_room

    def room_center(self, room):
        rx, ry, rw, rh = room
        return (rx + rw // 2, ry + rh // 2)

    def create_hall(self, room_a, room_b):
        ax, ay = self.room_center(room_a)
        bx, by = self.room_center(room_b)

        # 세로
        for y in range(min(ay, by), max(ay, by) + 1):
            for dx in range(-HALL_WIDTH, HALL_WIDTH + 1):
                tx = ax + dx

                if 0 <= tx < MAP_COLS and 0 <= y < MAP_ROWS:
                    if self.tilemap[y][tx] == WALL:
                        self.tilemap[y][tx] = HALL

        # 가로
        for x in range(min(ax, bx), max(ax, bx) + 1):
            for dy in range(-HALL_WIDTH, HALL_WIDTH + 1):
                ty = by + dy

                if 0 <= x < MAP_COLS and 0 <= ty < MAP_ROWS:
                    if self.tilemap[ty][x] == WALL:
                        self.tilemap[ty][x] = HALL

    def is_walkable(self, world_x, world_y):
        tx = int(world_x // TILE_SIZE)
        ty = int(world_y // TILE_SIZE)

        if tx < 0 or ty < 0 or tx >= MAP_COLS or ty >= MAP_ROWS:
            return False

        return self.tilemap[ty][tx] != WALL

    def draw(self, screen, camera_x, camera_y):
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):

                tile = self.tilemap[y][x]

                color = COLOR_WALL

                if tile == FLOOR:
                    color = COLOR_FLOOR
                elif tile == HALL:
                    color = COLOR_HALL

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        x * TILE_SIZE - camera_x,
                        y * TILE_SIZE - camera_y,
                        TILE_SIZE,
                        TILE_SIZE,
                    ),
                )


# =====================================================
# 플레이어
# =====================================================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.radius = 12
        self.speed = 4

        self.hp = 6

        self.shoot_delay = 200
        self.shoot_timer = 0

    def update(self, dungeon, dt, bullets, current_room, room_cleared):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed

        new_x = self.x + dx
        new_y = self.y + dy
        
        # ==========================================
        # 방 잠금 시스템
        # ==========================================
        if current_room and not room_cleared:

            current_tx = int(self.x // TILE_SIZE)
            current_ty = int(self.y // TILE_SIZE)

            next_tx = int(new_x // TILE_SIZE)
            next_ty = int(new_y // TILE_SIZE)

            # 현재는 방 안인데 다음 위치가 통로면 막기
            current_tile = dungeon.tilemap[current_ty][current_tx]
            next_tile = dungeon.tilemap[next_ty][next_tx]

            if current_tile == FLOOR and next_tile == HALL:
                new_x = self.x
                new_y = self.y

        if dungeon.is_walkable(new_x, self.y):
            self.x = new_x

        if dungeon.is_walkable(self.x, new_y):
            self.y = new_y

        self.shoot_timer -= dt

        shoot_dx = 0
        shoot_dy = 0

        if keys[pygame.K_UP]:
            shoot_dy = -1
        elif keys[pygame.K_DOWN]:
            shoot_dy = 1
        elif keys[pygame.K_LEFT]:
            shoot_dx = -1
        elif keys[pygame.K_RIGHT]:
            shoot_dx = 1

        if (shoot_dx != 0 or shoot_dy != 0) and self.shoot_timer <= 0:
            bullets.append(
                Bullet(
                    self.x,
                    self.y,
                    shoot_dx,
                    shoot_dy,
                    current_room,
                    dungeon.tilemap[player_ty][player_tx],
                )
            )

            self.shoot_timer = self.shoot_delay

    def draw(self, screen, camera_x, camera_y):
        pygame.draw.circle(
            screen,
            COLOR_PLAYER,
            (
                int(self.x - camera_x),
                int(self.y - camera_y),
            ),
            self.radius,
        )


# =====================================================
# 적
# =====================================================
class Enemy:
    def __init__(self, x, y, room):
        self.x = x
        self.y = y
        self.room = room

        self.radius = 12
        self.speed = 1.5

        self.hp = 3
        self.dead = False

    def update(self, player, dungeon):
        player_tx = int(player.x // TILE_SIZE)
        player_ty = int(player.y // TILE_SIZE)

        rx, ry, rw, rh = self.room

        # 플레이어가 같은 방에 없으면 추적 안함
        if not (
            rx <= player_tx <= rx + rw
            and ry <= player_ty <= ry + rh
        ):
            return
        
        dx = player.x - self.x
        dy = player.y - self.y

        dist = math.hypot(dx, dy)

        if dist > 0:
            dx /= dist
            dy /= dist

        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if dungeon.is_walkable(new_x, self.y):
            self.x = new_x

        if dungeon.is_walkable(self.x, new_y):
            self.y = new_y

    def draw(self, screen, camera_x, camera_y):
        pygame.draw.circle(
            screen,
            COLOR_ENEMY,
            (
                int(self.x - camera_x),
                int(self.y - camera_y),
            ),
            self.radius,
        )


# =====================================================
# 총알
# =====================================================
class Bullet:
    def __init__(self, x, y, dx, dy, room, start_tile):
        self.x = x
        self.y = y

        self.dx = dx
        self.dy = dy
        
        self.room = room
        self.start_tile = start_tile

        self.speed = 8
        self.radius = 5

        self.dead = False

    def update(self, dungeon, enemies):
        global gold
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        if self.room:

            bullet_tx = int(self.x // TILE_SIZE)
            bullet_ty = int(self.y // TILE_SIZE)

            rx, ry, rw, rh = self.room

            if not (
                rx <= bullet_tx <= rx + rw
                and ry <= bullet_ty <= ry + rh
            ):
                self.dead = True
                return
        
        # 통로에서 쏜 총알은 통로 밖으로 못 나감
        if self.start_tile == HALL:

            bullet_tx = int(self.x // TILE_SIZE)
            bullet_ty = int(self.y // TILE_SIZE)

            if dungeon.tilemap[bullet_ty][bullet_tx] != HALL:
                self.dead = True
                return

        if not dungeon.is_walkable(self.x, self.y):
            self.dead = True
            return

        for enemy in enemies:
            if enemy.dead:
                continue

            d = distance(self.x, self.y, enemy.x, enemy.y)

            if d < self.radius + enemy.radius:
                enemy.hp -= 1
                self.dead = True

                if enemy.hp <= 0:
                    enemy.dead = True
                    gold += 3

                break

    def draw(self, screen, camera_x, camera_y):
        pygame.draw.circle(
            screen,
            COLOR_BULLET,
            (
                int(self.x - camera_x),
                int(self.y - camera_y),
            ),
            self.radius,
        )


# =====================================================
# 게임 생성
# =====================================================
dungeon = Dungeon()
dungeon.generate()

start_room = dungeon.rooms[0]
rx, ry, rw, rh = start_room

player = Player(
    (rx + rw // 2) * TILE_SIZE,
    (ry + rh // 2) * TILE_SIZE,
)

gold = 0
bullets = []
enemies = []

# 적 생성
for room in dungeon.rooms[1:]:

    rx, ry, rw, rh = room

    # 방마다 2~5마리
    enemy_count = random.randint(2, 5)

    for _ in range(enemy_count):

        ex = random.randint(rx + 1, rx + rw - 2) * TILE_SIZE
        ey = random.randint(ry + 1, ry + rh - 2) * TILE_SIZE

        enemies.append(Enemy(ex, ey, room))


# =====================================================
# 메인 루프
# =====================================================
running = True

while running:
    dt = clock.tick(FPS)

    # 이벤트
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:

                dungeon.generate()

                start_room = dungeon.rooms[0]
                rx, ry, rw, rh = start_room

                player.x = (rx + rw // 2) * TILE_SIZE
                player.y = (ry + rh // 2) * TILE_SIZE

                bullets.clear()
                enemies.clear()

                for room in dungeon.rooms[1:]:
                    rx, ry, rw, rh = room

                    ex = random.randint(rx + 1, rx + rw - 2) * TILE_SIZE
                    ey = random.randint(ry + 1, ry + rh - 2) * TILE_SIZE

                    enemies.append(Enemy(ex, ey, room))

    # 카메라
    camera_x = player.x - SCREEN_WIDTH // 2
    camera_y = player.y - SCREEN_HEIGHT // 2

    camera_x = clamp(camera_x, 0, MAP_WIDTH - SCREEN_WIDTH)
    camera_y = clamp(camera_y, 0, MAP_HEIGHT - SCREEN_HEIGHT)

    # 현재 플레이어 위치 타일
    player_tx = int(player.x // TILE_SIZE)
    player_ty = int(player.y // TILE_SIZE)

    current_room = None
    in_hallway = False

    # 먼저 방 검사
    for room in dungeon.rooms:
        rx, ry, rw, rh = room

        if (
            rx <= player_tx <= rx + rw
            and ry <= player_ty <= ry + rh
        ):
            current_room = room
            break

    # 방이 아닐 때만 통로 처리
    if current_room is None:
        if dungeon.tilemap[player_ty][player_tx] == HALL:
            in_hallway = True
            
    # 현재 방의 살아있는 적 확인
    room_cleared = True

    if current_room:

        for enemy in enemies:

            if enemy.room == current_room and not enemy.dead:
                room_cleared = False
                break
        
    player.update(
        dungeon,
        dt,
        bullets,
        current_room,
        room_cleared,
    )

    for enemy in enemies:
        enemy.update(player, dungeon)

    for bullet in bullets:
        bullet.update(dungeon, enemies)

    bullets = [b for b in bullets if not b.dead]
    enemies = [e for e in enemies if not e.dead]
    
    # 렌더링
    screen.fill(COLOR_BG)

    dungeon.draw(screen, camera_x, camera_y)

    for bullet in bullets:
        bullet.draw(screen, camera_x, camera_y)

    for enemy in enemies:
        enemy.draw(screen, camera_x, camera_y)

    player.draw(screen, camera_x, camera_y)
    
    # ==========================================
    # 그림자 시스템
    # ==========================================
    shadow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 220))

    # 통로 시야
    if in_hallway:

        pygame.draw.circle(
            shadow,
            (0, 0, 0, 0),
            (
                int(player.x - camera_x),
                int(player.y - camera_y),
            ),
            TILE_SIZE * 3,
        )

    # 방 시야
    elif current_room:

        rx, ry, rw, rh = current_room

        room_screen_x = rx * TILE_SIZE - camera_x
        room_screen_y = ry * TILE_SIZE - camera_y

        room_screen_w = rw * TILE_SIZE
        room_screen_h = rh * TILE_SIZE

        pygame.draw.rect(
            shadow,
            (0, 0, 0, 0),
            (
                room_screen_x,
                room_screen_y,
                room_screen_w,
                room_screen_h,
            ),
        )

    screen.blit(shadow, (0, 0))

    ui = font.render(
        f"HP: {player.hp}  GOLD: {gold}  ENEMIES: {len(enemies)}   [R] 새 던전",
        True,
        COLOR_TEXT,
    )

    screen.blit(ui, (20, 20))

    pygame.display.flip()

pygame.quit()
