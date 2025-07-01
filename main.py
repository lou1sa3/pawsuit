#!/usr/bin/env python3
"""
Pawsuit - A 2D stealth game where a mouse must avoid a cat to reach cheese.

Main game module handling game loop, state management, and screen transitions.
"""

import pygame
import sys
from enum import Enum
from typing import Optional

from player import Mouse
from cat import Cat
from level import Level


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
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BROWN = (139, 69, 19)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (128, 128, 128)
    
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
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
        except pygame.error:
            self.font_large = pygame.font.SysFont('arial', 48)
            self.font_medium = pygame.font.SysFont('arial', 32)
            self.font_small = pygame.font.SysFont('arial', 24)
        
        # Load sounds (with fallback if files don't exist)
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
        
        # Initialize game objects
        self.reset_game()
    
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
                    if event.key == pygame.K_SPACE:
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
    
    def update(self):
        """Update game logic."""
        if self.state == GameState.PLAYING:
            # Update level (rolling obstacles)
            self.level.update()
            
            # Update cat AI
            self.cat.update(self.mouse.grid_x, self.mouse.grid_y)
            
            # Check collision with cat
            if (self.mouse.grid_x == self.cat.grid_x and 
                self.mouse.grid_y == self.cat.grid_y):
                self.sounds['caught'].play()
                self.state = GameState.GAME_OVER
            
            # Check collision with rolling obstacles
            for obstacle in self.level.rolling_obstacles:
                if (self.mouse.grid_x == obstacle.grid_x and 
                    self.mouse.grid_y == obstacle.grid_y):
                    self.sounds['caught'].play()
                    self.state = GameState.GAME_OVER
            
            # Check cheese collection
            cheese_collected = self.level.collect_cheese(self.mouse.grid_x, self.mouse.grid_y)
            if cheese_collected:
                self.sounds['collect'].play()
                self.score += 10
            
            # Check victory condition
            if self.level.check_victory(self.mouse.grid_x, self.mouse.grid_y):
                self.sounds['victory'].play()
                self.state = GameState.VICTORY
    
    def draw_title_screen(self):
        """Draw the title screen."""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = self.font_large.render("PAWSUIT", True, self.YELLOW)
        title_rect = title_text.get_rect(center=(self.WINDOW_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_medium.render("Mouse vs Cat Stealth Game", True, self.WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(self.WINDOW_WIDTH // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions
        instructions = [
            "Use WASD or Arrow Keys to move",
            "Avoid the cat, collect cheese",
            "Reach the mouse hole to win",
            "",
            "Press SPACE to start"
        ]
        
        y_offset = 300
        for instruction in instructions:
            if instruction:
                text = self.font_small.render(instruction, True, self.WHITE)
                text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 30
    
    def draw_game_screen(self):
        """Draw the game screen."""
        self.screen.fill(self.BROWN)
        
        # Draw level (obstacles, cheese, goal)
        self.level.draw(self.screen)
        
        # Draw game objects
        self.mouse.draw(self.screen)
        self.cat.draw(self.screen)
        
        # Draw HUD
        score_text = self.font_small.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        level_text = self.font_small.render(f"Level: {self.level_number}", True, self.WHITE)
        self.screen.blit(level_text, (10, 35))
        
        # Draw grid (optional debug)
        # self.draw_grid()
    
    def draw_grid(self):
        """Draw grid lines for debugging."""
        for x in range(0, self.WINDOW_WIDTH, self.GRID_SIZE):
            pygame.draw.line(self.screen, self.GRAY, (x, 0), (x, self.WINDOW_HEIGHT))
        for y in range(0, self.WINDOW_HEIGHT, self.GRID_SIZE):
            pygame.draw.line(self.screen, self.GRAY, (0, y), (self.WINDOW_WIDTH, y))
    
    def draw_game_over_screen(self):
        """Draw the game over screen."""
        self.screen.fill(self.RED)
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER", True, self.WHITE)
        game_over_rect = game_over_text.get_rect(center=(self.WINDOW_WIDTH // 2, 200))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.font_small.render("Press R to restart or SPACE for menu", True, self.WHITE)
        restart_rect = restart_text.get_rect(center=(self.WINDOW_WIDTH // 2, 400))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory_screen(self):
        """Draw the victory screen."""
        self.screen.fill(self.GREEN)
        
        # Victory text
        victory_text = self.font_large.render("VICTORY!", True, self.WHITE)
        victory_rect = victory_text.get_rect(center=(self.WINDOW_WIDTH // 2, 200))
        self.screen.blit(victory_text, victory_rect)
        
        # Score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.font_small.render("Press R to restart or SPACE for menu", True, self.WHITE)
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