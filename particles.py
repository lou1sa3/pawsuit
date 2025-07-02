"""
Particle effects system for Pawsuit game.

Contains classes for creating cute particle effects like hearts, sparkles, and twinkles.
"""

import pygame
import math
import random
from typing import List, Tuple
from enum import Enum


class ParticleType(Enum):
    """Types of particles available."""
    HEART = "heart"
    SPARKLE = "sparkle"
    TWINKLE = "twinkle"
    COLLECT = "collect"


class Particle:
    """Individual particle with position, velocity, and lifecycle."""
    
    def __init__(self, x: int, y: int, particle_type: ParticleType, color: Tuple[int, int, int]):
        """
        Initialize a particle.
        
        Args:
            x: Starting X position
            y: Starting Y position
            particle_type: Type of particle to create
            color: RGB color tuple
        """
        self.x = float(x)
        self.y = float(y)
        self.particle_type = particle_type
        self.color = color
        
        # Physics
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-3, -1)
        self.gravity = 0.1
        
        # Lifecycle
        self.life = 1.0
        self.life_decay = random.uniform(0.01, 0.03)
        
        # Visual properties
        self.size = random.uniform(3, 8) if particle_type == ParticleType.HEART else random.uniform(2, 5)
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        
        # Sparkle-specific
        self.pulse_timer = 0
        self.pulse_speed = random.uniform(0.1, 0.3)
    
    def update(self):
        """Update particle physics and lifecycle."""
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Apply gravity for hearts
        if self.particle_type == ParticleType.HEART:
            self.velocity_y += self.gravity
        
        # Update rotation
        self.rotation += self.rotation_speed
        
        # Update pulse for sparkles
        self.pulse_timer += self.pulse_speed
        
        # Decay life
        self.life -= self.life_decay
        
        return self.life > 0
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the particle on screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.life <= 0:
            return
        
        # Calculate alpha based on life
        alpha = max(0, min(255, int(self.life * 255)))
        color_with_alpha = (*self.color, alpha)
        
        # Create temporary surface for alpha blending
        temp_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        if self.particle_type == ParticleType.HEART:
            self.draw_heart(temp_surface, 10, 10, self.size, color_with_alpha)
        elif self.particle_type == ParticleType.SPARKLE:
            self.draw_sparkle(temp_surface, 10, 10, self.size, color_with_alpha)
        elif self.particle_type == ParticleType.TWINKLE:
            self.draw_twinkle(temp_surface, 10, 10, self.size, color_with_alpha)
        elif self.particle_type == ParticleType.COLLECT:
            self.draw_collect_star(temp_surface, 10, 10, self.size, color_with_alpha)
        
        # Blit to main screen
        screen.blit(temp_surface, (self.x - 10, self.y - 10))
    
    def draw_heart(self, surface: pygame.Surface, x: int, y: int, size: float, color: Tuple[int, int, int, int]):
        """Draw a cute heart shape."""
        # Simple heart using circles and triangle
        heart_size = max(2, int(size))
        
        # Left circle
        pygame.draw.circle(surface, color[:3], 
                         (x - heart_size//3, y - heart_size//4), 
                         heart_size//2)
        
        # Right circle  
        pygame.draw.circle(surface, color[:3], 
                         (x + heart_size//3, y - heart_size//4), 
                         heart_size//2)
        
        # Bottom triangle
        points = [
            (x, y + heart_size//2),
            (x - heart_size//2, y),
            (x + heart_size//2, y)
        ]
        pygame.draw.polygon(surface, color[:3], points)
    
    def draw_sparkle(self, surface: pygame.Surface, x: int, y: int, size: float, color: Tuple[int, int, int, int]):
        """Draw a sparkle with pulsing effect."""
        pulse_size = size * (1 + 0.3 * math.sin(self.pulse_timer))
        sparkle_size = max(2, int(pulse_size))
        
        # Draw cross pattern
        pygame.draw.line(surface, color[:3], 
                        (x - sparkle_size, y), (x + sparkle_size, y), 2)
        pygame.draw.line(surface, color[:3], 
                        (x, y - sparkle_size), (x, y + sparkle_size), 2)
        
        # Draw diagonal lines for more sparkle
        pygame.draw.line(surface, color[:3], 
                        (x - sparkle_size//2, y - sparkle_size//2), 
                        (x + sparkle_size//2, y + sparkle_size//2), 1)
        pygame.draw.line(surface, color[:3], 
                        (x - sparkle_size//2, y + sparkle_size//2), 
                        (x + sparkle_size//2, y - sparkle_size//2), 1)
    
    def draw_twinkle(self, surface: pygame.Surface, x: int, y: int, size: float, color: Tuple[int, int, int, int]):
        """Draw a simple twinkle dot."""
        twinkle_size = max(1, int(size))
        pygame.draw.circle(surface, color[:3], (x, y), twinkle_size)
    
    def draw_collect_star(self, surface: pygame.Surface, x: int, y: int, size: float, color: Tuple[int, int, int, int]):
        """Draw a collection star effect."""
        star_size = max(3, int(size))
        
        # Draw 4-pointed star
        points = [
            (x, y - star_size),           # Top
            (x + star_size//3, y - star_size//3),
            (x + star_size, y),           # Right
            (x + star_size//3, y + star_size//3),
            (x, y + star_size),           # Bottom
            (x - star_size//3, y + star_size//3),
            (x - star_size, y),           # Left
            (x - star_size//3, y - star_size//3),
        ]
        pygame.draw.polygon(surface, color[:3], points)


class ParticleSystem:
    """Manages multiple particles and effects."""
    
    def __init__(self):
        """Initialize the particle system."""
        self.particles: List[Particle] = []
        
        # Color palette
        self.colors = {
            'pink': (255, 182, 193),      # Light pink
            'lilac': (200, 162, 200),     # Soft lilac
            'cream': (255, 253, 208),     # Cream
            'baby_blue': (173, 216, 230), # Baby blue
            'peach': (255, 218, 185),     # Soft peach
            'mint': (152, 251, 152),      # Mint green
        }
    
    def add_heart_burst(self, x: int, y: int, count: int = 5):
        """
        Add a burst of heart particles.
        
        Args:
            x: Center X position
            y: Center Y position
            count: Number of hearts to create
        """
        for _ in range(count):
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            color = random.choice(list(self.colors.values()))
            
            particle = Particle(x + offset_x, y + offset_y, ParticleType.HEART, color)
            self.particles.append(particle)
    
    def add_sparkle_trail(self, x: int, y: int, count: int = 3):
        """
        Add sparkle particles for movement trail.
        
        Args:
            x: Center X position
            y: Center Y position
            count: Number of sparkles to create
        """
        for _ in range(count):
            offset_x = random.randint(-15, 15)
            offset_y = random.randint(-15, 15)
            color = random.choice([self.colors['cream'], self.colors['baby_blue']])
            
            particle = Particle(x + offset_x, y + offset_y, ParticleType.SPARKLE, color)
            particle.life_decay = 0.05  # Shorter life for trail
            self.particles.append(particle)
    
    def add_collect_effect(self, x: int, y: int):
        """
        Add collection effect particles.
        
        Args:
            x: Center X position
            y: Center Y position
        """
        # Add collection stars
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 30)
            particle_x = x + distance * math.cos(angle)
            particle_y = y + distance * math.sin(angle)
            
            particle = Particle(int(particle_x), int(particle_y), ParticleType.COLLECT, self.colors['cream'])
            particle.velocity_x = 2 * math.cos(angle)
            particle.velocity_y = 2 * math.sin(angle)
            self.particles.append(particle)
        
        # Add hearts
        self.add_heart_burst(x, y, 3)
    
    def add_ambient_twinkles(self, screen_width: int, screen_height: int):
        """
        Add ambient twinkle effects across the screen.
        
        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        if random.random() < 0.1:  
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            color = random.choice([self.colors['cream'], self.colors['baby_blue'], self.colors['mint']])
            
            particle = Particle(x, y, ParticleType.TWINKLE, color)
            particle.velocity_x = 0
            particle.velocity_y = 0
            particle.gravity = 0
            particle.life_decay = 0.02
            self.particles.append(particle)
    
    def update(self):
        """Update all particles."""
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen: pygame.Surface):
        """
        Draw all particles.
        
        Args:
            screen: Pygame surface to draw on
        """
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self):
        """Clear all particles."""
        self.particles.clear() 