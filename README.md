# Pawsuit

A 2D stealth game where a clever mouse must avoid a prowling cat to collect cheese and reach safety.

## Game Description

In Pawsuit, you control a mouse navigating through a kitchen filled with dangers. Your objective is to collect all the cheese pieces while avoiding the patrolling cat and rolling tomato obstacles, then reach the mouse hole to win.

## Features

- **Grid-based movement**: Navigate using WASD keys or arrow keys
- **Intelligent AI**: Cat patrols the kitchen and chases the mouse when spotted
- **Dynamic obstacles**: Rolling tomatoes that bounce around the level
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
   - Avoid the orange cat (it will chase you if it sees you!)
   - Avoid red rolling tomatoes
   - Reach the green mouse hole to win

4. **Game Elements:**
   - **Gray Mouse**: Your character
   - **Orange Cat**: Enemy that patrols and chases
   - **Yellow Cheese**: Collectible items (+10 points each)
   - **Green Mouse Hole**: Victory goal
   - **Red Tomatoes**: Rolling obstacles that move in patterns
   - **Brown Walls**: Obstacles that block movement

## Game Mechanics

- The cat patrols in a fixed pattern but will chase you if you get too close
- When the cat loses sight of you, it will search your last known location
- Rolling tomatoes move in straight lines and bounce off walls
- You must collect ALL cheese before you can win by reaching the mouse hole
- Touching the cat or a rolling tomato ends the game

## Project Structure

```
pawsuit/
├── main.py          # Game engine and main loop
├── player.py        # Mouse character class
├── cat.py          # Cat AI and behavior
├── level.py        # Level generation and management
├── assets/
│   └── sounds/     # Game sound effects
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## Development

The game is built using pygame and follows clean Python coding practices with:
- Type hints for better code documentation
- Comprehensive docstrings
- Modular design with separate classes for each game component
- PEP8 compliant formatting

## License

This project is created for educational purposes. Feel free to modify and enhance! 