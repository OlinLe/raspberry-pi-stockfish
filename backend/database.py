import sqlite3
from contextlib import closing
from pathlib import Path

# The database file is kept in the project folder.
DB_PATH = Path(__file__).resolve().parent.parent / "chess.db"


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS moves (
                    game_id TEXT NOT NULL,
                    ply INTEGER NOT NULL,
                    uci TEXT NOT NULL,
                    PRIMARY KEY (game_id, ply)
                )
            """)


def save_game(game_id, board):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute(
                "INSERT INTO games (id) VALUES (?)",
                (game_id,)
            )

            # If the player chose Black, Stockfish already made move 1.
            if board.move_stack:
                conn.execute(
                    "INSERT INTO moves (game_id, ply, uci) VALUES (?, ?, ?)",
                    (game_id, 1, board.move_stack[0].uci())
                )


def save_new_moves(game_id, board, count):
    # Get the last 1 or 2 moves from the game.
    new_moves = board.move_stack[-count:]
    first_ply = len(board.move_stack) - len(new_moves) + 1

    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            for i, move in enumerate(new_moves):
                conn.execute(
                    "INSERT INTO moves (game_id, ply, uci) VALUES (?, ?, ?)",
                    (game_id, first_ply + i, move.uci())
                )


def get_totals():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        game_count = conn.execute(
            "SELECT COUNT(*) FROM games"
        ).fetchone()[0]
        move_count = conn.execute(
            "SELECT COUNT(*) FROM moves"
        ).fetchone()[0]

    return game_count, move_count
