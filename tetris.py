import pygame
import random
import sys
import copy

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

# Tetromino Shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], 
     [1, 1]],  # O
    [[0, 1, 0], 
     [1, 1, 1]],  # T
    [[1, 0, 0], 
     [1, 1, 1]],  # L
    [[0, 0, 1], 
     [1, 1, 1]],  # J
    [[1, 1, 0], 
     [0, 1, 1]],  # S
    [[0, 1, 1], 
     [1, 1, 0]]   # Z
]

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

class Tetromino(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.shape_index = random.randrange(len(SHAPES))
        self.shape = copy.deepcopy(SHAPES[self.shape_index])
        self.width = len(self.shape[0]) * GRID_SIZE
        self.height = len(self.shape) * GRID_SIZE
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_shape()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.height
        self.speed = 2

    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.image, BLUE,
                                   (x * GRID_SIZE, y * GRID_SIZE,
                                    GRID_SIZE - 1, GRID_SIZE - 1))
    
    def check_collision(self, point):
        local_x = point[0] - self.rect.x
        local_y = point[1] - self.rect.y
        
        grid_x = local_x // GRID_SIZE
        grid_y = local_y // GRID_SIZE
        
        if 0 <= grid_y < len(self.shape) and 0 <= grid_x < len(self.shape[0]):
            return self.shape[grid_y][grid_x] == 1
        return False

    def remove_block(self, point):
        local_x = (point[0] - self.rect.x) // GRID_SIZE
        local_y = (point[1] - self.rect.y) // GRID_SIZE
        
        if 0 <= local_y < len(self.shape) and 0 <= local_x < len(self.shape[0]):
            if self.shape[local_y][local_x] == 1:
                self.shape[local_y][local_x] = 0
                self.draw_shape()
                return True
        return False

    def has_blocks(self):
        return any(any(row) for row in self.shape)
    
    def update(self):
        self.rect.y += self.speed

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Shooter")
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

    def spawn_tetromino(self):
        x = random.randrange(TETRIS_WIDTH + GRID_SIZE, SCREEN_WIDTH - 4 * GRID_SIZE)
        tetromino = Tetromino(x)
        self.falling_blocks.add(tetromino)
        self.all_sprites.add(tetromino)

    def add_to_tetris(self, tetromino):
        shape_height = len(tetromino.shape)
        shape_width = len(tetromino.shape[0])
        
        # Find first position from bottom that can fit the shape
        for base_y in range(TETRIS_ROWS - shape_height, -1, -1):
            for base_x in range(TETRIS_COLS - shape_width + 1):
                # Check if this position can fit the shape
                can_fit = True
                for y in range(shape_height):
                    for x in range(shape_width):
                        if tetromino.shape[y][x] and self.tetris_grid[base_y + y][base_x + x]:
                            can_fit = False
                            break
                    if not can_fit:
                        break
                
                if can_fit:
                    # Place the shape exactly as it is
                    for y in range(shape_height):
                        for x in range(shape_width):
                            if tetromino.shape[y][x]:
                                self.tetris_grid[base_y + y][base_x + x] = BLUE
                    return True
                    
        self.game_over = True
        return False

    def update(self):
        if not self.game_over:
            self.all_sprites.update()
            
            # Check for bullet collisions
            for bullet in list(self.bullets):
                hit = False
                for tetromino in list(self.falling_blocks):
                    if tetromino.check_collision((bullet.rect.centerx, bullet.rect.centery)):
                        tetromino.remove_block((bullet.rect.centerx, bullet.rect.centery))
                        bullet.kill()
                        hit = True
                        self.score += 50
                        
                        # Remove tetromino if all blocks are gone
                        if not tetromino.has_blocks():
                            tetromino.kill()
                        break
            
            # Check for player collisions with tetrominos
            for tetromino in list(self.falling_blocks):
                if pygame.sprite.collide_rect(self.player, tetromino):
                    if tetromino.has_blocks():  # Only catch if it still has blocks
                        self.add_to_tetris(tetromino)
                        tetromino.kill()
                        self.score += 200
                elif tetromino.rect.top > SCREEN_HEIGHT:  # Tetromino hits bottom
                    if tetromino.has_blocks():  # Only game over if it has blocks
                        self.game_over = True
                    else:
                        tetromino.kill()
                    break

            # Spawn new tetrominos
            self.spawn_timer += 1
            if self.spawn_timer >= 90:  # Spawn rate
                self.spawn_tetromino()
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