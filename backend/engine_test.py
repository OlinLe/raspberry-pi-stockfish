
import chess
import chess.engine

ENGINE_PATH = "/usr/games/stockfish"

board = chess.Board()

engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

try:
    engine.configure({
        "Threads": 1,
        "Hash": 16
    })

    print(board)
    print("\nStockfish is thinking...")

    result = engine.play(
        board,
        chess.engine.Limit(time=0.5)
    )

    print("Stockfish move:", result.move.uci())

    board.push(result.move)

    print("\nUpdated board:")
    print(board)

finally:
    engine.quit()
