import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
DARK_GREY = (50, 50, 50)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Player settings
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
PLAYER_JUMP_STRENGTH = 12
PLAYER_GRAVITY = 0.8
PLAYER_SPEED = 5
MAX_JUMPS = 2  # Allow double jump
PLAYER_HEALTH = 3  # Player health

# Enemy settings
ENEMY_SIZE = 30
ENEMY_SPEED = 3
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
ENEMY_FIRE_RATE = 2000  # milliseconds

# Collectible settings
COLLECTIBLE_SIZE = 20
COLLECTIBLE_POINTS = 10

# Platform settings
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
PLATFORM_GAP = 200
MAX_PLATFORMS = 10
MIN_PLATFORM_WIDTH = 50
MAX_PLATFORM_WIDTH = 150
MIN_PLATFORM_HEIGHT = 10
MAX_PLATFORM_HEIGHT = 40

# Projectile settings
PROJECTILE_WIDTH = 5
PROJECTILE_HEIGHT = 5
PROJECTILE_SPEED = 10

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("hypnos: the god of sleep v0.0.1")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont(None, 36) 

# Background color
background_color = DARK_GREY

# Collectible settings
COLLECTIBLE_WIDTH = 30
COLLECTIBLE_HEIGHT = 30
COLLECTIBLE_TIERS = {
    'common': {'points': 5},
    'rare': {'points': 10},
    'legendary': {'points': 20, 'boost': True}
}

BOOST_DURATION = 30  # seconds
BOOST_MULTIPLIER = 2

# Load images
player_image = pygame.image.load('player.png')
player_image = pygame.transform.scale(player_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

enemy_image = pygame.image.load('enemy.png')
enemy_image = pygame.transform.scale(enemy_image, (ENEMY_WIDTH, ENEMY_HEIGHT))

common_collectible_image = pygame.image.load('common_collectible.png')
common_collectible_image = pygame.transform.scale(common_collectible_image, (COLLECTIBLE_WIDTH, COLLECTIBLE_HEIGHT))

rare_collectible_image = pygame.image.load('rare_collectible.png')
rare_collectible_image = pygame.transform.scale(rare_collectible_image, (COLLECTIBLE_WIDTH, COLLECTIBLE_HEIGHT))

legendary_collectible_image = pygame.image.load('legendary_collectible.png')
legendary_collectible_image = pygame.transform.scale(legendary_collectible_image, (COLLECTIBLE_WIDTH, COLLECTIBLE_HEIGHT))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - PLATFORM_HEIGHT  # Ensure player spawns above the ground platform
        self.change_x = 0
        self.change_y = 0
        self.on_ground = False
        self.jumps_left = MAX_JUMPS
        self.shoot_delay = 500  # milliseconds
        self.last_shot_time = pygame.time.get_ticks()
        self.health = PLAYER_HEALTH
        self.max_y = self.rect.y
        self.score = 0  # Initialize the score attribute

    def update(self):
        self.gravity()
        self.rect.x += self.change_x
        self.rect.y += self.change_y

        # Check for collision with walls
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Check for collision with ground
        if self.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT:
            self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
            self.change_y = 0
            self.on_ground = True
            self.jumps_left = MAX_JUMPS

        # Track the maximum height reached
        if self.rect.y < self.max_y:
            self.max_y = self.rect.y

        # Check for falling to death
        if self.rect.y - self.max_y > 200:
            print("You just fell to death!")
            pygame.quit()
            exit()

    def gravity(self):
        if not self.on_ground:
            self.change_y += PLAYER_GRAVITY

    def jump(self):
        if self.jumps_left > 0:
            self.change_y = -PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.jumps_left -= 1

    def go_left(self):
        self.change_x = -PLAYER_SPEED

    def go_right(self):
        self.change_x = PLAYER_SPEED

    def stop(self):
        self.change_x = 0

    def shoot(self, target_x, target_y):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            projectile = Projectile(self.rect.centerx, self.rect.centery, target_x, target_y, RED)
            player_projectiles.add(projectile)
            all_sprites.add(projectile)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED])
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.change_x
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.change_x *= -1

        # Enemy shooting at intervals
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > ENEMY_FIRE_RATE:
            self.last_shot_time = now
            projectile = Projectile(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery, BLUE)
            enemy_projectiles.add(projectile)
            all_sprites.add(projectile)

