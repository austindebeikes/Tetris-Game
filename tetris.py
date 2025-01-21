import pygame
import random
import sys
import copy
import math

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
BRIGHT_BLUE = (0, 150, 255)
GRAY = (50, 50, 50)
TARGET_COLOR = (60, 60, 60)
PURPLE = (147, 0, 211)
STAR_COLORS = [(255, 255, 255), (200, 200, 255), (255, 200, 200)]

# Star field setup
class Star:
    def __init__(self):
        self.x = random.randrange(TETRIS_WIDTH, SCREEN_WIDTH)
        self.y = random.randrange(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.1, 0.5)
        self.color = random.choice(STAR_COLORS)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randrange(TETRIS_WIDTH, SCREEN_WIDTH)

# Create starfield
STARS = [Star() for _ in range(100)]

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
        self.width = 50
        self.height = 40
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = TETRIS_WIDTH + GALAGA_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 8
        self.thrust_counter = 0
        self.draw_ship()
        
    def draw_ship(self):
        # Main ship body
        ship_color = BRIGHT_BLUE
        points = [
            (self.width//2, 0),  # nose
            (0, self.height),    # bottom left
            (self.width//4, self.height*0.7),  # left indent
            (self.width*3//4, self.height*0.7),  # right indent
            (self.width, self.height)  # bottom right
        ]
        pygame.draw.polygon(self.image, ship_color, points)
        
        # Thruster animation
        self.thrust_counter = (self.thrust_counter + 1) % 6
        thrust_height = 10 + self.thrust_counter
        thrust_points = [
            (self.width//3, self.height),
            (self.width//2, self.height + thrust_height),
            (self.width*2//3, self.height)
        ]
        pygame.draw.polygon(self.image, PURPLE, thrust_points)
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > TETRIS_WIDTH:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        self.draw_ship()  # Update thruster animation

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 12), pygame.SRCALPHA)  # Wider bullet
        # Create glowing effect
        pygame.draw.circle(self.image, PURPLE, (8, 6), 8)  # Outer glow
        pygame.draw.circle(self.image, WHITE, (8, 6), 4)   # Inner core
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
        self.speed = 0.65  # Slowed down speed
        
    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    # Create glowing effect for blocks
                    glow_surf = pygame.Surface((GRID_SIZE - 1, GRID_SIZE - 1), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*BRIGHT_BLUE, 128),  # Semi-transparent glow
                                   (0, 0, GRID_SIZE - 1, GRID_SIZE - 1))
                    self.image.blit(glow_surf,
                                  (x * GRID_SIZE, y * GRID_SIZE))
                    pygame.draw.rect(self.image, BRIGHT_BLUE,
                                   (x * GRID_SIZE + 2, y * GRID_SIZE + 2,
                                    GRID_SIZE - 5, GRID_SIZE - 5))
    
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
        pygame.display.set_caption("Space Block Shooter")
        self.clock = pygame.time.Clock()
        
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.bullets = pygame.sprite.Group()
        self.falling_blocks = pygame.sprite.Group()
        self.tetris_grid = copy.deepcopy(DISPLAY_GRID)
        self.target_patterns = copy.deepcopy(TARGET_PATTERNS)
        self.current_column = 0
        self.game_over = False
        self.spawn_timer = 0
        self.score = 0

    def update_starfield(self):
        for star in STARS:
            star.update()

    def draw_starfield(self):
        for star in STARS:
            pygame.draw.circle(self.screen, star.color, (int(star.x), int(star.y)), star.size)

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

        if base_x + shape_width > TETRIS_COLS:
            self.game_over = True
            return False

        for y in range(shape_height):
            for x in range(shape_width):
                if tetromino.shape[y][x]:
                    new_y = base_y - (shape_height - 1) + y
                    if new_y >= 0:
                        self.tetris_grid[new_y][base_x + x] = BRIGHT_BLUE

        self.current_column += shape_width + 1
        self.generate_new_targets()
        return True

    def update(self):
        if not self.game_over:
            self.update_starfield()
            self.all_sprites.update()
            
            for bullet in list(self.bullets):
                for tetromino in list(self.falling_blocks):
                    if tetromino.check_collision((bullet.rect.centerx, bullet.rect.centery)):
                        tetromino.remove_block((bullet.rect.centerx, bullet.rect.centery))
                        bullet.kill()
                        self.score += 50
                        
                        if not tetromino.has_blocks():
                            tetromino.kill()
                        break
            
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

            self.spawn_timer += 1
            if self.spawn_timer >= 240:
                self.spawn_tetromino()
                self.spawn_timer = 0
    
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_starfield()
        
        for y in range(TETRIS_ROWS):
            for x in range(TETRIS_COLS):
                pygame.draw.rect(self.screen, GRAY,
                               (x * GRID_SIZE, y * GRID_SIZE,
                                GRID_SIZE, GRID_SIZE), 1)
                
                for pattern in self.target_patterns:
                    if pattern[y][x]:
                        pygame.draw.rect(self.screen, TARGET_COLOR,
                                       (x * GRID_SIZE, y * GRID_SIZE,
                                        GRID_SIZE - 1, GRID_SIZE - 1))
                
                if self.tetris_grid[y][x]:
                    # Add glow effect to placed blocks
                    glow_surf = pygame.Surface((GRID_SIZE - 1, GRID_SIZE - 1), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*BRIGHT_BLUE, 128),
                                   (0, 0, GRID_SIZE - 1, GRID_SIZE - 1))
                    self.screen.blit(glow_surf, (x * GRID_SIZE, y * GRID_SIZE))
                    pygame.draw.rect(self.screen, BRIGHT_BLUE,
                                   (x * GRID_SIZE + 2, y * GRID_SIZE + 2,
                                    GRID_SIZE - 5, GRID_SIZE - 5))
        
        pygame.draw.line(self.screen, BRIGHT_BLUE, (TETRIS_WIDTH, 0), 
                        (TETRIS_WIDTH, SCREEN_HEIGHT))
        
        self.all_sprites.draw(self.screen)
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, BRIGHT_BLUE)
        self.screen.blit(score_text, (TETRIS_WIDTH + 10, 10))
        
        if self.game_over:
            game_over_text = font.render('GAME OVER - Press R to Restart', True, BRIGHT_BLUE)
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