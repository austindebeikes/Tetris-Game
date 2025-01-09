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

# Initialize target pattern with proper size checking
TARGET_PATTERN = [[0 for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]

# Create a simple target pattern
def create_target_pattern():
    pattern = [[0 for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]
    # Create a simple tetris shape in the middle
    middle_col = TETRIS_COLS // 2 - 2
    # Add an L shape
    for i in range(4):
        pattern[10][middle_col + i] = 1  # Horizontal part
    for i in range(3):
        pattern[9-i][middle_col] = 1     # Vertical part
    return pattern

TARGET_PATTERN = create_target_pattern()
DISPLAY_GRID = [[0 for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]

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
        self.SHAPES = [
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
        
        self.shape_index = random.randrange(len(self.SHAPES))
        self.shape = copy.deepcopy(self.SHAPES[self.shape_index])
        self.width = len(self.shape[0]) * GRID_SIZE
        self.height = len(self.shape) * GRID_SIZE
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_shape()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.height
        self.speed = 3  # Increased speed for better gameplay
        
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