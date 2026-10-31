# Raspberry Pi Stockfish Chess

CURRENT WORKING LINK: https://ellen-hugo-improve-columnists.trycloudflare.com/

A self-hosted chess website where you can play against Stockfish running on a Raspberry Pi 3.

## Features

- Interactive chessboard with legal-move validation
- Stockfish AI opponent
- REST API for game creation and moves
- Self-hosted Linux server with public HTTPS access

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI, python-chess
- **Hosting:** Raspberry Pi 3, Linux, systemd, Cloudflare Tunnel

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

Open `http://127.0.0.1:8000` on the Raspberry Pi.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check server status |
| POST | `/api/games` | Start a new game |
| POST | `/api/games/{game_id}/move` | Submit a chess move |

## Hosting

Hosted on a Raspberry Pi 3 using systemd for automatic startup and Cloudflare Tunnel for temporary public HTTPS access.
