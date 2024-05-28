import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_COLOR = GREEN
PLAYER_JUMP_STRENGTH = 15
PLAYER_GRAVITY = 1

# Enemy settings
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
ENEMY_COLOR = RED
ENEMY_SPEED = 3

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platformer")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
        self.change_x = 0
        self.change_y = 0
        self.on_ground = False

    def update(self):
        self.gravity()
        self.rect.x += self.change_x
        self.rect.y += self.change_y

        # Check for collision with ground
        if self.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT:
            self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
            self.change_y = 0
            self.on_ground = True

    def gravity(self):
        if not self.on_ground:
            self.change_y += PLAYER_GRAVITY

    def jump(self):
        if self.on_ground:
            self.change_y = -PLAYER_JUMP_STRENGTH
            self.on_ground = False

    def go_left(self):
        self.change_x = -5

    def go_right(self):
        self.change_x = 5

    def stop(self):
        self.change_x = 0

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = ENEMY_SPEED

    def update(self):
        self.rect.x += self.change_x
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.change_x *= -1

# Initialize player and enemy groups
all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Create some enemies
for i in range(5):
    enemy = Enemy(random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH), random.randint(0, SCREEN_HEIGHT - ENEMY_HEIGHT))
    all_sprites.add(enemy)
    enemy_sprites.add(enemy)

# Game loop
running = True
score = 0
font = pygame.font.SysFont(None, 36)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                player.go_left()
            if event.key == pygame.K_d:
                player.go_right()
            if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a and player.change_x < 0:
                player.stop()
            if event.key == pygame.K_d and player.change_x > 0:
                player.stop()

    # Update all sprites
    all_sprites.update()

    # Check for collisions between player and enemies
    enemy_hits = pygame.sprite.spritecollide(player, enemy_sprites, True)
    if enemy_hits:
        score += 10

    # Calculate score based on height
    height_score = SCREEN_HEIGHT - player.rect.y
    total_score = score + height_score

    # Draw everything
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Draw the score
    score_text = font.render(f"Score: {total_score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Flip the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()