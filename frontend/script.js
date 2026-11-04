const boardElement = document.getElementById("board");
const statusElement = document.getElementById("status");
const restartButton = document.getElementById("restart");
const colorSelect = document.getElementById("player-color");
const historyElement = document.getElementById("move-history");

const pieces = {
    K: "♔", Q: "♕", R: "♖",
    B: "♗", N: "♘", P: "♙",
    k: "♚", q: "♛", r: "♜",
    b: "♝", n: "♞", p: "♟"
};

let gameId = null;
let currentFen = null;
let selected = null;
let busy = false;
let gameOver = false;
let playerColor = "white";

// Convert the FEN position into an 8x8 board.
function parseFen(fen) {
    const rows = fen.split(" ")[0].split("/");
    const board = [];

    for (const row of rows) {
        const squares = [];

        for (const char of row) {
            if (/[1-8]/.test(char)) {
                for (let i = 0; i < Number(char); i++) {
                    squares.push(null);
                }
            } else {
                squares.push(char);
            }
        }

        board.push(squares);
    }

    return board;
}

// Check whether a piece belongs to the player.
function isOwnPiece(piece) {
    if (!piece) return false;

    if (playerColor === "white") {
        return piece === piece.toUpperCase();
    }
    return piece === piece.toLowerCase();
}

// Draw the chessboard.
function renderBoard() {
    const board = parseFen(currentFen);
    boardElement.innerHTML = "";

    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement("button");

            // Turn the board around when playing Black.
            const boardRow = playerColor === "white" ? row : 7 - row;
            const boardCol = playerColor === "white" ? col : 7 - col;
            const file = "abcdefgh"[boardCol];
            const rank = 8 - boardRow;
            const name = file + rank;

            square.className = "square";
            square.classList.add(
                (row + col) % 2 === 0 ? "light" : "dark"
            );

            if (selected === name) {
                square.classList.add("selected");
            }

            const piece = board[boardRow][boardCol];
            square.textContent = pieces[piece] || "";

            square.onclick = () => selectSquare(name, piece);
            boardElement.appendChild(square);
        }
    }
}

// Display moves in standard chess notation.
function renderHistory(moves) {
    historyElement.innerHTML = "";

    for (let i = 0; i < moves.length; i += 2) {
        const line = document.createElement("div");
        line.textContent = `${i / 2 + 1}. ${moves[i]} ${moves[i + 1] || ""}`;
        historyElement.appendChild(line);
    }

    historyElement.scrollTop = historyElement.scrollHeight;
}

// Handle clicking chess squares.
async function selectSquare(square, piece) {
    if (busy || gameOver) return;

    if (selected === null) {
        if (isOwnPiece(piece)) {
            selected = square;
            renderBoard();
        }
        return;
    }

    if (selected === square) {
        selected = null;
        renderBoard();
        return;
    }

    const from = selected;
    selected = null;

    if (isOwnPiece(piece)) {
        selected = square;
        renderBoard();
        return;
    }

    let move = from + square;

    const board = parseFen(currentFen);
    const fromRow = 8 - Number(from[1]);
    const fromCol = "abcdefgh".indexOf(from[0]);
    const movingPiece = board[fromRow][fromCol];

    // Ask which piece to promote to.
    if (movingPiece && movingPiece.toLowerCase() === "p" &&
        square[1] === (playerColor === "white" ? "8" : "1")) {
        const choice = prompt("Promote to q, r, b, or n:", "q");

        if (choice === null) {
            renderBoard();
            return;
        }

        const promotion = choice.toLowerCase();

        if (!["q", "r", "b", "n"].includes(promotion)) {
            statusElement.textContent = "Invalid promotion";
            renderBoard();
            return;
        }

        move += promotion;
    }

    busy = true;
    statusElement.textContent = "Stockfish is thinking...";
    renderBoard();

    try {
        const response = await fetch(
            `/api/games/${gameId}/move`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ move })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Move failed");
        }

        currentFen = data.fen;
        gameOver = data.game_over;
        renderHistory(data.san_moves);

        statusElement.textContent = gameOver
            ? `Game over: ${data.result}`
            : "Your turn";

    } catch (error) {
        statusElement.textContent = error.message;
    } finally {
        busy = false;
        renderBoard();
    }
}

// Start a new chess game.
async function newGame() {
    if (busy) return;

    busy = true;
    restartButton.disabled = true;
    colorSelect.disabled = true;
    statusElement.textContent = "Starting game...";
    const chosenColor = colorSelect.value;

    try {
        const response = await fetch("/api/games", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ color: chosenColor })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not start game");
        }

        gameId = data.game_id;
        currentFen = data.fen;
        selected = null;
        gameOver = data.game_over;
        playerColor = chosenColor;

        renderBoard();
        renderHistory(data.san_moves);
        statusElement.textContent = "Your turn";

    } catch (error) {
        statusElement.textContent = error.message;
    } finally {
        busy = false;
        restartButton.disabled = false;
        colorSelect.disabled = false;
    }
}

restartButton.onclick = newGame;
newGame();
