# 1v1 Shooter Arena — v3 (audited & repaired)

This version is the result of a full audit against the PDF spec. See
`AUDIT_REPORT.md` for the complete requirement-by-requirement traceability
matrix, but the short version:

## Run it

```bash
pip install -r requirements.txt
python main.py
```

A `data/` folder is created automatically on first run, holding a single
SQLite database (`shooter_arena.db`) with `users` and `leaderboard` tables.

**Flow:** Main Menu → Sign Up (once per player) → Login & Play (both
players log in, back-to-back) → Match → Game Over (rematch / menu /
leaderboard).

- **Player 1:** `WASD` to move, `SPACE` to shoot.
- **Player 2:** **Arrow keys** to move, `ENTER` to shoot.
- Crosshairs are invisible until each player's first shot, then start
  at a random point and move with the keys above.

## What this audit fixed

1. **Critical — the whole menu was dead.** `MenuScreen` never overrode
   `next_screen()`, so clicking Sign Up / Login / Help / Leaderboard set
   the pending transition internally but the app's state machine never
   picked it up — every button appeared to do nothing and the game could
   never actually be started. Added the missing override.
2. **Input-focus bug.** Clicking any button (Create, Login, ...) blurred
   *every* text field on the screen (an `InputBox` deactivated itself on
   *any* click, even one outside every field), so after a failed login/
   sign-up attempt the player had to click back into the field before
   they could correct their input, and the auto-focus handoff into
   Player 2's username field on the login screen was fragile. Fixed the
   focus logic to only change on relevant clicks, and to auto-focus the
   username field at the start of each login stage.
3. **Bonus: real SQL persistence.** Swapped the JSON-file `DataManager`
   for a `sqlite3`-backed one (accounts + leaderboard tables), per the
   spec's optional "SQL database" bonus item. No other file needed to
   change — `DataManager`'s public interface stayed the same.
4. **Bonus: sound effects.** Added `src/core/audio.py`, a small
   `SoundManager` that synthesizes short shoot/hit/power-up/sabotage/
   game-over tones with NumPy (no external asset files needed) and fails
   silently on machines with no audio device, per the spec's optional
   sound-effects bonus item.

Everything else (OOP structure, scoring, targets/power-ups, timers,
crosshair mechanics) was already correctly implemented and is unchanged;
see `AUDIT_REPORT.md` for the full verification.

## Architecture

```
main.py                       # App: owns the window + swaps the active Screen
src/
  config.py                   # All tunable constants, colors, controls
  theme.py                    # Gradient background, starfield, glow text, panels
  data_manager.py              # DataManager — SQLite users/leaderboard, salted password hashes
  entities/
    base.py                     # GameEntity (ABC) — the one common parent class
    targets.py                   # Target, and PowerUp subclasses (inherit Target)
    player.py                     # Crosshair (GameEntity) + Player (composes a Crosshair)
  core/
    scoring.py                     # ScoreCalculator — distance + combo rules
    spawner.py                      # Spawner — keeps targets/power-ups populated
    audio.py                         # SoundManager — procedural SFX (bonus)
    game_engine.py                    # GameEngine — orchestrates one match
  ui/
    widgets.py                        # Button, InputBox (hover/focus styling)
    hud.py                              # In-match name/bullets/time/score panels
    screens.py                          # Screen (ABC) + Menu/SignUp/Login/Help/
                                         # Leaderboard/GameOver/PlayingScreen
```

### Class hierarchy

```
GameEntity (ABC)
 ├── Crosshair
 └── Target
      ├── ExtraAmmoItem   (PowerUpItem)
      ├── ExtraTimeItem   (PowerUpItem)
      └── SabotageItem    (PowerUpItem)

Screen (ABC)
 ├── MenuScreen
 ├── SignUpScreen
 ├── LoginScreen
 ├── HelpScreen
 ├── LeaderboardScreen
 ├── GameOverScreen
 └── PlayingScreen  ── wraps ──▶  GameEngine

Player  ── composes ──▶  Crosshair
GameEngine ── uses ──▶  Player, Target, Spawner, ScoreCalculator, SoundManager, Hud
App ── uses ──▶  Screen (polymorphically — never knows which concrete screen it holds)
```

### The four pillars, where to find them

| Pillar | Where |
|---|---|
| **Encapsulation** | `Player`/`Crosshair` keep state private, exposed only via read-only properties and validated mutators. `DataManager` is the only class that ever touches the database. |
| **Abstraction** | `GameEntity` and `Screen` are both `abc.ABC`s with abstract methods — callers (GameEngine, App) never touch concrete subclasses directly. |
| **Inheritance** | `GameEntity → Crosshair`, `GameEntity → Target → PowerUpItem → {ExtraAmmoItem, ExtraTimeItem, SabotageItem}`, and `Screen → {every UI screen}`. |
| **Polymorphism** | `GameEngine._fire()` calls `target.on_hit(...)` without knowing the concrete subclass. `App.run()` calls `screen.update()/.draw()/.handle_event()` without knowing which screen is active. |

## Full requirement traceability

See `AUDIT_REPORT.md` in the project root.
