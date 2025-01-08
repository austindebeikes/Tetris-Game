import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 900
TETRIS_WIDTH = 300
GALAGA_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 30
TETRIS_COLS = TETRIS_WIDTH // GRID_SIZE
TETRIS_ROWS = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 50, 50)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(20, 0), (0, 40), (40, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = TETRIS_WIDTH + GALAGA_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 8
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > TETRIS_WIDTH:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10
        
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Block(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.is_red = random.choice([True, False])  # Randomly choose block type
        self.image = pygame.Surface((GRID_SIZE - 2, GRID_SIZE - 2))
        self.image.fill(RED if self.is_red else BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -GRID_SIZE
        self.speed = 2
        
    def update(self):
        self.rect.y += self.speed

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Shooter")
        self.clock = pygame.time.Clock()
        
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.bullets = pygame.sprite.Group()
        self.falling_blocks = pygame.sprite.Group()
        self.tetris_grid = [[0 for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]
        self.game_over = False
        self.spawn_timer = 0
        self.score = 0

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over:
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                    elif event.key == pygame.K_r and self.game_over:
                        self.__init__()
            
            self.update()
            self.draw()
            pygame.display.flip()

    def spawn_block(self):
        x = random.randrange(TETRIS_WIDTH + GRID_SIZE, SCREEN_WIDTH - GRID_SIZE)
        block = Block(x)
        self.falling_blocks.add(block)
        self.all_sprites.add(block)

    def add_to_tetris(self, block):
        # Find first available position from bottom-left
        for y in range(TETRIS_ROWS - 1, -1, -1):
            for x in range(TETRIS_COLS):
                if self.tetris_grid[y][x] == 0:
                    self.tetris_grid[y][x] = BLUE if not block.is_red else RED
                    return True
        
        self.game_over = True
        return False

    def update(self):
        if not self.game_over:
            self.all_sprites.update()
            
            # Check for bullet collisions with red blocks
            hits = pygame.sprite.groupcollide(self.bullets, self.falling_blocks, True, False)
            for bullet, blocks in hits.items():
                for block in blocks:
                    if block.is_red:  # Only destroy red blocks with bullets
                        block.kill()
                        self.score += 100
            
            # Check for player collisions with blue blocks
            for block in list(self.falling_blocks):
                if not block.is_red and pygame.sprite.collide_rect(self.player, block):
                    self.add_to_tetris(block)
                    block.kill()
                    self.score += 200
                elif block.rect.bottom >= SCREEN_HEIGHT:  # Block hits bottom
                    self.game_over = True
                    break

            # Spawn new blocks
            self.spawn_timer += 1
            if self.spawn_timer >= 60:  # Spawn every second
                self.spawn_block()
                self.spawn_timer = 0
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw dividing line
        pygame.draw.line(self.screen, WHITE, (TETRIS_WIDTH, 0), (TETRIS_WIDTH, SCREEN_HEIGHT))
        
        # Draw tetris grid and blocks
        for y in range(TETRIS_ROWS):
            for x in range(TETRIS_COLS):
                pygame.draw.rect(self.screen, (30, 30, 30),
                               (x * GRID_SIZE, y * GRID_SIZE,
                                GRID_SIZE, GRID_SIZE), 1)
                if self.tetris_grid[y][x]:
                    pygame.draw.rect(self.screen, self.tetris_grid[y][x],
                                   (x * GRID_SIZE, y * GRID_SIZE,
                                    GRID_SIZE - 1, GRID_SIZE - 1))
        
        self.all_sprites.draw(self.screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (TETRIS_WIDTH + 10, 10))
        
        if self.game_over:
            game_over_text = font.render('GAME OVER - Press R to Restart', True, WHITE)
            self.screen.blit(game_over_text,
                           (SCREEN_WIDTH//2 - game_over_text.get_width()//2,
                            SCREEN_HEIGHT//2))

def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()