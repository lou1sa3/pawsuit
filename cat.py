"""
Cat module for Pawsuit game.

Contains the Cat class representing the enemy AI character.
"""

import pygame
import math
from enum import Enum
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from level import Level


class CatState(Enum):
    """Cat AI state enumeration."""
    PATROL = "patrol"
    CHASE = "chase"
    RETURN = "return"


class Cat:
    """Enemy AI - a cat that patrols and chases the mouse."""
    
    def __init__(self, grid_x: int, grid_y: int, grid_size: int, level: 'Level'):
        """
        Initialize the cat.
        
        Args:
            grid_x: Starting grid X position
            grid_y: Starting grid Y position
            grid_size: Size of each grid cell in pixels
            level: Current level for navigation
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid_size = grid_size
        self.level = level
        
        # AI State
        self.state = CatState.PATROL
        self.move_timer = 0
        self.move_delay = 30  # Frames between moves (cat is slower than player)
        
        # Patrol behavior
        self.patrol_points = self.generate_patrol_path()
        self.current_patrol_target = 0
        self.patrol_start = (grid_x, grid_y)
        
        # Chase behavior
        self.chase_range = 4  # Grid cells within which cat will chase
        self.chase_target = None
        self.last_known_mouse_pos = None
        
        # Visual properties
        self.color = (255, 140, 0)  # Orange
        self.size = grid_size - 2
        
        # Animation
        self.animation_timer = 0
        self.animation_speed = 8
        
    def generate_patrol_path(self) -> List[Tuple[int, int]]:
        """
        Generate a patrol path for the cat.
        
        Returns:
            List of (x, y) grid positions for patrol route
        """
        # Create a simple rectangular patrol pattern
        patrol_points = [
            (self.grid_x, self.grid_y),
            (self.grid_x + 3, self.grid_y),
            (self.grid_x + 3, self.grid_y + 3),
            (self.grid_x, self.grid_y + 3),
        ]
        
        # Filter out invalid positions
        valid_points = []
        for x, y in patrol_points:
            if (0 <= x < self.level.width and 
                0 <= y < self.level.height and 
                not self.level.is_wall(x, y)):
                valid_points.append((x, y))
        
        # If no valid patrol points, just stay in place
        if not valid_points:
            valid_points = [(self.grid_x, self.grid_y)]
        
        return valid_points
    
    @property
    def pixel_x(self) -> int:
        """Get pixel X position from grid position."""
        return self.grid_x * self.grid_size
    
    @property
    def pixel_y(self) -> int:
        """Get pixel Y position from grid position."""
        return self.grid_y * self.grid_size
    
    def distance_to(self, target_x: int, target_y: int) -> float:
        """
        Calculate distance to target position.
        
        Args:
            target_x: Target grid X position
            target_y: Target grid Y position
            
        Returns:
            Distance in grid units
        """
        dx = self.grid_x - target_x
        dy = self.grid_y - target_y
        return math.sqrt(dx * dx + dy * dy)
    
    def can_see_mouse(self, mouse_x: int, mouse_y: int) -> bool:
        """
        Check if cat can see the mouse (line of sight).
        
        Args:
            mouse_x: Mouse grid X position
            mouse_y: Mouse grid Y position
            
        Returns:
            True if mouse is visible, False otherwise
        """
        # Simple distance-based detection
        distance = self.distance_to(mouse_x, mouse_y)
        return distance <= self.chase_range
    
    def get_next_move_towards(self, target_x: int, target_y: int) -> Tuple[int, int]:
        """
        Calculate next move towards target position.
        
        Args:
            target_x: Target grid X position
            target_y: Target grid Y position
            
        Returns:
            (dx, dy) movement direction
        """
        dx = 0
        dy = 0
        
        if target_x > self.grid_x:
            dx = 1
        elif target_x < self.grid_x:
            dx = -1
        
        if target_y > self.grid_y:
            dy = 1
        elif target_y < self.grid_y:
            dy = -1
        
        # Try to move in both directions first, then single direction
        if self.can_move_to(self.grid_x + dx, self.grid_y + dy):
            return (dx, dy)
        elif self.can_move_to(self.grid_x + dx, self.grid_y):
            return (dx, 0)
        elif self.can_move_to(self.grid_x, self.grid_y + dy):
            return (0, dy)
        else:
            return (0, 0)
    
    def can_move_to(self, grid_x: int, grid_y: int) -> bool:
        """
        Check if cat can move to given position.
        
        Args:
            grid_x: Target grid X position
            grid_y: Target grid Y position
            
        Returns:
            True if position is valid, False otherwise
        """
        # Check bounds
        if (grid_x < 0 or grid_x >= self.level.width or 
            grid_y < 0 or grid_y >= self.level.height):
            return False
        
        # Check for walls
        return not self.level.is_wall(grid_x, grid_y)
    
    def update_patrol(self):
        """Update patrol behavior."""
        if not self.patrol_points:
            return
        
        # Get current patrol target
        target_x, target_y = self.patrol_points[self.current_patrol_target]
        
        # Check if reached current patrol point
        if self.grid_x == target_x and self.grid_y == target_y:
            # Move to next patrol point
            self.current_patrol_target = (self.current_patrol_target + 1) % len(self.patrol_points)
            target_x, target_y = self.patrol_points[self.current_patrol_target]
        
        # Move towards patrol target
        dx, dy = self.get_next_move_towards(target_x, target_y)
        if dx != 0 or dy != 0:
            self.grid_x += dx
            self.grid_y += dy
    
    def update_chase(self, mouse_x: int, mouse_y: int):
        """
        Update chase behavior.
        
        Args:
            mouse_x: Mouse grid X position
            mouse_y: Mouse grid Y position
        """
        # Update last known mouse position
        if self.can_see_mouse(mouse_x, mouse_y):
            self.last_known_mouse_pos = (mouse_x, mouse_y)
        
        # Chase towards last known position
        if self.last_known_mouse_pos:
            target_x, target_y = self.last_known_mouse_pos
            
            # If reached last known position, switch back to patrol
            if self.grid_x == target_x and self.grid_y == target_y:
                self.state = CatState.RETURN
                return
            
            # Move towards mouse
            dx, dy = self.get_next_move_towards(target_x, target_y)
            if dx != 0 or dy != 0:
                self.grid_x += dx
                self.grid_y += dy
    
    def update_return(self):
        """Update return to patrol behavior."""
        # Return to patrol start position
        target_x, target_y = self.patrol_start
        
        # Check if back at patrol start
        if self.grid_x == target_x and self.grid_y == target_y:
            self.state = CatState.PATROL
            return
        
        # Move towards patrol start
        dx, dy = self.get_next_move_towards(target_x, target_y)
        if dx != 0 or dy != 0:
            self.grid_x += dx
            self.grid_y += dy
    
    def update(self, mouse_x: int, mouse_y: int):
        """
        Update cat AI behavior.
        
        Args:
            mouse_x: Mouse grid X position
            mouse_y: Mouse grid Y position
        """
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed * 2:
            self.animation_timer = 0
        
        # Update move timer
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return
        
        self.move_timer = 0
        
        # State machine logic
        if self.state == CatState.PATROL:
            # Check if mouse is nearby
            if self.can_see_mouse(mouse_x, mouse_y):
                self.state = CatState.CHASE
                self.last_known_mouse_pos = (mouse_x, mouse_y)
            else:
                self.update_patrol()
        
        elif self.state == CatState.CHASE:
            # Check if still chasing or lost mouse
            if self.can_see_mouse(mouse_x, mouse_y):
                self.update_chase(mouse_x, mouse_y)
            else:
                # Continue to last known position
                self.update_chase(mouse_x, mouse_y)
        
        elif self.state == CatState.RETURN:
            self.update_return()
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the cat on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Calculate position with small offset for centering
        x = self.pixel_x + 1
        y = self.pixel_y + 1
        
        # Draw cat body (oval)
        body_rect = pygame.Rect(x + 4, y + 8, self.size - 8, self.size - 12)
        pygame.draw.ellipse(screen, self.color, body_rect)
        
        # Draw cat head (circle)
        head_center = (x + self.size // 2, y + self.size // 3)
        head_radius = self.size // 4
        pygame.draw.circle(screen, self.color, head_center, head_radius)
        
        # Draw cat ears (triangles)
        ear_size = self.size // 8
        left_ear = [
            (x + self.size // 2 - ear_size, y + ear_size),
            (x + self.size // 2 - ear_size // 2, y),
            (x + self.size // 2, y + ear_size)
        ]
        right_ear = [
            (x + self.size // 2, y + ear_size),
            (x + self.size // 2 + ear_size // 2, y),
            (x + self.size // 2 + ear_size, y + ear_size)
        ]
        
        pygame.draw.polygon(screen, self.color, left_ear)
        pygame.draw.polygon(screen, self.color, right_ear)
        
        # Draw eyes (green)
        eye_color = (0, 255, 0)  # Green eyes
        eye_size = 2
        eye_y = y + self.size // 3 - 2
        
        # Left eye
        pygame.draw.circle(screen, eye_color,
                         (x + self.size // 2 - 4, eye_y),
                         eye_size)
        
        # Right eye
        pygame.draw.circle(screen, eye_color,
                         (x + self.size // 2 + 4, eye_y),
                         eye_size)
        
        # Draw nose (small black triangle)
        nose_points = [
            (x + self.size // 2, y + self.size // 3 + 2),
            (x + self.size // 2 - 2, y + self.size // 3 + 5),
            (x + self.size // 2 + 2, y + self.size // 3 + 5)
        ]
        pygame.draw.polygon(screen, (0, 0, 0), nose_points)
        
        # Draw tail (animated)
        tail_sway = 5 if self.animation_timer < self.animation_speed else -5
        tail_start = (x + self.size - 5, y + self.size - 8)
        tail_mid = (x + self.size + 5, y + self.size - 12 + tail_sway)
        tail_end = (x + self.size + 12, y + self.size - 5)
        
        pygame.draw.lines(screen, self.color, False, 
                         [tail_start, tail_mid, tail_end], 3)
        
        # Draw state indicator (for debugging)
        if self.state == CatState.CHASE:
            # Red circle around cat when chasing
            pygame.draw.circle(screen, (255, 0, 0), 
                             (x + self.size // 2, y + self.size // 2),
                             self.size // 2 + 3, 2)
    
    def get_rect(self) -> pygame.Rect:
        """
        Get collision rectangle for the cat.
        
        Returns:
            pygame.Rect representing the cat's bounds
        """
        return pygame.Rect(self.pixel_x, self.pixel_y, self.grid_size, self.grid_size) 