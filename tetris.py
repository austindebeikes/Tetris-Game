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
GRAY = (50, 50, 50)
TARGET_COLOR = (60, 60, 60)

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

def create_target_patterns():
    patterns = []
    shapes = []
    for i in range(2):
        pattern = [[0 for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]
        shape = random.choice(SHAPES)
        shape_height = len(shape)
        shape_width = len(shape[0])
        
        # Place patterns in upper quarter, spaced apart
        if i == 0:
            start_x = TETRIS_COLS // 4 - shape_width // 2
            start_y = TETRIS_ROWS // 4
        else:
            start_x = 3 * TETRIS_COLS // 4 - shape_width // 2
            start_y = TETRIS_ROWS // 4
        
        for y in range(shape_height):
            for x in range(shape_width):
                if shape[y][x]:
                    pattern[start_y + y][start_x + x] = 1
                    
        patterns.append(pattern)
        shapes.append(shape)
                
    return patterns, shapes

# Initialize display grid and patterns
DISPLAY_GRID = [[0 for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]
TARGET_PATTERNS, CURRENT_TARGET_SHAPES = create_target_patterns()

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
        self.speed = 1.5
        
    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.image, BLUE,
                                   (x * GRID_SIZE, y * GRID_SIZE,
                                    GRID_SIZE - 1, GRID_SIZE - 1))
    
    def check_collision(self, point):
        try:
            local_x = point[0] - self.rect.x
            local_y = point[1] - self.rect.y
            
            grid_x = local_x // GRID_SIZE
            grid_y = local_y // GRID_SIZE
            
            if 0 <= grid_y < len(self.shape) and 0 <= grid_x < len(self.shape[0]):
                return self.shape[grid_y][grid_x] == 1
        except (IndexError, ZeroDivisionError):
            return False
        return False

    def remove_block(self, point):
        try:
            local_x = (point[0] - self.rect.x) // GRID_SIZE
            local_y = (point[1] - self.rect.y) // GRID_SIZE
            
            if 0 <= local_y < len(self.shape) and 0 <= local_x < len(self.shape[0]):
                if self.shape[local_y][local_x] == 1:
                    self.shape[local_y][local_x] = 0
                    self.draw_shape()
                    return True
        except (IndexError, ZeroDivisionError):
            return False
        return False

    def has_blocks(self):
        return any(any(row) for row in self.shape)
    
    def update(self):
        self.rect.y += self.speed

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Puzzle Shooter")
        self.clock = pygame.time.Clock()
        
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.bullets = pygame.sprite.Group()
        self.falling_blocks = pygame.sprite.Group()
        self.tetris_grid = copy.deepcopy(DISPLAY_GRID)
        self.target_patterns = copy.deepcopy(TARGET_PATTERNS)
        self.current_column = 0  # Track where to place next piece
        self.game_over = False
        self.spawn_timer = 0
        self.score = 0

    def generate_new_targets(self):
        global TARGET_PATTERNS, CURRENT_TARGET_SHAPES
        TARGET_PATTERNS, CURRENT_TARGET_SHAPES = create_target_patterns()
        self.target_patterns = copy.deepcopy(TARGET_PATTERNS)

    def find_next_position(self):
        bottom_row = TETRIS_ROWS - 1
        return self.current_column, bottom_row

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
        try:
            x = random.randrange(TETRIS_WIDTH + GRID_SIZE, SCREEN_WIDTH - 4 * GRID_SIZE)
            tetromino = Tetromino(x)
            self.falling_blocks.add(tetromino)
            self.all_sprites.add(tetromino)
        except ValueError:
            print("Error spawning tetromino: Invalid position calculated")

    def matches_any_target(self, tetromino):
        return any(tetromino.shape == shape for shape in CURRENT_TARGET_SHAPES)

    def place_tetromino(self, tetromino):
        if not self.matches_any_target(tetromino):
            return False
            
        base_x, base_y = self.find_next_position()
        shape_height = len(tetromino.shape)
        shape_width = len(tetromino.shape[0])

        # Check if there's room to place the piece
        if base_x + shape_width > TETRIS_COLS:
            self.game_over = True
            return False

        # Place the piece
        for y in range(shape_height):
            for x in range(shape_width):
                if tetromino.shape[y][x]:
                    new_y = base_y - (shape_height - 1) + y
                    if new_y >= 0:
                        self.tetris_grid[new_y][base_x + x] = BLUE

        # Update the current column for next placement
        self.current_column += shape_width + 1  # Add 1 for spacing
        
        # Generate new targets after successful placement
        self.generate_new_targets()
        return True

    def update(self):
        if not self.game_over:
            self.all_sprites.update()
            
            # Handle bullet collisions
            for bullet in list(self.bullets):
                for tetromino in list(self.falling_blocks):
                    if tetromino.check_collision((bullet.rect.centerx, bullet.rect.centery)):
                        tetromino.remove_block((bullet.rect.centerx, bullet.rect.centery))
                        bullet.kill()
                        self.score += 50
                        
                        if not tetromino.has_blocks():
                            tetromino.kill()
                        break
            
            # Handle tetromino collisions
            for tetromino in list(self.falling_blocks):
                if pygame.sprite.collide_rect(self.player, tetromino):
                    if tetromino.has_blocks():
                        if self.place_tetromino(tetromino):
                            tetromino.kill()
                            self.score += 200
                elif tetromino.rect.top > SCREEN_HEIGHT:
                    if tetromino.has_blocks():
                        self.game_over = True
                    tetromino.kill()

            # Spawn new tetrominos
            self.spawn_timer += 1
            if self.spawn_timer >= 120:
                self.spawn_tetromino()
                self.spawn_timer = 0
    
    def draw(self):
        try:
            self.screen.fill(BLACK)
            
            # Draw grid and target patterns
            for y in range(TETRIS_ROWS):
                for x in range(TETRIS_COLS):
                    # Grid lines
                    pygame.draw.rect(self.screen, GRAY,
                                   (x * GRID_SIZE, y * GRID_SIZE,
                                    GRID_SIZE, GRID_SIZE), 1)
                    
                    # Draw both target patterns
                    for pattern in self.target_patterns:
                        if pattern[y][x]:
                            pygame.draw.rect(self.screen, TARGET_COLOR,
                                           (x * GRID_SIZE, y * GRID_SIZE,
                                            GRID_SIZE - 1, GRID_SIZE - 1))
                    
                    # Placed blocks
                    if self.tetris_grid[y][x]:
                        pygame.draw.rect(self.screen, BLUE,
                                       (x * GRID_SIZE, y * GRID_SIZE,
                                        GRID_SIZE - 1, GRID_SIZE - 1))
            
            # Draw dividing line
            pygame.draw.line(self.screen, WHITE, (TETRIS_WIDTH, 0), 
                           (TETRIS_WIDTH, SCREEN_HEIGHT))
            
            self.all_sprites.draw(self.screen)
            
            # Draw HUD
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {self.score}', True, WHITE)
            self.screen.blit(score_text, (TETRIS_WIDTH + 10, 10))
            
            if self.game_over:
                game_over_text = font.render('GAME OVER - Press R to Restart', True, WHITE)
                self.screen.blit(game_over_text,
                               (SCREEN_WIDTH//2 - game_over_text.get_width()//2,
                                SCREEN_HEIGHT//2))

        except Exception as e:
            print(f"Error in draw method: {e}")

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