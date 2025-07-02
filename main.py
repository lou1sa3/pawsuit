#!/usr/bin/env python3
"""
Pawsuit - A cute 2D stealth game where an adorable mouse avoids a friendly cat.

Main game module handling game loop, state management, and screen transitions.
"""

import pygame
import sys
import math
from enum import Enum
from typing import Optional

from player import Mouse
from cat import Cat
from level import Level
from particles import ParticleSystem


class GameState(Enum):
    """Game state enumeration."""
    TITLE = "title"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class Game:
    """Main game class handling game loop and state management."""
    
    # Game constants
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 60
    GRID_SIZE = 40
    GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
    GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
    
    # Color Palette
    BLACK = (0, 0, 0)                 
    CREAM = (255, 253, 208)           
    SOFT_PINK = (255, 182, 193)       
    LILAC = (200, 162, 200)         
    BABY_BLUE = (173, 216, 230)       
    PEACH = (255, 218, 185)           
    MINT = (152, 251, 152)            
    LAVENDER = (230, 230, 250)       
    ROSE_QUARTZ = (247, 202, 201)     
    WHITE = (255, 255, 255)           
    SOFT_GRAY = (245, 245, 245)       
    
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        pygame.mixer.init()
        
        # Create game window
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Pawsuit")
        
        # Game clock
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.TITLE
        self.running = True
        self.score = 0
        self.level_number = 1
        
        # Load fonts 
        self.load_fonts()
        
        # Load sounds 
        self.sounds = {}
        try:
            self.sounds['move'] = pygame.mixer.Sound('assets/sounds/move.wav')
            self.sounds['collect'] = pygame.mixer.Sound('assets/sounds/collect.wav')
            self.sounds['caught'] = pygame.mixer.Sound('assets/sounds/caught.wav')
            self.sounds['victory'] = pygame.mixer.Sound('assets/sounds/victory.wav')
        except pygame.error:
            # Create silent sounds as fallback
            self.sounds = {
                'move': pygame.mixer.Sound(buffer=b'\x00' * 44100),
                'collect': pygame.mixer.Sound(buffer=b'\x00' * 44100),
                'caught': pygame.mixer.Sound(buffer=b'\x00' * 44100),
                'victory': pygame.mixer.Sound(buffer=b'\x00' * 44100)
            }
        
        # Initialize particle system
        self.particles = ParticleSystem()
        
        # Background animation
        self.bg_animation_timer = 0
        
        # Initialize game objects
        self.reset_game()
    
    def load_fonts(self):
        """Load custom fonts with fallbacks."""
        # Try to load fonts
        kawaii_font_paths = [
            'assets/fonts/baloo.ttf',
            'assets/fonts/fredoka.ttf', 
            'assets/fonts/comic_neue.ttf',
            'assets/fonts/kawaii.ttf'
        ]
        
        # Try custom fonts first
        custom_font_loaded = False
        for font_path in kawaii_font_paths:
            try:
                self.font_title = pygame.font.Font(font_path, 72)  # Large title font
                self.font_large = pygame.font.Font(font_path, 48)
                self.font_medium = pygame.font.Font(font_path, 32)
                self.font_small = pygame.font.Font(font_path, 24)
                custom_font_loaded = True
                break
            except (pygame.error, FileNotFoundError):
                continue
        
        # Fallback to system fonts 
        if not custom_font_loaded:
            # Try system fonts
            kawaii_system_fonts = ['Comic Sans MS', 'Trebuchet MS', 'Verdana', 'Arial Rounded', 'Helvetica']
            font_found = False
            
            for font_name in kawaii_system_fonts:
                try:
                    test_font = pygame.font.SysFont(font_name, 12)
                    # Backup fonts
                    self.font_title = pygame.font.SysFont(font_name, 72, bold=True)
                    self.font_large = pygame.font.SysFont(font_name, 48, bold=True)
                    self.font_medium = pygame.font.SysFont(font_name, 32)
                    self.font_small = pygame.font.SysFont(font_name, 24)
                    font_found = True
                    break
                except pygame.error:
                    continue
            
            # Ultimate fallback
            if not font_found:
                self.font_title = pygame.font.Font(None, 72)
                self.font_large = pygame.font.Font(None, 48)
                self.font_medium = pygame.font.Font(None, 32)
                self.font_small = pygame.font.Font(None, 24)
    
    def reset_game(self):
        """Reset game to starting state."""
        self.level = Level(self.GRID_WIDTH, self.GRID_HEIGHT, self.level_number)
        self.mouse = Mouse(1, 1, self.GRID_SIZE)
        self.cat = Cat(10, 8, self.GRID_SIZE, self.level)
        self.score = 0
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.TITLE:
                    if event.key == pygame.K_RETURN:  # Changed from SPACE to ENTER
                        self.state = GameState.PLAYING
                        self.reset_game()
                elif self.state == GameState.PLAYING:
                    self.handle_game_input(event.key)
                elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.TITLE
                    elif event.key == pygame.K_r:
                        self.state = GameState.PLAYING
                        self.reset_game()
    
    def handle_game_input(self, key):
        """Handle input during gameplay."""
        old_pos = (self.mouse.grid_x, self.mouse.grid_y)
        
        if key in [pygame.K_UP, pygame.K_w]:
            self.mouse.move(0, -1, self.level)
        elif key in [pygame.K_DOWN, pygame.K_s]:
            self.mouse.move(0, 1, self.level)
        elif key in [pygame.K_LEFT, pygame.K_a]:
            self.mouse.move(-1, 0, self.level)
        elif key in [pygame.K_RIGHT, pygame.K_d]:
            self.mouse.move(1, 0, self.level)
        
        # Play move sound if position changed
        if (self.mouse.grid_x, self.mouse.grid_y) != old_pos:
            self.sounds['move'].play()
            # Add trail
            mouse_center_x = self.mouse.pixel_x + self.GRID_SIZE // 2
            mouse_center_y = self.mouse.pixel_y + self.GRID_SIZE // 2
            self.particles.add_sparkle_trail(mouse_center_x, mouse_center_y, 2)
    
    def update(self):
        """Update game logic."""
        # Update particles in all states
        self.particles.update()
        self.bg_animation_timer += 1
        
        if self.state == GameState.PLAYING:
            # Update level (rolling obstacles)
            self.level.update()
            
            # Update cat AI
            self.cat.update(self.mouse.grid_x, self.mouse.grid_y)
            
            # Add ambient twinkles 
            self.particles.add_ambient_twinkles(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            
            # Check collision with cat
            if (self.mouse.grid_x == self.cat.grid_x and 
                self.mouse.grid_y == self.cat.grid_y):
                self.sounds['caught'].play()
                # Add heart burst effect 
                cat_center_x = self.cat.pixel_x + self.GRID_SIZE // 2
                cat_center_y = self.cat.pixel_y + self.GRID_SIZE // 2
                self.particles.add_heart_burst(cat_center_x, cat_center_y, 8)
                self.state = GameState.GAME_OVER
            
            # Check collision with rolling obstacles
            for obstacle in self.level.rolling_obstacles:
                if (self.mouse.grid_x == obstacle.grid_x and 
                    self.mouse.grid_y == obstacle.grid_y):
                    self.sounds['caught'].play()
                    # Add heart burst 
                    obstacle_center_x = obstacle.pixel_x + self.GRID_SIZE // 2
                    obstacle_center_y = obstacle.pixel_y + self.GRID_SIZE // 2
                    self.particles.add_heart_burst(obstacle_center_x, obstacle_center_y, 5)
                    self.state = GameState.GAME_OVER
            
            # Check cheese collection
            cheese_collected = self.level.collect_cheese(self.mouse.grid_x, self.mouse.grid_y)
            if cheese_collected:
                self.sounds['collect'].play()
                self.score += 10
                # Add collection effect
                mouse_center_x = self.mouse.pixel_x + self.GRID_SIZE // 2
                mouse_center_y = self.mouse.pixel_y + self.GRID_SIZE // 2
                self.particles.add_collect_effect(mouse_center_x, mouse_center_y)
            
            # Check victory condition
            if self.level.check_victory(self.mouse.grid_x, self.mouse.grid_y):
                self.sounds['victory'].play()
                # Add victory celebration
                mouse_center_x = self.mouse.pixel_x + self.GRID_SIZE // 2
                mouse_center_y = self.mouse.pixel_y + self.GRID_SIZE // 2
                self.particles.add_heart_burst(mouse_center_x, mouse_center_y, 15)
                self.state = GameState.VICTORY
    
    def draw_title_screen(self):
        """Draw the cartoon-style title screen with black background."""
        # Black background 
        self.screen.fill(self.BLACK)
        
        # Draw decorative hearts 
        self.draw_title_decorations()
        
        # Main title 
        title_text = "PAWSUIT"
        title_color = self.LILAC  
        
        outline_color = self.SOFT_PINK
        outline_offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]
        
        # Draw outline
        for offset_x, offset_y in outline_offsets:
            outline_surface = self.font_title.render(title_text, True, outline_color)
            outline_rect = outline_surface.get_rect(center=(self.WINDOW_WIDTH // 2 + offset_x, 200 + offset_y))
            self.screen.blit(outline_surface, outline_rect)
        
        # Draw main title text
        main_title = self.font_title.render(title_text, True, title_color)
        title_rect = main_title.get_rect(center=(self.WINDOW_WIDTH // 2, 200))
        self.screen.blit(main_title, title_rect)
        
        # Subtitle 
        subtitle_text = self.font_medium.render("♡ Cute Mouse Adventure ♡", True, self.SOFT_PINK)
        subtitle_rect = subtitle_text.get_rect(center=(self.WINDOW_WIDTH // 2, 260))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions 
        instructions = [
            "Use WASD or Arrow Keys to move",
            "Avoid the kitty, collect cheese",
            "Reach the mouse hole to win!"
        ]
        
        y_offset = 350
        for instruction in instructions:
            text = self.font_small.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
        
        # Start button 
        start_text = self.font_medium.render("Press ENTER to start", True, self.LILAC)
        start_rect = start_text.get_rect(center=(self.WINDOW_WIDTH // 2, 480))
        
        # Add a glow effect to the start text
        glow_surface = self.font_medium.render("Press ENTER to start", True, self.SOFT_PINK)
        for glow_offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            glow_rect = glow_surface.get_rect(center=(self.WINDOW_WIDTH // 2 + glow_offset[0], 480 + glow_offset[1]))
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(start_text, start_rect)
        
        # Add blinking effect to start text
        if (self.bg_animation_timer // 30) % 2:  # Blink every 30 frames
            sparkle_text = self.font_small.render("✨ ✨ ✨", True, self.BABY_BLUE)
            sparkle_rect = sparkle_text.get_rect(center=(self.WINDOW_WIDTH // 2, 500))
            self.screen.blit(sparkle_text, sparkle_rect)
    
    def draw_title_decorations(self):
        """Draw decorative elements for the title screen."""
        import math
        
        # Animated floating hearts
        for i in range(6):
            angle = (self.bg_animation_timer * 0.02) + (i * math.pi / 3)
            heart_x = self.WINDOW_WIDTH // 2 + int(250 * math.cos(angle))
            heart_y = 300 + int(80 * math.sin(angle * 0.7))
            
            # Draw heart
            heart_size = 8 + int(3 * math.sin(self.bg_animation_timer * 0.05 + i))
            pygame.draw.circle(self.screen, self.SOFT_PINK, (heart_x - 2, heart_y - 2), heart_size // 2)
            pygame.draw.circle(self.screen, self.SOFT_PINK, (heart_x + 2, heart_y - 2), heart_size // 2)
            pygame.draw.polygon(self.screen, self.SOFT_PINK, 
                              [(heart_x, heart_y + heart_size//2), 
                               (heart_x - heart_size//2, heart_y), 
                               (heart_x + heart_size//2, heart_y)])
        
        # Corner sparkles
        sparkle_positions = [(50, 50), (750, 50), (50, 550), (750, 550)]
        for i, (x, y) in enumerate(sparkle_positions):
            sparkle_size = 3 + int(2 * math.sin(self.bg_animation_timer * 0.1 + i))
            # Draw sparkle cross
            pygame.draw.line(self.screen, self.BABY_BLUE, 
                           (x - sparkle_size, y), (x + sparkle_size, y), 2)
            pygame.draw.line(self.screen, self.BABY_BLUE, 
                           (x, y - sparkle_size), (x, y + sparkle_size), 2)
    
    def draw_game_screen(self):
        """Draw the game screen."""
        self.screen.fill(self.CREAM)
        
        # Draw level (obstacles, cheese, goal)
        self.level.draw(self.screen)
        
        # Draw game objects
        self.mouse.draw(self.screen)
        self.cat.draw(self.screen)
        
        # Draw particles
        self.particles.draw(self.screen)
        
        # Draw HUD with heart decorations
        score_text = self.font_small.render(f"♡ Score: {self.score} ♡", True, self.SOFT_PINK)
        self.screen.blit(score_text, (10, 10))
        
        level_text = self.font_small.render(f"☆ Level: {self.level_number} ☆", True, self.LILAC)
        self.screen.blit(level_text, (10, 35))
        
        # Draw soft grid (optional debug)
        # self.draw_grid()
    
    def draw_grid(self):
        """Draw soft grid lines for debugging."""
        for x in range(0, self.WINDOW_WIDTH, self.GRID_SIZE):
            pygame.draw.line(self.screen, self.SOFT_GRAY, (x, 0), (x, self.WINDOW_HEIGHT))
        for y in range(0, self.WINDOW_HEIGHT, self.GRID_SIZE):
            pygame.draw.line(self.screen, self.SOFT_GRAY, (0, y), (self.WINDOW_WIDTH, y))
    
    def draw_game_over_screen(self):
        """Draw the game over screen."""
        self.screen.fill(self.ROSE_QUARTZ)
        
        # Draw particles
        self.particles.draw(self.screen)
        
        # Game Over text 
        game_over_text = self.font_large.render("♡ OH NO! ♡", True, self.WHITE)
        game_over_rect = game_over_text.get_rect(center=(self.WINDOW_WIDTH // 2, 180))
        self.screen.blit(game_over_text, game_over_rect)
        
        caught_text = self.font_medium.render("The kitty caught you!", True, self.SOFT_PINK)
        caught_rect = caught_text.get_rect(center=(self.WINDOW_WIDTH // 2, 220))
        self.screen.blit(caught_text, caught_rect)
        
        # Score
        score_text = self.font_medium.render(f"♡ Final Score: {self.score} ♡", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.font_small.render("☆ Press R to restart or SPACE for menu ☆", True, self.WHITE)
        restart_rect = restart_text.get_rect(center=(self.WINDOW_WIDTH // 2, 400))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory_screen(self):
        """Draw the victory screen."""
        self.screen.fill(self.MINT)
        
        # Draw particles
        self.particles.draw(self.screen)
        
        # Victory text 
        victory_text = self.font_large.render("♡ VICTORY! ♡", True, self.WHITE)
        victory_rect = victory_text.get_rect(center=(self.WINDOW_WIDTH // 2, 180))
        self.screen.blit(victory_text, victory_rect)
        
        success_text = self.font_medium.render("You reached safety!", True, self.SOFT_PINK)
        success_rect = success_text.get_rect(center=(self.WINDOW_WIDTH // 2, 220))
        self.screen.blit(success_text, success_rect)
        
        # Score
        score_text = self.font_medium.render(f"♡ Final Score: {self.score} ♡", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.font_small.render("☆ Press R to restart or SPACE for menu ☆", True, self.WHITE)
        restart_rect = restart_text.get_rect(center=(self.WINDOW_WIDTH // 2, 400))
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        """Draw the current screen based on game state."""
        if self.state == GameState.TITLE:
            self.draw_title_screen()
        elif self.state == GameState.PLAYING:
            self.draw_game_screen()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over_screen()
        elif self.state == GameState.VICTORY:
            self.draw_victory_screen()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
        
        pygame.quit()
        sys.exit()


def main():
    """Main function to start the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main() 