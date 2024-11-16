import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game Constants
screen_width, screen_height = 300, 600 # Standard Tetris screen
cell_size = 30 # Each cell is 30x30 pixels
columns, rows = 10, 20 # Tetris grid size

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_COLOR = (50, 50, 50)

# Initialize the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tetris")

# Game clock
clock = pygame.time.Clock()

# Initialize the grid to track filled cells
grid = [[0 for _ in range(columns)] for _ in range(rows)]

score = 0

def clear_lines():
    global grid
    cleared_lines = 0
    # Iterate from the bottom up
    for y in range(rows -1, -1, -1):
        if all(grid[y]): # Check if row is full
            del grid[y] # Remove the full row
            grid.insert(0, [0 for _ in range(columns)]) # Add an empty row at the top
            cleared_lines += 1
    return cleared_lines


# Draw the grid lines
def draw_grid():
    for x in range(0, screen_width, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, screen_height))
    for y in range(0, screen_height, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (screen_width, y))

# Define shapes ande their rotations as 4x4 matrices
shapes = [
    [[1, 1, 1, 1]],  # I shape
    [[1, 1], [1, 1]],  # O shape
    [[0, 1, 0], [1, 1, 1]],  # T shape
    [[1, 0, 0], [1, 1, 1]],  # L shape
    [[0, 0, 1], [1, 1, 1]],  # J shape
    [[1, 1, 0], [0, 1, 1]],  # S shape
    [[0, 1, 1], [1, 1, 0]]   # Z shape
]

# Colors for each shape
colors = [
    (0, 255, 255),  # Cyan (I)
    (255, 255, 0),  # Yellow (O)
    (128, 0, 128),  # Purple (T)
    (255, 165, 0),  # Orange (L)
    (0, 0, 255),    # Blue (J)
    (0, 255, 0),    # Green (S)
    (255, 0, 0)     # Red (Z)
]

#Tetronimo class
class Tetronimo:
    def __init__(self):
        self.shape = random.choice(shapes)
        self.color = colors[shapes.index(self.shape)]
        self.x = columns // 2 - len(self.shape[0]) // 2
        self.y = 0

    def draw(self):
        for row_index, row in enumerate(self.shape):
            for col_index, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.color,
                                        (self.x * cell_size + col_index * cell_size,
                                        self.y * cell_size + row_index * cell_size,
                                        cell_size, cell_size))

    def move_down(self):
        if not self.check_collision(0, 1): # Check if moving down is safe
            self.y += 1
        else:
            self.add_to_grid()
            return True # Indicates the piece is placed
        return False
    
    def move_horizontal(self, dx):
        if not self.check_collision(dx, 0): # Check horizontal collision
            self.x += dx

    def check_collision(self, dx, dy):
        for row_index, row in enumerate(self.shape):
            for col_index, cell in enumerate(row):
                if cell:
                    new_x = self.x + col_index + dx
                    new_y = self.y + row_index + dy
                    # Check boundries
                    if new_x < 0 or new_x >= columns or new_y >= rows:
                        return True
                    #Check grid for existing blocks
                    if grid[new_y][new_x]:
                        return True
        return False
    
    def add_to_grid(self):
        global score
        for row_index, row in enumerate(self.shape):
            for col_index, cell in enumerate(row):
                if cell:
                    grid[self.y + row_index][self.x + col_index] = self.color
            # Clear lines and update score
            score += clear_lines() * 10

# Create the first piece
current_piece = Tetronimo()

# Main game loop
def main():
    global current_piece
    fall_speed = 500
    last_fall_time = pygame.time.get_ticks()

    while True:
        screen.fill(BLACK)
        draw_grid()

        # Draw the existing pieces on the grid
        for y in range(rows):
            for x in range(columns):
                if grid[y][x]:
                    pygame.draw.rect(screen, grid[y][x],
                                    (x * cell_size, y * cell_size, cell_size, cell_size))
                    
        # Display the score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Move piece down in intervals
        current_time = pygame.time.get_ticks()
        if current_time - last_fall_time > fall_speed:
            if current_piece.move_down():
                current_piece = Tetronimo()
            last_fall_time = current_time # Reset fall timer

        # Draw current piece
        current_piece.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: # Move left
                    current_piece.move_horizontal(-1)
                elif event.key == pygame.K_RIGHT: # Move right
                    current_piece.move_horizontal(1)
                elif event.key == pygame.K_DOWN: # Soft drop
                    current_piece.move_down()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip() # Update the display
        clock.tick(60) # 60 frames per second

# Run game
main()