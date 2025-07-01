"""
Player module for Pawsuit game.

Contains the Mouse class representing the player character.
"""

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from level import Level


class Mouse:
    """Player character - a mouse that moves on a grid."""
    
    def __init__(self, grid_x: int, grid_y: int, grid_size: int):
        """
        Initialize the mouse.
        
        Args:
            grid_x: Starting grid X position
            grid_y: Starting grid Y position
            grid_size: Size of each grid cell in pixels
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid_size = grid_size
        
        # Visual properties
        self.color = (150, 150, 150)  # Light gray
        self.size = grid_size - 4  # Slightly smaller than grid
        
        # Animation properties
        self.animation_timer = 0
        self.animation_speed = 10
        
    @property
    def pixel_x(self) -> int:
        """Get pixel X position from grid position."""
        return self.grid_x * self.grid_size
    
    @property
    def pixel_y(self) -> int:
        """Get pixel Y position from grid position."""
        return self.grid_y * self.grid_size
    
    def move(self, dx: int, dy: int, level: 'Level') -> bool:
        """
        Attempt to move the mouse by the given grid offset.
        
        Args:
            dx: Grid offset in X direction (-1, 0, or 1)
            dy: Grid offset in Y direction (-1, 0, or 1)
            level: Current level for collision checking
            
        Returns:
            True if move was successful, False if blocked
        """
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        
        # Check if new position is valid
        if self.can_move_to(new_x, new_y, level):
            self.grid_x = new_x
            self.grid_y = new_y
            return True
        
        return False
    
    def can_move_to(self, grid_x: int, grid_y: int, level: 'Level') -> bool:
        """
        Check if the mouse can move to the given grid position.
        
        Args:
            grid_x: Target grid X position
            grid_y: Target grid Y position
            level: Current level for collision checking
            
        Returns:
            True if position is valid, False otherwise
        """
        # Check bounds
        if (grid_x < 0 or grid_x >= level.width or 
            grid_y < 0 or grid_y >= level.height):
            return False
        
        # Check for walls/obstacles
        return not level.is_wall(grid_x, grid_y)
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the mouse on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed * 2:
            self.animation_timer = 0
        
        # Calculate position with small offset for centering
        x = self.pixel_x + 2
        y = self.pixel_y + 2
        
        # Draw mouse body (circle)
        pygame.draw.circle(screen, self.color, 
                         (x + self.size // 2, y + self.size // 2), 
                         self.size // 2)
        
        # Draw mouse ears (smaller circles)
        ear_size = self.size // 6
        ear_offset = self.size // 3
        
        # Left ear
        pygame.draw.circle(screen, self.color,
                         (x + ear_offset, y + ear_offset),
                         ear_size)
        
        # Right ear
        pygame.draw.circle(screen, self.color,
                         (x + self.size - ear_offset, y + ear_offset),
                         ear_size)
        
        # Draw eyes (small black dots)
        eye_size = 2
        eye_y = y + self.size // 3
        
        # Left eye
        pygame.draw.circle(screen, (0, 0, 0),
                         (x + self.size // 3, eye_y),
                         eye_size)
        
        # Right eye
        pygame.draw.circle(screen, (0, 0, 0),
                         (x + 2 * self.size // 3, eye_y),
                         eye_size)
        
        # Draw nose (small pink dot)
        nose_color = (255, 192, 203)  # Pink
        pygame.draw.circle(screen, nose_color,
                         (x + self.size // 2, y + self.size // 2),
                         1)
        
        # Draw tail (animated)
        tail_sway = 3 if self.animation_timer < self.animation_speed else -3
        tail_start = (x + self.size, y + self.size // 2)
        tail_end = (x + self.size + 8, y + self.size // 2 + tail_sway)
        
        pygame.draw.line(screen, self.color, tail_start, tail_end, 2)
    
    def get_rect(self) -> pygame.Rect:
        """
        Get the collision rectangle for the mouse.
        
        Returns:
            pygame.Rect representing the mouse's bounds
        """
        return pygame.Rect(self.pixel_x, self.pixel_y, self.grid_size, self.grid_size) 