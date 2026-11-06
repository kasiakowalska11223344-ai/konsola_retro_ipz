# Snake

A modular Pygame Snake project.

## Files

- `main.py` — starts the game and runs the main loop.
- `settings.py` — window, board, movement, color, and direction settings.
- `board.py` — checkerboard rendering and grid-to-pixel conversion.
- `snake.py` — snake state, smooth movement, turn handling, collisions, and drawing.
- `food.py` — food spawning and drawing.
- `ui.py` — score and end screens.

## Run

Install Pygame:

```bash
python -m pip install pygame-ce
```

Run the game from this folder:

```bash
python main.py
```

Use the arrow keys to start and steer. Press `Esc` to quit.

The game uses a 1280x720 fullscreen window and a 17x15 tile board.
