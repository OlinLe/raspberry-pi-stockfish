
import asyncio
import os
import threading
import time
import uuid

import chess
import chess.engine
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Pi Stockfish Chess")

ENGINE_PATH = os.getenv(
    "STOCKFISH_PATH", "/usr/games/stockfish"
)

MAX_GAMES = 100
GAME_TTL = 3600

games = {}
games_lock = threading.Lock()
engine_lock = threading.Lock()

engine = None


class MoveRequest(BaseModel):
    move: str


def get_engine():
    global engine

    if engine is None:
        engine = chess.engine.SimpleEngine.popen_uci(
            ENGINE_PATH
        )
        engine.configure({
            "Threads": 1,
            "Hash": 16
        })

    return engine


def game_data(game_id, board):
    return {
        "game_id": game_id,
        "fen": board.fen(),
        "turn": "white" if board.turn else "black",
        "game_over": board.is_game_over(claim_draw=True),
        "result": (
            board.result(claim_draw=True)
            if board.is_game_over(claim_draw=True)
            else None
        ),
        "moves": [
            move.uci() for move in board.move_stack
        ]
    }


def calculate_move(board):
    with engine_lock:
        result = get_engine().play(
            board,
            chess.engine.Limit(time=0.3)
        )
        return result.move


@app.get("/api/health")
def health():
    return {"status": "online"}


@app.post("/api/games")
def new_game():
    now = time.monotonic()

    with games_lock:
        expired = [
            gid for gid, g in games.items()
            if now - g["updated"] > GAME_TTL
            and not g["busy"]
        ]

        for gid in expired:
            del games[gid]

        if len(games) >= MAX_GAMES:
            raise HTTPException(503, "Server is busy")

        game_id = uuid.uuid4().hex
        board = chess.Board()

        games[game_id] = {
            "board": board,
            "updated": now,
            "busy": False
        }

    return game_data(game_id, board)


@app.post("/api/games/{game_id}/move")
async def make_move(game_id: str, request: MoveRequest):
    with games_lock:
        game = games.get(game_id)

        if game is None:
            raise HTTPException(404, "Game not found")

        if game["busy"]:
            raise HTTPException(409, "Game is busy")

        board = game["board"]

        if board.is_game_over(claim_draw=True):
            raise HTTPException(400, "Game is over")

        try:
            move = chess.Move.from_uci(request.move)
        except ValueError:
            raise HTTPException(400, "Invalid move format")

        if move not in board.legal_moves:
            raise HTTPException(400, "Illegal move")

        game["busy"] = True
        board.push(move)
        game["updated"] = time.monotonic()

        if board.is_game_over(claim_draw=True):
            game["busy"] = False
            return game_data(game_id, board)

        position = board.copy(stack=True)

    try:
        reply = await asyncio.to_thread(
            calculate_move, position
        )
    except Exception:
        with games_lock:
            game["busy"] = False
        raise HTTPException(
            503, "Chess engine unavailable"
        )

    with games_lock:
        board.push(reply)
        game["updated"] = time.monotonic()
        game["busy"] = False
        return game_data(game_id, board)


from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@app.get("/")
def homepage():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)

