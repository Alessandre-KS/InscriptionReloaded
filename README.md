# Inscription RELOADED 🎮

> **Academic Project Notice**: This game is a **1st-semester school project** connected to [**GamersDen**](https://github.com/Alessandre-KS/GamersDen). Check out the [GamersDen repository](https://github.com/Alessandre-KS/GamersDen) to learn more about the broader ecosystem and project context!

---

## 📖 Overview

**Inscription RELOADED** is an action-packed 2D wave-based platform survival shooter built with Python and Pygame (`pygame-ce`). 

Defend yourself against relentless waves of mythical and monstrous enemies, upgrade and switch between multiple firearms, blast enemies away with a kinetic knockback attack, fight alongside an autonomous AI companion, and survive epic boss battles against the Fire Boss and Dragon Boss.

---

## 🕹️ Controls

| Key / Input | Action |
| :--- | :--- |
| <kbd>W</kbd> or <kbd>Space</kbd> | Jump |
| <kbd>A</kbd> / <kbd>D</kbd> | Move Left / Right |
| <kbd>Left Click</kbd> | Shoot Weapon (mouse-aimed) |
| <kbd>Right Click</kbd> | AoE Knockback Blast (pushes & interrupts nearby enemies) |
| <kbd>Q</kbd> | Switch Weapon (AK ➔ Unlimited Pistol ➔ Spread Shotgun) |
| <kbd>ESC</kbd> | Return to Title Menu |
| <kbd>M</kbd> | Toggle Debug Stats Display |
| <kbd>H</kbd> | Toggle Hitbox & Pixel-Mask Outlines |
| <kbd>I</kbd> | Toggle God Mode (Debug / Invincibility) |

---

## ✨ Features

- **Arsenal System**:
  - **Pistol**: Unlimited ammunition, medium fire-rate, precision shots.
  - **AK**: High-velocity rapid fire, high damage against swarms.
  - **Shotgun**: Triple-bullet spread blast, high stopping power.
  - **Knockback Blast**: Radial kinetic pulse that knocks enemies back and cancels their attack windups.
- **Dynamic Wave Combat**:
  - Progressive wave scaling with increasing enemy limits and spawn speed factors.
  - Cooldown countdown breaks between waves with automatic health and ammo replenishment.
  - Boss battles on milestone waves (Wave 10 Fire Boss, Wave 20 Dragon Boss, Wave 30+ dual-boss encounters).
- **10 Unique Enemy Types**:
  - **Ground**: Frog, Ghoul, Axolotl, Witch (with homing fire projectiles).
  - **Flying**: Bat, Rocket Enemy, Reaper.
  - **Bosses**: Fire Boss (flame aura and enrage) and Dragon Boss (tracking, roaring chase, and breath attacks).
- **Autonomous Ally Companion**:
  - An AI-controlled ally who tracks nearby ground enemies, initiates multi-hit martial arts combos, launches uppercuts, and assists the player.
- **Persistent SQLite Leaderboard**:
  - High scores, player names, and waves reached are saved to an embedded SQLite database (`leaderboard.db`).
  - Highlights the #1 champion with a golden crown in the leaderboard menu.
- **Modular & Optimized Architecture**:
  - Preloaded asset frames and precomputed collision masks for 60 FPS performance without frame stutter.
  - Clean separation into 10 decoupled modules.

---

## 📁 Project Structure

```
Inscription RELOADED/
├── assets/ or ASSETS/      # Sound effects, music tracks, fonts, and sprite frames
├── constants.py            # Screen dimensions, physics constants, colors, button rects
├── database.py             # SQLite database manager for leaderboard persistence
├── state.py                # Runtime game state, sprite group references, and screen shake
├── assets.py               # Preloaded sprite caches, frame loaders, and audio controller
├── weapons.py              # Bullet physics, Gun weapon cycling, and Knife AoE blast
├── player.py               # Player movement, platform collisions, and Ally companion AI
├── enemies.py              # Enemy behaviors, animations, projectile spawns, and boss logic
├── systems.py              # WaveSystem, EnemySpawner, and ScoreSystem
├── ui.py                   # Title screen, Leaderboard, How-To-Play, and Name Entry menus
├── main.py                 # Main orchestration entry point and Pygame 60 FPS loop
├── leaderboard.db          # SQLite database storing high scores
└── test_modules.py         # Self-check verification test suite
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have **Python 3.10 or higher** installed.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Alessandre-KS/InscriptionReloaded.git
   cd InscriptionReloaded
   ```

2. Install Pygame Community Edition (`pygame-ce`):
   ```bash
   pip install pygame-ce
   ```

3. Launch the game:
   ```bash
   python main.py
   ```

### Standalone Executable (.exe)

A standalone Windows executable is built in the `dist/` directory:
- Simply double-click [`dist/InscriptionReloaded.exe`](file:///w:/Inscription%20RELOADED/dist/InscriptionReloaded.exe) to play — **no Python or library installation required**!
- To rebuild the `.exe`:
  ```bash
  pip install pyinstaller
  pyinstaller --noconfirm --onefile --windowed --icon="icon.ico" --add-data "ASSETS;ASSETS" --name "InscriptionReloaded" main.py
  ```

---

## 🧪 Testing

To run the automated modular self-check test suite:
```bash
python test_modules.py
```

---

## 🔗 Related Projects

- **[GamersDen](https://github.com/Alessandre-KS/GamersDen)** — The main hub / parent project for this 1st-semester coursework.
