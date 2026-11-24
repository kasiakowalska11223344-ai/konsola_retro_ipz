# Snake Arcade

A modular Pygame Snake game designed for the GamingPiLauncher arcade cabinet.

## Requirements

- Python 3.10+
- Pygame Community Edition (pygame-ce)

Install Pygame Community Edition with pip:

```bash
python3 -m pip install pygame-ce
```

## Run

```bash
python3 main.py
```

## Arcade controls

- Joystick: move the snake (WASD events from GamingPiLauncher).
- `BUTTON_1_1` / SPACE: confirm a menu choice or save initials.
- `BUTTON_1_2` / RETURN: quit the game.
- Arrow keys also work for movement when testing with a regular keyboard.
- ESC quits during desktop testing.

## Leaderboard

The game stores the local top ten in `leaderboard.json` in the project directory.
After a round ends, it displays the result for about two seconds, then shows the
leaderboard and asks whether to save the score. LEFT/RIGHT toggles YES/NO and
SPACE confirms. If the score qualifies for the top ten, enter three initials:
UP/DOWN changes the selected letter, LEFT/RIGHT selects a letter slot, and
SPACE saves. The final leaderboard remains visible afterward. The player can only quit
with `BUTTON_1_2` / RETURN (or ESC during desktop testing); SPACE no longer
starts another round.

The leaderboard file is created automatically the first time a score is saved.

## Assets

- Font: `assets/fonts/PressStart2P-Regular.ttf`
- Sound effects: `assets/sounds/*.wav`

## Project layout

```text
snake_project/
│
├── main.py
├── settings.py
├── snake.py
├── board.py
├── food.py
├── ui.py
├── sounds.py
├── fonts.py
├── leaderboard.py
│
├── assets/
│   ├── fonts/
│   │   └── PressStart2P-Regular.ttf
│   └── sounds/
│       ├── turn.wav
│       ├── eat_fruit.wav
│       └── game_over.wav
│
├── GamingPiLauncher/
│   ├── gameSettings.json
│   └── imgs/
│       ├── logo.png
│       └── gameDashboardImg.png
│
├── leaderboard.json
├── .gitignore
└── README.md
```
