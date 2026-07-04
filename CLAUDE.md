# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Gomoku (五子棋) two-player board game built with Python and tkinter. 15×15 board, black plays first, win by connecting five pieces in a row (horizontal, vertical, or diagonal).

## Commands

```bash
# Run the game
python3 gomoku.py
```

No dependencies beyond Python 3.x with tkinter (included in standard library).

## Architecture

Single-file application (`gomoku.py`) with one main class:

- **`GomokuGame`** — manages all game state and UI
  - `board` — 15×15 2D list (0=empty, 1=black, 2=white)
  - `_on_click()` → `_place_piece()` → `_check_win()` — core input→logic→win pipeline
  - `_check_win()` — scans 4 directions (→, ↓, ↘, ↙) from the placed piece
  - `undo_move()` — reverts the last two moves (one per player)
  - `reset_game()` — clears board and state
  - Canvas-based rendering with tkinter, no external game/physics engine

No complex rules (禁手) are implemented — first to five in a row wins.

## Git

SSH key at `~/.ssh/id_ed25519_gomoku` is configured for pushing to GitHub. `~/.ssh/config` maps `github.com` to use it.
