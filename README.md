# ♡ Pawsuit ♡

A cute 2D stealth game where a mouse must avoid a cat to collect cheese and reach safety<3

## Game Description

In Pawsuit, you control a mouse navigating through a kitchen filled with obstacles. Your objective is to collect all the cheese pieces while avoiding the cat and rolling obstacles, then reach the mouse hole to win. Everything is designed with a soft, cute aesthetic featuring pastel colors and heart particle effects.

## ✨ Features ✨

- **Grid-based movement**: Navigate using WASD keys or arrow keys
- **Intelligent AI**: Cat patrols the kitchen and chases the mouse when spotted
- **Dynamic obstacles**: Rolling obstacles that bounce around the level
- **Progressive difficulty**: Levels get more challenging with more obstacles and cheese
- **Score system**: Earn points by collecting cheese
- **Multiple game states**: Title screen, gameplay, game over, and victory screens

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python main.py
   ```

2. **Controls:**
   - **WASD** or **Arrow Keys**: Move the mouse
   - **Space**: Start game / Return to menu
   - **R**: Restart game (from game over/victory screen)

3. **Objective:**
   - Collect all yellow cheese pieces
   - Avoid the cat -> it will chase you if it sees you^^
   - Avoid obstacles
   - Reach the mouse hole to win <3

4. **Game Elements:**
   - **♡ Mouse**: Your character
   - **♡ Cat**: Enemy that patrols and chases
   - **♡ Cheese**: Collectible items (+10 points each)
   - **♡ Mouse Hole**: Victory portal
   - **♡ Obstacles**: Rolling obstacles that move in patterns
   - **♡ Walls**: Obstacles that block movement

## ♡ Game Mechanics ♡

- The cat immediately starts chasing as soon as you move 
- Stealth and timing are key -> use obstacles and corners to avoid the kitty
- Rolling obstacles move in patterns 
- Collect sparkly particle trails as you move around the kitchen
- All cheese must be collected before the mouse hole opens for victory


## Project Structure

```
pawsuit/
├── main.py             # Game engine and main loop
├── player.py           # Mouse character class
├── cat.py              # Cat AI with immediate chase behavior
├── level.py            # Level generation and management
├── particles.py        # Heart, sparkle, and twinkle particle effects
├── assets/
│   └── sounds/         # Game sound effects
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Development

The game is built using pygame and follows clean Python coding practices with:
- Type hints for better code documentation
- Comprehensive docstrings
- Modular design with separate classes for each game component
- PEP8 compliant formatting
