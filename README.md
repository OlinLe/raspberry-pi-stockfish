# Raspberry Pi Stockfish Chess

**[Live Demo](https://hoster.tailb60b9d.ts.net/)**

A self-hosted chess web application where users can play against the Stockfish chess engine running on a Raspberry Pi 3.

## Features

- Interactive chessboard with legal-move validation
- Stockfish AI opponent
- REST API for game creation and moves
- Public HTTPS access via Tailscale Funnel

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI, python-chess, Stockfish
- **Infrastructure:** Raspberry Pi 3, Linux, systemd, Tailscale Funnel

## Installation

```bash
sudo apt install python3-venv stockfish git
git clone https://github.com/OlinLe/raspberry-pi-stockfish.git
cd raspberry-pi-stockfish
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-chess
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` on the host machine.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check server status |
| POST | `/api/games` | Start a new game |
| POST | `/api/games/{game_id}/move` | Submit a chess move |

## Hosting

Hosted on a Raspberry Pi 3 running Linux, with systemd managing automatic startup and process recovery. Tailscale Funnel provides a stable public HTTPS address without requiring router port forwarding.
