import asyncio
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Literal, Optional

import chess
import chess.engine
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Pi Stockfish Chess")

ENGINE_PATH = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")

MAX_GAMES = 100
GAME_TTL = 3600

games = {}
games_lock = threading.Lock()
engine_lock = threading.Lock()

engine = None


class MoveRequest(BaseModel):
    move: str


class NewGameRequest(BaseModel):
    color: Literal["white", "black"] = "white"


def get_engine():
    global engine

    if engine is None:
        engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
        engine.configure({"Threads": 1, "Hash": 16})

    return engine


def game_data(game_id, board):
    # Replay moves to convert them to readable chess notation.
    replay = chess.Board()
    san_moves = []

    for move in board.move_stack:
        san_moves.append(replay.san(move))
        replay.push(move)

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
        "moves": [move.uci() for move in board.move_stack],
        "san_moves": san_moves
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
def new_game(request: Optional[NewGameRequest] = None):
    color = request.color if request else "white"
    board = chess.Board()

    # Stockfish makes the first move if the player picks Black.
    if color == "black":
        try:
            board.push(calculate_move(board))
        except Exception:
            raise HTTPException(503, "Chess engine unavailable")

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

        games[game_id] = {
            "board": board,
            "updated": now,
            "busy": False,
            "player_color": color
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

        if board.turn != (game["player_color"] == "white"):
            raise HTTPException(409, "Not your turn")

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
        reply = await asyncio.to_thread(calculate_move, position)
    except Exception:
        with games_lock:
            board.pop()
            game["busy"] = False
        raise HTTPException(503, "Chess engine unavailable")

    with games_lock:
        board.push(reply)
        game["updated"] = time.monotonic()
        game["busy"] = False
        return game_data(game_id, board)


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
