import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

COLORS = [RED, BLUE, GREEN, YELLOW]

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Color Match Shooter")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        pygame.draw.polygon(self.image, GREEN, [(15, 0), (0, 30), (30, 30)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 7
        
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE - 2, GRID_SIZE - 2))
        self.color = random.choice(COLORS)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -GRID_SIZE
        self.speed = 2
        self.move_phase = random.random() * 2 * math.pi  # Random starting phase
        
    def update(self):
        # Sinusoidal movement
        self.rect.x += math.sin(pygame.time.get_ticks() * 0.002 + self.move_phase) * 2
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - GRID_SIZE))
        self.rect.y += self.speed

class Game:
    def __init__(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.blocks = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.enemy_spawn_timer = 0
        
    def spawn_enemy(self):
        grid_x = random.randrange(GRID_WIDTH)
        x = grid_x * GRID_SIZE
        enemy = Enemy(x)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        
    def try_shift_blocks(self, grid_x, grid_y, direction):
        if not (0 <= grid_y < GRID_HEIGHT):
            return
        
        # Try to shift blocks in the given direction
        if direction < 0:  # Shift left
            if grid_x > 0 and self.blocks[grid_y][grid_x - 1] == 0:
                self.blocks[grid_y][grid_x - 1] = self.blocks[grid_y][grid_x]
                self.blocks[grid_y][grid_x] = 0
        elif direction > 0:  # Shift right
            if grid_x < GRID_WIDTH - 1 and self.blocks[grid_y][grid_x + 1] == 0:
                self.blocks[grid_y][grid_x + 1] = self.blocks[grid_y][grid_x]
                self.blocks[grid_y][grid_x] = 0

    def add_block(self, enemy, bullet):
        grid_x = enemy.rect.x // GRID_SIZE
        grid_y = enemy.rect.y // GRID_SIZE
        
        # Determine shift direction based on hit position
        hit_pos = bullet.rect.centerx
        enemy_center = enemy.rect.centerx
        shift_direction = -1 if hit_pos < enemy_center else 1
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            self.blocks[grid_y][grid_x] = enemy.color
            self.try_shift_blocks(grid_x, grid_y, shift_direction)
            
    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            # Check if line is full and all same color
            if all(self.blocks[y]):
                first_color = self.blocks[y][0]
                if all(color == first_color for color in self.blocks[y]):
                    lines_cleared += 1
                    # Remove the line
                    del self.blocks[y]
                    # Add new empty line at top
                    self.blocks.insert(0, [0 for _ in range(GRID_WIDTH)])
                else:
                    y -= 1
            else:
                y -= 1
        return lines_cleared
    
    def apply_gravity(self):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT-2, -1, -1):
                if self.blocks[y][x] and not self.blocks[y+1][x]:
                    self.blocks[y+1][x] = self.blocks[y][x]
                    self.blocks[y][x] = 0
        
    def check_game_over(self):
        return any(self.blocks[0])
        
    def update(self):
        if not self.game_over:
            self.all_sprites.update()
            
            # Spawn enemies
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= 45:  # Faster spawn rate
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
                
            # Check bullet collisions
            hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)
            for bullet, enemies_hit in hits.items():
                for enemy in enemies_hit:
                    self.add_block(enemy, bullet)
                    enemy.kill()
                    self.score += 50
            
            # Check enemies reaching bottom
            for enemy in list(self.enemies):
                if enemy.rect.bottom >= SCREEN_HEIGHT - GRID_SIZE:
                    grid_y = (enemy.rect.y + GRID_SIZE - 1) // GRID_SIZE - 1
                    if 0 <= grid_y < GRID_HEIGHT:
                        self.add_block(enemy, None)
                    enemy.kill()
            
            # Apply gravity and clear lines
            self.apply_gravity()
            lines_cleared = self.clear_lines()
            self.score += lines_cleared * 1000  # More points for color matches
            
            # Check game over
            if self.check_game_over():
                self.game_over = True
                
    def draw(self):
        screen.fill(BLACK)
        
        # Draw grid
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (30, 30, 30), (0, y), (SCREEN_WIDTH, y))
            
        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.blocks[y][x]:
                    pygame.draw.rect(screen, self.blocks[y][x],
                                   (x * GRID_SIZE, y * GRID_SIZE,
                                    GRID_SIZE - 2, GRID_SIZE - 2))
                    
        self.all_sprites.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if self.game_over:
            game_over_text = font.render('GAME OVER - Press R to Restart', True, WHITE)
            screen.blit(game_over_text,
                       (SCREEN_WIDTH//2 - game_over_text.get_width()//2,
                        SCREEN_HEIGHT//2))

def main():
    game = Game()
    running = True
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game.game_over:
                    bullet = Bullet(game.player.rect.centerx, game.player.rect.top)
                    game.bullets.add(bullet)
                    game.all_sprites.add(bullet)
                elif event.key == pygame.K_r and game.game_over:
                    game = Game()
        
        game.update()
        game.draw()
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()