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
        self.body_color = (255, 182, 193)  # Soft pink
        self.belly_color = (255, 253, 208)  # Cream
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
        center_x = x + self.size // 2
        center_y = y + self.size // 2
        
        # Mouse body (larger, rounder)
        body_radius = self.size // 2
        pygame.draw.circle(screen, self.body_color, (center_x, center_y), body_radius)
        
        # Belly 
        belly_radius = body_radius - 4
        pygame.draw.circle(screen, self.belly_color, (center_x, center_y + 2), belly_radius)
        
        # Ears 
        ear_radius = self.size // 5
        ear_offset_x = self.size // 3
        ear_offset_y = self.size // 4
        
        # Left ear (outer)
        pygame.draw.circle(screen, self.body_color,
                         (center_x - ear_offset_x, center_y - ear_offset_y), ear_radius)
        # Left ear (inner)
        pygame.draw.circle(screen, (255, 192, 203),  # Pink inner ear
                         (center_x - ear_offset_x, center_y - ear_offset_y), ear_radius - 2)
        
        # Right ear (outer)
        pygame.draw.circle(screen, self.body_color,
                         (center_x + ear_offset_x, center_y - ear_offset_y), ear_radius)
        # Right ear (inner)
        pygame.draw.circle(screen, (255, 192, 203),  # Pink inner ear
                         (center_x + ear_offset_x, center_y - ear_offset_y), ear_radius - 2)
        
        # Eyes
        eye_radius = 4
        eye_offset = self.size // 4
        eye_y_offset = -3
        
        # Left eye 
        pygame.draw.circle(screen, (255, 255, 255),
                         (center_x - eye_offset, center_y + eye_y_offset), eye_radius)
        # Left eye pupil
        pygame.draw.circle(screen, (0, 0, 0),
                         (center_x - eye_offset + 1, center_y + eye_y_offset), 2)
        # Left eye sparkle 
        pygame.draw.circle(screen, (255, 255, 255),
                         (center_x - eye_offset + 2, center_y + eye_y_offset - 1), 1)
        
        # Right eye 
        pygame.draw.circle(screen, (255, 255, 255),
                         (center_x + eye_offset, center_y + eye_y_offset), eye_radius)
        # Right eye pupil
        pygame.draw.circle(screen, (0, 0, 0),
                         (center_x + eye_offset + 1, center_y + eye_y_offset), 2)
        # Right eye sparkle
        pygame.draw.circle(screen, (255, 255, 255),
                         (center_x + eye_offset + 2, center_y + eye_y_offset - 1), 1)
        
        # Draw nose 
        nose_y = center_y + 3
        nose_size = 2
        pygame.draw.circle(screen, (255, 105, 180),  # Hot pink
                         (center_x - 1, nose_y - 1), nose_size // 2)
        pygame.draw.circle(screen, (255, 105, 180),
                         (center_x + 1, nose_y - 1), nose_size // 2)
        pygame.draw.circle(screen, (255, 105, 180),
                         (center_x, nose_y + 1), nose_size // 2)
        
        # Tail
        tail_sway = 4 if self.animation_timer < self.animation_speed else -4
        tail_start = (center_x + body_radius - 2, center_y)
        tail_mid = (center_x + body_radius + 6, center_y + tail_sway)
        tail_end = (center_x + body_radius + 12, center_y - tail_sway)
        
        # Tail
        pygame.draw.lines(screen, self.body_color, False, 
                         [tail_start, tail_mid, tail_end], 3)
        
        # Add blush marks
        blush_color = (255, 192, 203, 128)  
        pygame.draw.circle(screen, (255, 192, 203),
                         (center_x - self.size // 3, center_y + 5), 3)
        pygame.draw.circle(screen, (255, 192, 203),
                         (center_x + self.size // 3, center_y + 5), 3)
    
    def get_rect(self) -> pygame.Rect:
        """
        Get the collision rectangle for the mouse.
        
        Returns:
            pygame.Rect representing the mouse's bounds
        """
        return pygame.Rect(self.pixel_x, self.pixel_y, self.grid_size, self.grid_size) 