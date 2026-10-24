# ⚔️ Inscription RELOADED

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame--ce-2.5+-FFE873?style=for-the-badge&logo=python&logoColor=black)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

> 🎓 **Academic Project Notice**: This game is a **1st-semester school project** connected to [**GamersDen**](https://github.com/Alessandre-KS/GamersDen). Visit the [GamersDen repository](https://github.com/Alessandre-KS/GamersDen) to learn more about the complete ecosystem and project background!

---

## 📖 Overview

**Inscription RELOADED** is an action-packed 2D wave-based platform survival shooter built using Python and Pygame Community Edition (`pygame-ce`).

Step into the arena, survive relentless onslaughts of monstrous invaders, strategically switch between distinct firearms, unleash kinetic shockwaves to knock back aggressive mobs, fight shoulder-to-shoulder with an autonomous martial-arts AI companion, and survive devastating milestone boss battles.

---

## 📦 Quick Play (No Python Required)

Want to jump straight into the action without installing Python or packages?

1. Head over to **[Releases](https://github.com/Alessandre-KS/InscriptionReloaded/releases)** or the local `dist/` folder.
2. Download and run [`InscriptionReloaded.exe`](dist/InscriptionReloaded.exe).
3. That's it — double-click and play!

---

## 🕹️ Controls

| Key / Input | Action | Description |
| :--- | :--- | :--- |
| <kbd>W</kbd> or <kbd>Space</kbd> | **Jump** | Leap across platforms and dodge ground hazards |
| <kbd>A</kbd> / <kbd>D</kbd> | **Move Left / Right** | Traverse the arena floor and platforms |
| <kbd>Left Click</kbd> | **Shoot Weapon** | Fire your active gun toward the mouse cursor |
| <kbd>Right Click</kbd> | **Kinetic Blast** | AoE shockwave that knocks back and interrupts nearby enemies |
| <kbd>Q</kbd> | **Switch Weapon** | Cycle through: `AK-47` ➔ `Pistol` ➔ `Shotgun` |
| <kbd>ESC</kbd> | **Menu / Pause** | Return to Title Screen |
| <kbd>M</kbd> | **Stats Display** | Toggle live ground/flying count and game stats |
| <kbd>H</kbd> | **Hitboxes** | Toggle debug hitbox outlines and pixel masks |
| <kbd>I</kbd> | **God Mode** | Toggle debug invincibility mode |

---

## ✨ Key Features

### 🔫 Arsenal & Combat
- **Pistol**: High precision, unlimited ammunition — your dependable fallback sidearm.
- **AK-47**: High fire-rate assault rifle engineered to shred through swarms of ground and airborne monsters.
- **Shotgun**: Devastating triple-pellet spread designed for close-quarters crowd clearing.
- **Kinetic Blast**: Emergency radial pulse that pushes enemies away and cancels active enemy attack windups.

### 🌊 Dynamic Wave Survival
- **Intelligent Scaling**: Enemy spawn rates, health pools, and active limits increase with every wave survived.
- **Tactical Breathers**: 5-second countdown rest periods between waves with automatic player healing and ammo replenishment.
- **Milestone Boss Battles**:
  - **Wave 10**: The raging **Fire Boss** equipped with a fiery aura and enrage triggers.
  - **Wave 20**: The airborne **Dragon Boss** featuring screen-shaking roars and tracking breath attacks.
  - **Wave 30+**: Dual-boss endurance gauntlets.

### 👹 10 Unique Enemy Types
- **Ground Forces**:
  - 🐸 **Frog**: Agile jumper that hops across platforms.
  - 🧟 **Ghoul**: Relentless melee brawler.
  - 🦎 **Axolotl**: Fast-closing amphibious predator.
  - 🧙‍♀️ **Witch**: Ranged caster firing homing cursed projectiles.
- **Airborne Threats**:
  - 🦇 **Bat**: Erratic flyer that dives at vulnerable angles.
  - 🚀 **Rocket Enemy**: High-speed kamikaze drone targeting player coordinates.
  - 💀 **Reaper**: Floating specter with telegraphed slashing attacks.
- **Bosses**:
  - 🔥 **Fire Boss**: Heavy ground behemoth.
  - 🐉 **Dragon Boss**: Screen-dominating flying terror.

### 🥋 Autonomous Ally Companion
- An intelligent, autonomous NPC ally fights alongside you on the ground.
- Automatically acquires targets, rushes threats, and unleashes multi-hit martial arts combos and anti-air uppercuts.

### 🏆 Persistent SQLite Leaderboard
- Embedded database ([`leaderboard.db`](leaderboard.db)) permanently records high scores, waves reached, and timestamps.
- Features a **Name Entry** screen after game over with full input validation.
- Top-ranking champion is crowned with a gold crown badge on the leaderboard screen.

### ⚡ 60 FPS Optimized Engine
- Assets, frames, and collision masks are precomputed and cached at startup for butter-smooth 60 FPS gameplay with zero frame-stutter on enemy spawns.

---

## 📁 Project Architecture

The codebase is organized into 10 clean, modular Python files:

```
Inscription RELOADED/
├── assets/                 # Audio files, fonts, and sprite sheets
├── constants.py            # Window dimensions, physics constants, colors, button rects
├── database.py             # SQLite database operations and cached query helpers
├── state.py                # Runtime game state, sprite group references, and screen shake
├── assets.py               # Preloaded sprite caches, frame loaders, and sound controller
├── weapons.py              # Bullet physics, Gun weapon cycling, and Knife AoE blast
├── player.py               # Player movement, platform collisions, and Ally companion AI
├── enemies.py              # Enemy behaviors, animations, projectile spawns, and boss logic
├── systems.py              # WaveSystem, EnemySpawner, and ScoreSystem
├── ui.py                   # Title screen, Leaderboard, How-To-Play, and Name Entry menus
├── main.py                 # Main orchestration entry point and Pygame 60 FPS loop
├── leaderboard.db          # Embedded SQLite database for persistent records
└── test_modules.py         # Automated modular self-check test suite
```

---

## 🚀 Running from Source

### 1. Prerequisites
- **Python 3.10** or higher installed on your system.

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/Alessandre-KS/InscriptionReloaded.git
cd InscriptionReloaded

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Game
```bash
python main.py
```

---

## 🛠️ Building the Executable

To compile a standalone `.exe` from source:
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon="icon.ico" --add-data "ASSETS;ASSETS" --name "InscriptionReloaded" main.py
```
The output executable will be created in the `dist/` folder.

---

## 🧪 Testing

Run the automated test suite to verify all modules and gameplay logic:
```bash
python test_modules.py
```

---

## 🔗 Related Projects

- **[GamersDen](https://github.com/Alessandre-KS/GamersDen)** — The main hub / parent repository for this 1st-semester academic coursework.
