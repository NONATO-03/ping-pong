# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A fullscreen Pong game built with Python and `pygame`. It adds arenas, fruit-based
power-ups, special events, a bot opponent, and an Undertale-style "Determinação"
mode. The codebase and all identifiers/comments are in **Brazilian Portuguese** —
match this language when adding code.

## Commands

```sh
pip install -r requirements.txt   # only dependency is pygame
python main.py                    # run the game (opens fullscreen)
```

There is no test suite, linter, or build step. `python main.py` is the only way to
exercise the code, and it requires a display + audio device (pygame opens a real
fullscreen window via `pygame.display.set_mode(..., pygame.FULLSCREEN)` and loads
`.wav` files at startup), so it cannot run headless without a virtual display.

## Architecture

`main.py` is the heart of the game: a single `while running` loop holding module-level
global state and a **string-based state machine**. `game_state` moves between
`"menu"`, `"modo"`, `"ajuda"`, `"creditos"`, `"map_select"`, `"playing"`, and
`"gameover"`. Each loop iteration: (1) decides background music from the state,
(2) delegates menu states to `MenuState.run`, (3) runs match logic, or (4) draws game
over. New game-wide features generally mean editing this loop, not just a submodule.

The code separates **logic** from **rendering**:

- **`config.py`** — global constants imported everywhere: arena geometry
  (`ARENA_*`), the font path, and the power/fruit definitions
  (`POWER_TOTAL_TIMER`, `POWER_COLORS`, `POWER_TEXTS`). It calls `pygame.init()` and
  loads arena/fruit images **at import time**, so importing it has side effects.
- **`visual.py`** — all drawing. `render_visual(...)` is the master per-frame draw
  call for a match; other `draw_*` functions render menus, score, game over, etc.
  Holds cross-module render state like `visual.fan_angle` (mutated from `main.py`).
- **`game/entities/`** — stateful game objects: `Bola`/`BolaFake` (`bola.py`),
  `Raquete` (`raquete.py`, owns power-up activation/timers), `Habilidade` +
  `GerenciadorHabilidades` (fruit spawning/collection), `ObstaculoCruz`.
- **`game/systems/`** — cross-cutting managers: `Placar` (score + winner check),
  `BotController`, `SistemaDeSom` (all music/SFX playback), `GerenciadorEventos` +
  `FestivalDasFrutas` + cat event (`eventos.py`), the Determinação subsystem
  (`determinacao.py`: `DeterminacaoManager`, `DeterminacaoCutscene`, and the
  `pode_coletar_fruta` gate), per-arena draw functions (`arenas.py`).
- **`game/states/menu.py`** — `MenuState` drives every menu screen and returns the
  next `game_state` back to the main loop.

### Cross-module coupling to watch for

- State is passed around as **plain globals**, not encapsulated. `main.py` mutates
  `visual.fan_angle` and sets attributes on the `pygame` module itself
  (`pygame.festival_ativo`) as ad-hoc global channels read by other modules.
- **Arena selection by integer index**: `selected_map_idx` 0–4 map to
  alpha/beta/gamma/delta/epsilon; index `5` (`INDICE_DA_ARENA_ALEATORIA`) means
  "random", resolved to `arena_aleatoria_idx`. Match logic branches on the resolved
  `arena_idx` (e.g. `1` = beta's rotating fan, `2` = gamma's cross obstacles).
- Power-ups/events are coordinated through long positional argument lists threaded
  from `main.py` into `Bola.update`, `GerenciadorEventos.atualizar`, and
  `render_visual` — adding a parameter usually means updating all call sites.

### Controls (hardcoded in `main.py`)

Left paddle `W`/`S`; right paddle `↑`/`↓` (local mode) or the bot (`vs bot` mode).
`Z` returns to the menu during a match; `Space` returns to the menu from game over.

## Legacy / duplicate code

The top-level **`states/menu.py` is unused legacy** — it differs from
`game/states/menu.py`, and `main.py` imports `MenuState` only from `game.states.menu`.
Edit `game/states/menu.py`; do not assume the top-level `states/` directory is live.
