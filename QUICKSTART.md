# 🚀 Quick Start Guide

## First Time Setup (2 minutes)

### Step 1: Install Dependencies
```bash
pip install pygame numpy scipy
```

### Step 2: Generate Audio Files
```bash
python generate_audio.py
```
You should see:
```
✓ Created move.wav
✓ Created win.wav
✓ Created background.mp3
```

### Step 3: Run the Game
```bash
python Python_project.py
```

## First Play

1. **Enter Your Name** - Type at least 2 characters and press Enter
2. **Click "Play"** - Start from Level 1
3. **Learn the Basics**:
   - Click a stack to select the top plate (turns yellow)
   - Click another stack to move it there
   - Stack all plates in order (1,2,3,4...) on any single stack
4. **Win!** - Complete the level before time runs out

## Quick Tips

- **Press Z** - Undo your last move
- **Press H** - Get a hint
- **Watch the Timer** - It turns red at 30 seconds
- **Check Settings** - Toggle music/sound if needed

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Z | Undo last move |
| H | Show hint |
| Enter | Confirm name input |
| Backspace | Delete character |

## Game Screens

- **Home** - Main menu with all options
- **Levels** - Select any unlocked level (🔒 = locked)
- **Help** - Full game instructions
- **Settings** - Toggle audio on/off
- **Leaderboard** - View top scores

## Troubleshooting

**No sound?**
```bash
python generate_audio.py
```

**Game crashes?**
```bash
pip install --upgrade pygame numpy scipy
```

**Want to reset progress?**
```bash
del leaderboard.txt
```

---

**That's it! Have fun! 🎮**
