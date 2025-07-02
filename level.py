"""
Level module for Pawsuit game.

Contains the Level class managing game world layout, obstacles, and collectibles.
"""

import pygame
import random
from typing import List, Tuple, Set
from enum import Enum


class CellType(Enum):
    """Grid cell type enumeration."""
    EMPTY = 0
    WALL = 1
    CHEESE = 2
    GOAL = 3
    OBSTACLE = 4


class Level:
    """Game level containing layout, obstacles, and collectibles."""
    
    def __init__(self, width: int, height: int, level_number: int = 1):
        """
        Initialize the level.
        
        Args:
            width: Level width in grid cells
            height: Level height in grid cells
            level_number: Current level number for difficulty scaling
        """
        self.width = width
        self.height = height
        self.level_number = level_number
        self.grid_size = 40  # Pixel size of each grid cell
        
        # Game world grid
        self.grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        
        # Collectibles and objectives
        self.cheese_positions: Set[Tuple[int, int]] = set()
        self.goal_positions: Set[Tuple[int, int]] = set()
        self.obstacle_positions: Set[Tuple[int, int]] = set()
        
        # Rolling obstacles (tomatoes)
        self.rolling_obstacles: List[RollingObstacle] = []
        
        # Colors
        self.colors = {
            CellType.EMPTY: (139, 69, 19),     
            CellType.WALL: (101, 67, 33),      
            CellType.CHEESE: (255, 255, 0),    
            CellType.GOAL: (34, 139, 34),      
            CellType.OBSTACLE: (139, 69, 19),  
        }
        
        # Generate level layout
        self.generate_level()
    
    def generate_level(self):
        """Generate the level layout based on level number."""
        # Clear the grid
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = CellType.EMPTY
        
        # Add perimeter walls
        for x in range(self.width):
            self.grid[0][x] = CellType.WALL
            self.grid[self.height - 1][x] = CellType.WALL
        
        for y in range(self.height):
            self.grid[y][0] = CellType.WALL
            self.grid[y][self.width - 1] = CellType.WALL
        
        # Add some interior walls/obstacles
        self.add_interior_walls()
        
        # Add cheese collectibles
        self.add_cheese()
        
        # Add goal (mouse hole)
        self.add_goal()
        
        # Add rolling obstacles (tomatoes) based on level
        self.add_rolling_obstacles()
    
    def add_interior_walls(self):
        """Add interior walls to create interesting layouts."""
        # Add some scattered walls for cover
        wall_count = min(8 + self.level_number, 20)
        
        for _ in range(wall_count):
            # Try to place a wall in a random location
            for _ in range(50):  # Max attempts
                x = random.randint(2, self.width - 3)
                y = random.randint(2, self.height - 3)
                
                # Don't place walls near starting positions
                if (x < 4 and y < 4) or (x > self.width - 5 and y > self.height - 5):
                    continue
                
                if self.grid[y][x] == CellType.EMPTY:
                    self.grid[y][x] = CellType.WALL
                    break
        
        # Add some kitchen furniture (rectangular blocks)
        self.add_kitchen_furniture()
    
    def add_kitchen_furniture(self):
        """Add kitchen furniture as rectangular obstacles."""
        furniture_pieces = min(2 + self.level_number // 2, 4)
        
        for _ in range(furniture_pieces):
            # Try to place furniture
            for _ in range(30):  # Max attempts
                width = random.randint(2, 4)
                height = random.randint(2, 3)
                x = random.randint(3, self.width - width - 3)
                y = random.randint(3, self.height - height - 3)
                
                # Check if area is clear
                clear = True
                for fy in range(height):
                    for fx in range(width):
                        if self.grid[y + fy][x + fx] != CellType.EMPTY:
                            clear = False
                            break
                    if not clear:
                        break
                
                if clear:
                    # Place furniture
                    for fy in range(height):
                        for fx in range(width):
                            self.grid[y + fy][x + fx] = CellType.WALL
                    break
    
    def add_cheese(self):
        """Add cheese collectibles to the level."""
        cheese_count = 3 + self.level_number
        self.cheese_positions.clear()
        
        for _ in range(cheese_count):
            # Try to place cheese in random empty location
            for _ in range(100):  
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                
                if (self.grid[y][x] == CellType.EMPTY and 
                    (x, y) not in self.cheese_positions and
                    not (x < 3 and y < 3)):  
                    
                    self.cheese_positions.add((x, y))
                    self.grid[y][x] = CellType.CHEESE
                    break
    
    def add_goal(self):
        """Add the goal (mouse hole) to the level."""
        self.goal_positions.clear()
        
        # Place goal in far corner from start
        goal_x = self.width - 2
        goal_y = self.height - 2
        
        # Make sure goal area is clear
        if self.grid[goal_y][goal_x] == CellType.WALL:
            self.grid[goal_y][goal_x] = CellType.EMPTY
        
        self.goal_positions.add((goal_x, goal_y))
        self.grid[goal_y][goal_x] = CellType.GOAL
    
    def add_rolling_obstacles(self):
        """Add rolling tomato obstacles."""
        self.rolling_obstacles.clear()
        
        # Add rolling obstacles based on level difficulty
        obstacle_count = min(self.level_number // 2, 3)
        
        for _ in range(obstacle_count):
            # Try to place rolling obstacle
            for _ in range(50):  
                x = random.randint(3, self.width - 4)
                y = random.randint(3, self.height - 4)
                
                if (self.grid[y][x] == CellType.EMPTY and
                    (x, y) not in self.cheese_positions and
                    (x, y) not in self.goal_positions):
                    
                    # Create rolling obstacle
                    direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                    obstacle = RollingObstacle(x, y, direction, self.grid_size)
                    self.rolling_obstacles.append(obstacle)
                    break
    
    def is_wall(self, x: int, y: int) -> bool:
        """
        Check if position contains a wall or obstacle.
        
        Args:
            x: Grid X position
            y: Grid Y position
            
        Returns:
            True if position is blocked, False otherwise
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        
        # Check static walls
        if self.grid[y][x] == CellType.WALL:
            return True
        
        # Check rolling obstacles
        for obstacle in self.rolling_obstacles:
            if obstacle.grid_x == x and obstacle.grid_y == y:
                return True
        
        return False
    
    def collect_cheese(self, x: int, y: int) -> bool:
        """
        Attempt to collect cheese at position.
        
        Args:
            x: Grid X position
            y: Grid Y position
            
        Returns:
            True if cheese was collected, False otherwise
        """
        if (x, y) in self.cheese_positions:
            self.cheese_positions.remove((x, y))
            self.grid[y][x] = CellType.EMPTY
            return True
        return False
    
    def check_victory(self, x: int, y: int) -> bool:
        """
        Check if victory condition is met.
        
        Args:
            x: Player grid X position
            y: Player grid Y position
            
        Returns:
            True if player has won, False otherwise
        """
        # Must be at goal and have collected all cheese
        return (x, y) in self.goal_positions and len(self.cheese_positions) == 0
    
    def update(self):
        """Update dynamic level elements."""
        # Update rolling obstacles
        for obstacle in self.rolling_obstacles:
            obstacle.update(self)
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the level on screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw grid cells
        for y in range(self.height):
            for x in range(self.width):
                cell_type = self.grid[y][x]
                color = self.colors[cell_type]
                
                rect = pygame.Rect(x * self.grid_size, y * self.grid_size,
                                 self.grid_size, self.grid_size)
                pygame.draw.rect(screen, color, rect)
                
                # Draw cell borders for walls
                if cell_type == CellType.WALL:
                    pygame.draw.rect(screen, (0, 0, 0), rect, 1)
                
                # Draw special cell contents
                self.draw_cell_content(screen, x, y, cell_type)
        
        # Draw rolling obstacles
        for obstacle in self.rolling_obstacles:
            obstacle.draw(screen)
    
    def draw_cell_content(self, screen: pygame.Surface, x: int, y: int, cell_type: CellType):
        """
        Draw special content for specific cell types.
        
        Args:
            screen: Pygame surface to draw on
            x: Grid X position
            y: Grid Y position  
            cell_type: Type of cell to draw
        """
        pixel_x = x * self.grid_size
        pixel_y = y * self.grid_size
        center_x = pixel_x + self.grid_size // 2
        center_y = pixel_y + self.grid_size // 2
        
        if cell_type == CellType.CHEESE:
            # Draw cheese (yellow circle with holes)
            pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), 12)
            pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), 10)
            
            # Cheese holes
            pygame.draw.circle(screen, (255, 255, 0), (center_x - 3, center_y - 2), 2)
            pygame.draw.circle(screen, (255, 255, 0), (center_x + 2, center_y + 1), 1)
            pygame.draw.circle(screen, (255, 255, 0), (center_x - 1, center_y + 3), 1)
        
        elif cell_type == CellType.GOAL:
            # Draw mouse hole 
            pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 15)
            pygame.draw.circle(screen, (34, 139, 34), (center_x, center_y), 13)
            pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 11)


class RollingObstacle:
    """A rolling tomato obstacle that moves in a fixed pattern."""
    
    def __init__(self, grid_x: int, grid_y: int, direction: Tuple[int, int], grid_size: int):
        """
        Initialize rolling obstacle.
        
        Args:
            grid_x: Starting grid X position
            grid_y: Starting grid Y position
            direction: Movement direction (dx, dy)
            grid_size: Size of grid cells in pixels
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.direction = direction
        self.grid_size = grid_size
        
        # Movement timing
        self.move_timer = 0
        self.move_delay = 60  
        
        # Visual properties
        self.color = (255, 0, 0)  
        self.size = grid_size - 6
        
        # Animation
        self.rotation = 0
        self.rotation_speed = 5
    
    @property
    def pixel_x(self) -> int:
        """Get pixel X position."""
        return self.grid_x * self.grid_size
    
    @property
    def pixel_y(self) -> int:
        """Get pixel Y position."""
        return self.grid_y * self.grid_size
    
    def update(self, level: 'Level'):
        """
        Update obstacle movement.
        
        Args:
            level: Current level for collision checking
        """
        # Update animation
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation = 0
        
        # Update movement
        self.move_timer += 1
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            
            # Calculate next position
            next_x = self.grid_x + self.direction[0]
            next_y = self.grid_y + self.direction[1]
            
            # Check if next position is valid
            if (0 < next_x < level.width - 1 and 
                0 < next_y < level.height - 1 and
                level.grid[next_y][next_x] != CellType.WALL):
                
                self.grid_x = next_x
                self.grid_y = next_y
            else:
                # Reverse direction if hit wall
                self.direction = (-self.direction[0], -self.direction[1])
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the rolling obstacle.
        
        Args:
            screen: Pygame surface to draw on
        """
        center_x = self.pixel_x + self.grid_size // 2
        center_y = self.pixel_y + self.grid_size // 2
        
        # Draw tomato body
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.size // 2)
        
        # Draw tomato highlight
        highlight_color = (255, 100, 100)
        pygame.draw.circle(screen, highlight_color, 
                         (center_x - 3, center_y - 3), self.size // 4)
        
        # Draw stem 
        stem_color = (0, 128, 0)  
        stem_length = 8
        stem_angle = self.rotation * (3.14159 / 180)  
        
        import math
        stem_end_x = center_x + int(stem_length * math.cos(stem_angle))
        stem_end_y = center_y + int(stem_length * math.sin(stem_angle))
        
        pygame.draw.line(screen, stem_color, 
                        (center_x, center_y), 
                        (stem_end_x, stem_end_y), 3) 