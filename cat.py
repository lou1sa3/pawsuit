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
    IDLE = "idle"
    CHASE = "chase"


class Cat:
    """Enemy AI - a cat that patrols and chases the mouse."""
    
    def __init__(self, grid_x: int, grid_y: int, grid_size: int, level: 'Level', level_number: int = 1):
        """
        Initialize the cat.
        
        Args:
            grid_x: Starting grid X position
            grid_y: Starting grid Y position
            grid_size: Size of each grid cell in pixels
            level: Current level for navigation
            level_number: Current level number for difficulty scaling
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid_size = grid_size
        self.level = level
        self.level_number = level_number
        
        #AI State 
        self.state = CatState.IDLE
        self.move_timer = 0
        # Speed scaling: cat gets faster each level (lower delay = faster movement)
        base_delay = 40  # Increased from 25 to make first level easier
        speed_increase = min(level_number - 1, 10)  # Cap speed increase at level 11
        self.move_delay = max(base_delay - speed_increase * 2, 8)  # Minimum delay of 8 frames  
        
        # Chase behavior 
        self.chase_range = 20  
        self.mouse_has_moved = False  
        self.last_known_mouse_pos = (grid_x, grid_y)
        
        # Visual properties
        self.body_color = (200, 162, 200)  
        self.belly_color = (255, 253, 208)  
        self.size = grid_size - 2
        
        # Animation
        self.animation_timer = 0
        self.animation_speed = 8
        
    def should_start_chasing(self, mouse_x: int, mouse_y: int) -> bool:
        """
        Determine if cat should start chasing based on mouse movement.
        
        Args:
            mouse_x: Mouse grid X position
            mouse_y: Mouse grid Y position
            
        Returns:
            True if cat should chase, False otherwise
        """
        # Check if mouse has moved from initial position
        if (mouse_x, mouse_y) != self.last_known_mouse_pos:
            self.mouse_has_moved = True
            self.last_known_mouse_pos = (mouse_x, mouse_y)
        
        # Cat starts chasing as soon as mouse moves
        return self.mouse_has_moved
    
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
        # Distance-based detection
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
            # If stuck, try all possible moves to find an escape route
            possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for move_dx, move_dy in possible_moves:
                if self.can_move_to(self.grid_x + move_dx, self.grid_y + move_dy):
                    return (move_dx, move_dy)
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
    
    def update_idle(self):
        """Update idle behavior - cat just waits."""
        # In idle state, cat doesn't move
        pass
    
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
        
        # simplified pathfinding
        target_x, target_y = mouse_x, mouse_y
        
        # Move towards mouse
        dx, dy = self.get_next_move_towards(target_x, target_y)
        if dx != 0 or dy != 0:
            # Double-check that the move is actually valid before executing
            new_x = self.grid_x + dx
            new_y = self.grid_y + dy
            if self.can_move_to(new_x, new_y):
                self.grid_x = new_x
                self.grid_y = new_y
    
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
        if self.state == CatState.IDLE:
            # Check if mouse has moved - if so, start chasing
            if self.should_start_chasing(mouse_x, mouse_y):
                self.state = CatState.CHASE
        
        elif self.state == CatState.CHASE:
            # Always chase the mouse
            self.update_chase(mouse_x, mouse_y)
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the cat on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Calculate position with small offset for centering
        x = self.pixel_x + 1
        y = self.pixel_y + 1
        center_x = x + self.size // 2
        center_y = y + self.size // 2
        
        # Cat body
        body_radius = self.size // 2
        pygame.draw.circle(screen, self.body_color, (center_x, center_y), body_radius)
        
        # Belly
        belly_radius = body_radius - 5
        pygame.draw.circle(screen, self.belly_color, (center_x, center_y + 3), belly_radius)
        
        # Cat ears
        ear_size = self.size // 4
        ear_offset = self.size // 3
        
        # Left ear
        left_ear_points = [
            (center_x - ear_offset, center_y - ear_size),
            (center_x - ear_offset - ear_size//2, center_y - ear_size - ear_size//2),
            (center_x - ear_offset + ear_size//2, center_y - ear_size - ear_size//2)
        ]
        pygame.draw.polygon(screen, self.body_color, left_ear_points)
        
        # Left ear inner
        inner_ear_points = [
            (center_x - ear_offset, center_y - ear_size + 2),
            (center_x - ear_offset - ear_size//3, center_y - ear_size - ear_size//3),
            (center_x - ear_offset + ear_size//3, center_y - ear_size - ear_size//3)
        ]
        pygame.draw.polygon(screen, (255, 192, 203), inner_ear_points)
        
        # Right ear
        right_ear_points = [
            (center_x + ear_offset, center_y - ear_size),
            (center_x + ear_offset - ear_size//2, center_y - ear_size - ear_size//2),
            (center_x + ear_offset + ear_size//2, center_y - ear_size - ear_size//2)
        ]
        pygame.draw.polygon(screen, self.body_color, right_ear_points)
        
        # Right ear inner
        inner_ear_points = [
            (center_x + ear_offset, center_y - ear_size + 2),
            (center_x + ear_offset - ear_size//3, center_y - ear_size - ear_size//3),
            (center_x + ear_offset + ear_size//3, center_y - ear_size - ear_size//3)
        ]
        pygame.draw.polygon(screen, (255, 192, 203), inner_ear_points)
        
        # Eyes
        eye_radius = 5
        eye_offset = self.size // 4
        eye_y_offset = -4
        
        # Left eye 
        pygame.draw.circle(screen, (255, 255, 255),
                         (center_x - eye_offset, center_y + eye_y_offset), eye_radius)
        # Left eye pupil 
        pygame.draw.circle(screen, (100, 149, 237),  # Cornflower blue
                         (center_x - eye_offset + 1, center_y + eye_y_offset), 3)
        # Left eye sparkle
        pygame.draw.circle(screen, (255, 255, 255),
                         (center_x - eye_offset + 2, center_y + eye_y_offset - 1), 1)
        
        # Right eye 
        pygame.draw.circle(screen, (255, 255, 255),
                         (center_x + eye_offset, center_y + eye_y_offset), eye_radius)
        # Right eye pupil 
        pygame.draw.circle(screen, (100, 149, 237),  # Cornflower blue
                         (center_x + eye_offset + 1, center_y + eye_y_offset), 3)
        # Right eye sparkle
        pygame.draw.circle(screen, (255, 255, 255),
                         (center_x + eye_offset + 2, center_y + eye_y_offset - 1), 1)
        
        # Nose
        nose_y = center_y + 2
        nose_points = [
            (center_x, nose_y),
            (center_x - 2, nose_y + 3),
            (center_x + 2, nose_y + 3)
        ]
        pygame.draw.polygon(screen, (255, 105, 180), nose_points)
        
        # Mouth
        mouth_y = center_y + 6
        pygame.draw.arc(screen, (255, 105, 180), 
                       (center_x - 4, mouth_y - 2, 8, 4), 0, 3.14159, 2)
        
        # Tail
        tail_sway = 6 if self.animation_timer < self.animation_speed else -6
        tail_start = (center_x + body_radius - 3, center_y)
        tail_mid = (center_x + body_radius + 8, center_y + tail_sway)
        tail_end = (center_x + body_radius + 15, center_y - tail_sway)
        
        # Tail
        pygame.draw.lines(screen, self.body_color, False, 
                         [tail_start, tail_mid, tail_end], 4)
        
        # Blush Marks
        pygame.draw.circle(screen, (255, 192, 203),
                         (center_x - self.size // 3, center_y + 8), 3)
        pygame.draw.circle(screen, (255, 192, 203),
                         (center_x + self.size // 3, center_y + 8), 3)
        
        # State indicator
        if self.state == CatState.CHASE:
            # Pink hearts
            import math
            for i in range(4):
                angle = (self.animation_timer + i * 90) * 0.1
                heart_x = center_x + int(25 * math.cos(angle))
                heart_y = center_y + int(25 * math.sin(angle))
                
                # Tiny heart
                pygame.draw.circle(screen, (255, 182, 193), (heart_x - 1, heart_y - 1), 2)
                pygame.draw.circle(screen, (255, 182, 193), (heart_x + 1, heart_y - 1), 2)
                pygame.draw.polygon(screen, (255, 182, 193), 
                                  [(heart_x, heart_y + 2), (heart_x - 2, heart_y), (heart_x + 2, heart_y)])
    
    def get_rect(self) -> pygame.Rect:
        """
        Get collision rectangle for the cat.
        
        Returns:
            pygame.Rect representing the cat's bounds
        """
        return pygame.Rect(self.pixel_x, self.pixel_y, self.grid_size, self.grid_size) 