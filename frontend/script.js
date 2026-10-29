
const boardElement = document.getElementById("board");
const statusElement = document.getElementById("status");
const restartButton = document.getElementById("restart");

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

// Draw the chessboard.
function renderBoard() {
    const board = parseFen(currentFen);
    boardElement.innerHTML = "";

    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement("button");

            const file = "abcdefgh"[col];
            const rank = 8 - row;
            const name = file + rank;

            square.className = "square";
            square.classList.add(
                (row + col) % 2 === 0 ? "light" : "dark"
            );

            if (selected === name) {
                square.classList.add("selected");
            }

            const piece = board[row][col];
            square.textContent = pieces[piece] || "";

            square.onclick = () => selectSquare(name, piece);
            boardElement.appendChild(square);
        }
    }
}

// Handle clicking chess squares.
async function selectSquare(square, piece) {
    if (busy || gameOver) return;

    if (selected === null) {
        if (piece && piece === piece.toUpperCase()) {
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

    if (piece && piece === piece.toUpperCase()) {
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
    if (movingPiece === "P" && square[1] === "8") {
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
    statusElement.textContent = "Starting game...";

    try {
        const response = await fetch("/api/games", {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not start game");
        }

        gameId = data.game_id;
        currentFen = data.fen;
        selected = null;
        gameOver = false;

        renderBoard();
        statusElement.textContent = "Your turn";

    } catch (error) {
        statusElement.textContent = error.message;
    } finally {
        busy = false;
        restartButton.disabled = false;
    }
}

restartButton.onclick = newGame;
newGame();
