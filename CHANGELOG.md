# Changelog

All notable changes and improvements to the Stacking Plates Game.

## [2.0.0] - 2026-02-07

### 🎉 Major Update - Feature Complete Edition

### Added
- **Settings Menu** - Toggle music and sound effects independently
- **Hint System** - Press 'H' or click Hint button for move suggestions
- **Performance Rating** - Star-based rating system (⭐⭐⭐ Perfect, ⭐⭐ Great, ⭐ Good)
- **Audio Generator** - `generate_audio.py` creates all required sound files automatically
- **Stack Labels** - Visual stack numbers for easier identification
- **Level Display** - Current level shown during gameplay
- **Time Warning** - Timer turns red when under 30 seconds
- **Welcome Message** - Player name displayed on home screen
- **Quick Start Guide** - `QUICKSTART.md` for new players
- **Requirements File** - `requirements.txt` for easy dependency installation
- **Comprehensive README** - Full documentation with installation, gameplay, and customization guides

### Improved
- **Audio System** - Added toggle controls for music and sound effects
- **Help Screen** - Updated with hint system instructions
- **UI Layout** - Better button spacing and organization on home screen
- **Visual Feedback** - Enhanced stack highlighting and selection indicators
- **Code Organization** - Added helper functions for audio control

### Fixed
- Sound effects now respect the sound toggle setting
- Win sound plays only when sound effects are enabled
- Better error handling for missing audio files

### Technical
- Added `toggle_music()` and `toggle_sound()` functions
- Implemented `get_hint()` algorithm for move suggestions
- Enhanced `draw_stacks()` with stack labels
- Expanded `draw_screens()` with settings screen and improvements
- Added keyboard shortcut 'H' for hints

---

## [1.0.0] - 2025-02-07

### Initial Release

### Features
- 5 progressive difficulty levels
- Dynamic stack system (3-5 stacks)
- Time-based challenges (60s base, increases per level)
- Move counter and scoring
- Undo system (Z key)
- Name registration system
- Leaderboard with persistent storage
- Background music and sound effects
- Gradient backgrounds
- Win/timeout screens
- Level selection with unlock system
- Help screen with instructions
- Button-based UI with hover effects
- Emoji support in UI

### Core Mechanics
- Plate stacking puzzle gameplay
- Valid move checking (can't place larger on smaller)
- Win condition detection (all plates sorted on one stack)
- Progressive difficulty (more plates and stacks per level)
- Move history tracking for undo functionality

### Audio
- Background music loop
- Plate movement sound effect
- Victory celebration sound

### Data Persistence
- Leaderboard saved to `leaderboard.txt`
- Level completion tracking
- Player name storage

---

## Future Ideas

### Potential Features
- [ ] More levels (10+ total)
- [ ] Different game modes (timed sprint, move limit, endless)
- [ ] Achievements system
- [ ] Custom themes and color schemes
- [ ] Multiplayer support
- [ ] Daily challenges
- [ ] Tutorial mode for beginners
- [ ] Replay system to watch your solutions
- [ ] Statistics tracking (total moves, time played, etc.)
- [ ] Difficulty settings (easy/normal/hard)
- [ ] Custom level editor
- [ ] Mobile touch controls
- [ ] Fullscreen mode toggle
- [ ] Pause functionality
- [ ] Better animations (smooth plate movement)
- [ ] Particle effects for wins
- [ ] More music tracks
- [ ] Volume sliders instead of on/off toggles

### Community Requests
*Add your feature requests here!*

---

**Version Format:** [Major.Minor.Patch]
- **Major:** Breaking changes or major feature additions
- **Minor:** New features, backward compatible
- **Patch:** Bug fixes and small improvements