# Collectible class
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, tier):
        super().__init__()
        if tier == 'common':
            self.image = common_collectible_image
        elif tier == 'rare':
            self.image = rare_collectible_image
        elif tier == 'legendary':
            self.image = legendary_collectible_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tier = tier
        self.points = COLLECTIBLE_TIERS[tier]['points']

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, color):
        super().__init__()
        self.image = pygame.Surface((PROJECTILE_WIDTH, PROJECTILE_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        angle = math.atan2(target_y - y, target_x - x)
        self.change_x = PROJECTILE_SPEED * math.cos(angle)
        self.change_y = PROJECTILE_SPEED * math.sin(angle)

    def update(self):
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Function to generate random platforms
def generate_random_platforms():
    platforms = pygame.sprite.Group()
    platform_y = SCREEN_HEIGHT - PLATFORM_HEIGHT
    while platform_y > -PLATFORM_HEIGHT:
        platform_width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
        platform_height = random.randint(MIN_PLATFORM_HEIGHT, MAX_PLATFORM_HEIGHT)
        platform_x = random.randint(0, SCREEN_WIDTH - platform_width)
        platform = Platform(platform_x, platform_y, platform_width, platform_height)
        platforms.add(platform)
        platform_y -= random.randint(PLATFORM_HEIGHT + 20, PLATFORM_GAP)
    return platforms

# Function to generate random platforms with enemies and collectibles
def generate_complex_platforms(enemies, collectibles):
    platforms = pygame.sprite.Group()
    platform_y = SCREEN_HEIGHT - PLATFORM_HEIGHT
    while platform_y > -PLATFORM_HEIGHT * 10:  # Generate more platforms for vertical level
        platform_width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
        platform_height = random.randint(MIN_PLATFORM_HEIGHT, MAX_PLATFORM_HEIGHT)
        platform_x = random.randint(0, SCREEN_WIDTH - platform_width)
        platform = Platform(platform_x, platform_y, platform_width, platform_height)
        platforms.add(platform)
        platform_y -= random.randint(PLATFORM_HEIGHT + 20, PLATFORM_GAP)

        # Randomly place enemies on platforms
        if random.random() < 0.3:  # 30% chance to spawn an enemy
            enemy = Enemy(random.randint(platform.rect.left, platform.rect.right - ENEMY_WIDTH), platform.rect.top - ENEMY_HEIGHT)
            enemies.add(enemy)

        # Randomly place collectibles on platforms
        if random.random() < 0.3:  # 30% chance to spawn a collectible
            tier = random.choice(list(COLLECTIBLE_TIERS.keys()))
            collectible = Collectible(random.randint(platform.rect.left, platform.rect.right - COLLECTIBLE_WIDTH), platform.rect.top - COLLECTIBLE_HEIGHT, tier)
            collectibles.add(collectible)

    return platforms

# Function to handle collisions between player and platforms
def handle_collisions(player, platforms):
    player.on_ground = False  # Reset on_ground status before checking collisions
    for platform in platforms:
        if player.rect.colliderect(platform.rect):
            if player.change_y > 0:
                player.rect.bottom = platform.rect.top
                player.on_ground = True
                player.change_y = 0
                player.jumps_left = MAX_JUMPS
            elif player.change_y < 0:
                player.rect.top = platform.rect.bottom
                player.change_y = 0

# Function to handle collisions between player and enemies
def handle_enemy_collisions(player, enemies):
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            print("Player hit an enemy!")
            player.health -= 1
            enemy.kill()
            if player.health <= 0:
                print("Player died!")
                pygame.quit()
                exit()

# Function to handle collisions between player and collectibles
def handle_collectible_collisions(player, collectibles):
    for collectible in collectibles:
        if player.rect.colliderect(collectible.rect):
            print("Player collected a", collectible.tier, "collectible!")
            player.score += collectible.points
            collectibles.remove(collectible)
            all_sprites.remove(collectible)

# Function to handle projectile collisions
def handle_projectile_collisions(projectiles, targets):
    for projectile in projectiles:
        for target in targets:
            if projectile.rect.colliderect(target.rect):
                print("Projectile hit a target!")
                target.kill()  # Remove the target
                projectile.kill()  # Remove the projectile
                create_explosion(target.rect.centerx, target.rect.centery)  # Create particle explosion

# Function to create a particle explosion
def create_explosion(x, y):
    for _ in range(20):  # Number of particles
        particle = Particle(x, y)
        particles.add(particle)
        all_sprites.add(particle)

# Particle class for explosion effect
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((3, 3))  # Small particle size
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.change_x = random.uniform(-2, 2)  # Random horizontal speed
        self.change_y = random.uniform(-2, 2)  # Random vertical speed
        self.lifetime = 20  # Lifetime of the particle

    def update(self):
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# Game loop
player = Player()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()
player_projectiles = pygame.sprite.Group()
enemy_projectiles = pygame.sprite.Group()
particles = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

platforms = generate_complex_platforms(enemies, collectibles)
all_sprites.add(player)
all_sprites.add(platforms)
all_sprites.add(enemies)
all_sprites.add(collectibles)

scroll_offset = 0
score = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_a:
                player.go_left()
            if event.key == pygame.K_d:
                player.go_right()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a and player.change_x < 0:
                player.stop()
            if event.key == pygame.K_d and player.change_x > 0:
                player.stop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                target_x, target_y = pygame.mouse.get_pos()
                player.shoot(target_x, target_y)

    # Update player
    player.update()

    # Update enemies
    enemies.update()

    # Update projectiles
    player_projectiles.update()
    enemy_projectiles.update()
    particles.update()

    # Handle collisions
    handle_collisions(player, platforms)
    handle_enemy_collisions(player, enemies)
    handle_collectible_collisions(player, collectibles)
    handle_projectile_collisions(player_projectiles, enemies)
    handle_projectile_collisions(enemy_projectiles, player)

    # Scroll screen with player
    if player.rect.top <= SCREEN_HEIGHT // 4:
        scroll_offset = SCREEN_HEIGHT // 4 - player.rect.top
        player.rect.top = SCREEN_HEIGHT // 4
        for sprite in all_sprites:
            if sprite != player:
                sprite.rect.y += scroll_offset

    # Update score based on height
    score = SCREEN_HEIGHT - player.max_y
    score_text = font.render(f"Score: {score}", True, WHITE)

    # Clear the screen with the background color
    screen.fill(background_color)

    # Draw sprites
    all_sprites.draw(screen)

    # Draw score
    screen.blit(score_text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
