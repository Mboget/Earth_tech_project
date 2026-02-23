# Earth_tech_project

2D Pygame game about waste sorting with trajectory, levels, and menu.

## Features
- Drag and drop to launch waste (partial trajectory shown).
- Bins aligned on the right, waste on the left.
- Level system with progressive difficulty.
- Space mini-game after each sorting level (avoid debris and collect stars).
- Start menu + level selection (progressive unlock).
- Controls menu (choose WASD or ZQSD).
- Pause menu via `Esc`.
- Close button (red X) in the top-right.
- Local progress save.

## Requirements
- Python 3.x
- Pygame
- OpenCV (for intro video playback)

Install Pygame:
```bash
pip install pygame
```

Install OpenCV:
```bash
pip install opencv-python
```

Generate the intro video with Manim (auto on first launch if missing):
```bash
pip install manim
manim -pqh asset/intro_manim.py IntroText
```
Then copy the generated `IntroText.mp4` to `Earth_tech_project/asset/intro.mp4`.

## Run the game
From `Earth_tech_project/src`:
```bash
python main.py
```

## Controls
- Click + drag on the waste: launch
- `Esc`: pause / resume
- Click the red X: close the game

## Progress save
Progress is stored in:
- `Earth_tech_project/src/app/progress.json`

## Project structure
```
Earth_tech_project/
  .gitignore
  assets/
  src/
    main.py
    app/
      __init__.py
      constants.py
      ui.py
      menu.py
      game.py
      bins.py
      trajectory.py
      waste_item.py
      space_game.py
      progress.json
  README.md
  requirements.txt
```
