# Raspberry Pi Stockfish Chess

**[Live Demo](https://hoster.tailb60b9d.ts.net/)**

A self-hosted chess web application running on a Raspberry Pi 3 that allows users to play against the Stockfish chess engine.

## Features

- Chessboard that checks for legal moves

- Play as White or Black

- Move history using chess notation

- monitoring of Raspberry Pi CPU, RAM, disk and temperature

- Saving game and move statistics using SQLite

- REST API for gameplay and server statistics

- Public HTTPS access using Tailscale Funnel

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript

- **Backend:** Python, FastAPI, python-chess, Stockfish

- **Database:** SQLite

- **Infrastructure:** Raspberry Pi 3 Linux, systemd, Tailscale Funnel

- **Monitoring:** psutil

## Installation

```bash

sudo apt install python3-venv stockfish git

git clone https://github.com/OlinLe/raspberry-pi-stockfish.git

cd raspberry-pi-stockfish

python3 -m venv .venv

source .venv/bin/activate

pip install fastapi uvicorn python-chess psutil

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

```

To view the website, go to http://127.0.0.1:8000 on the Raspberry Pi.

The SQLite database named `chess.db` is created automatically when the application starts.


## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check if the server is working |
| GET | `/api/stats` | Get system metrics and chess data |
| POST | `/api/games` | Start a new game |
| POST | `/api/games/{game_id}/move` | Make a chess move |


## Hosting

The project is run on a Raspberry Pi 3 running Linux. The systemd service manager starts the application automatically after boot and recovers from crashes. The Tailscale Funnel allows for public HTTPS access to the application without having to forward any ports on the router.

SQLite keeps game. Move data even after server restarts. The current game session is stored in memory.
