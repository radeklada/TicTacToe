const BOARD_COUNT = 9;
const POS_COUNT = 9;
const CIRCLE_SYMBOL = "O";
const CROSS_SYMBOL = "X";
const DRAW = "DRAW";

const CROSS_MARKER = 'cross-marker';
const CIRCLE_MARKER = 'circle-marker';
const SUGGESTION_MARKER = 'suggestion-marker';
const BOARD_ODD_MARKER = 'board-odd-marker';
const BOARD_EVEN_MARKER = 'board-even-marker';
const CROSS_STRONG_MARKER = 'cross-strong-marker';
const CIRCLE_STRONG_MARKER = 'circle-strong-marker';
const ALL_MARKERS = [
    CROSS_MARKER,
    CIRCLE_MARKER,
    SUGGESTION_MARKER,
    BOARD_ODD_MARKER,
    BOARD_EVEN_MARKER,
    CROSS_STRONG_MARKER,
    CIRCLE_STRONG_MARKER
]


function getSymbolName(symbol) {
    if (symbol === CROSS_SYMBOL) {
        return 'cross';
    }
    else if (symbol === CIRCLE_SYMBOL) {
        return 'circle';
    }
    else {
        return null;
    }
}


function isStrongMarker(marker) {
    return (
        marker === CROSS_MARKER ||
        marker === CIRCLE_MARKER ||
        marker === CROSS_STRONG_MARKER ||
        marker === CIRCLE_STRONG_MARKER
    );
}


function getMarkerBySymbol(symbol) {
    if (symbol === CROSS_SYMBOL) {
        return CROSS_MARKER;
    }
    return CIRCLE_MARKER;
}


function toBoards($fields) {
    const boards = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}, 9: {}};
    console.log($fields)
    $fields.each(function () {
        const $field = $(this);
        const boardNr = $field.data('board-nr');
        const pos = $field.data('pos');
        boards[boardNr][pos] = $field;
    });

    return boards;
}


function toMainBoard(moves) {
    const board = {};
    moves.forEach(function (move) {
        var boardNr = move['board_nr'];
        var position = move['position'];
        var value = move['value'];
        if (boardNr === 0){
            board[position] = value;
        }
    });
    return board;
}


function clearField($field) {
    ALL_MARKERS.forEach(function (marker) {
        $field.removeClass(marker);
    })
}


function clearBoards(boards) {
    for (var boardNr = 1; boardNr <= BOARD_COUNT; ++boardNr) {
        for (var pos = 1; pos <= POS_COUNT; ++pos) {
            clearField(boards[boardNr][pos]);
        }
    }
}


function unmarkField($field, marker) {
    $field.removeClass(marker);
}


function markField($field, marker) {
    if (isStrongMarker(marker)) {
        clearField($field);
        $field.addClass(marker);
    }
    else if (!$field.hasClass(CROSS_MARKER) && !$field.hasClass(CIRCLE_MARKER)) {
        $field.addClass(marker);
    }
}

function unmarkBoard(board, marker) {
  for (var i = 1; i <= 9; ++i) {
      var $field = board[i];
      unmarkField($field, marker);
  }
}


function markBoard(board, marker) {
    for (var i = 1; i <= 9; ++i) {
      const $field = board[i];
      markField($field, marker);
    }
}


function markMiniBoardsWinner(miniBoards, mainBoard) {
    for (var i = 1; i <= 9; ++i) {
        var result = mainBoard[i];
        if (result && result !== DRAW) {
            var marker = getMarkerBySymbol(result);
            markBoard(miniBoards[i], marker);
        }
    }
}


function checkFields($field, boardNr, pos) {
    console.log(boardNr, pos);
}

//{"moves": [{"board_nr": 3, "position": 3, "value": "X"}
function insertMoves(miniBoards, moves) {
    moves.forEach(function (move) {
        var boardNr = move['board_nr'];
        var position = move['position'];
        var value = move['value'];
        if (boardNr > 0){
            var $field = miniBoards[boardNr][position];
            var marker = getMarkerBySymbol(value);
            markField($field, marker);
        }
    });
}


function setDefaultFieldsBackground(boards) {
    for (var boardNr = 1; boardNr <= BOARD_COUNT; ++boardNr) {
        for (var pos = 1; pos <= POS_COUNT; ++pos) {
            var $field = boards[boardNr][pos];
            if (boardNr % 2 === 0){
                markField($field, BOARD_EVEN_MARKER);
            }
            else {
                markField($field, BOARD_ODD_MARKER);
            }
        }
    }
}


function getLastMoveBySymbol(moves, symbol) {
    for (var i = moves.length - 1; i > 0; --i) {
        if (moves[i]['value'] === symbol && moves[i]['board_nr'] > 0) {
            return moves[i];
        }
    }
    return null;
}


function markLastMoveBySymbol(moves, miniBoards, symbol, marker) {
    var lastMove = getLastMoveBySymbol(moves, symbol);
    if (lastMove) {
        console.log(lastMove);
        miniBoards
        var boardNr = lastMove['board_nr'];
        var position = lastMove['position'];
        var $field = miniBoards[boardNr][position];
        markField($field, marker);
    }
}


function markLastUsedFields(moves, miniBoards) {
    markLastMoveBySymbol(moves, miniBoards, CROSS_SYMBOL, CROSS_STRONG_MARKER);
    markLastMoveBySymbol(moves, miniBoards, CIRCLE_SYMBOL, CIRCLE_STRONG_MARKER);
}


function setupBoard(moves, onFieldClick) {
    const $fields = $(".ttt td");
    const miniBoards = toBoards($fields);
    const mainBoard = toMainBoard(moves);
    setDefaultFieldsBackground(miniBoards);
    insertMoves(miniBoards, moves);
    markMiniBoardsWinner(miniBoards, mainBoard);
    markLastUsedFields(moves, miniBoards);
    const board = {
        'enabled': true,
        'miniBoards': miniBoards,
    };
    $fields.click(function () {
       const $field = $(this);
       if (board['enabled']) {
           onFieldClick(board, $field, $field.data("board-nr"), $field.data("pos"));
       }
    });
    // markBoard(boards[1], CROSS_MARKER);
    // markBoard(boards[2], CIRCLE_MARKER);
    // markBoard(boards[3], CROSS_MARKER);
    // markBoard(boards[4], CIRCLE_MARKER);
    // markBoard(boards[5], CROSS_MARKER);
    //
    // markField(boards[7][7], CROSS_MARKER);
    // markBoard(boards[7], SUGGESTION_MARKER);
    // unmarkBoard(boards[7], SUGGESTION_MARKER);
    // clearBoards(boards);
}


function setupMessageDisplayer(message) {
    $('#message-displayer').text(message);
}


function getDataFromScript(scriptId) {
    const text = $("#" + scriptId).text();
    return JSON.parse(text);
}


function nextSymbol(symbol) {
    if (symbol === CROSS_SYMBOL) {
        return CIRCLE_SYMBOL;
    }
    return CROSS_SYMBOL;
}


function calcMiniBoardMoves(moves) {
    var counter = 0;
    moves.forEach(function(move) {
        if (move['board_nr'] > 0) {
            ++counter;
        }
    });
    return counter;
}


function isYourMove(game) {
    var n = calcMiniBoardMoves(game['moves']);
    return (
        (game['your_symbol'] === CROSS_SYMBOL && (n % 2 === 0)) ||
        (game['your_symbol'] === CIRCLE_SYMBOL && (n % 2 === 1))
    );
}


function isGameRunning(game) {
    return game['result'] === null;
}


function getMessageFromGame(game) {
    if (game['result'] === game['your_symbol']) {
        return "Wygra??e??";
    }
    else if (game['result'] === nextSymbol(game['your_symbol'])) {
        return "Przegra??e??";
    }
    else if (game['result'] === DRAW) {
        return "Remis";
    }
    else if (isYourMove(game)) {
        return "Tw??j ruch";
    }
    else {
        return "Czekaj na przeciwnika";
    }
}


function lockBoardContext(board, fn) {
    board['enabled'] = false;
    fn(function () {
        board['enabled'] = true;
    });
}


function sendUpdateBoardRequest(boardNr, position, done) {
    //tu wywo??amy ajax
    //tu zwracamy callback
    // setTimeout(function () {
    //     done({status: 200});
    // }, 3000)
    $.post("", JSON.stringify({
        boardNr:boardNr,
        position: position
    }), function (data) {
        console.log(data);
        done({status: 200});
    }).fail(function (response) {
        console.log(response.responseJSON);
        done({status: response.status});
    });
}


function updateBoard(board, boardNr, position, symbol) {
    const miniBoard = board['miniBoards'][boardNr];
    const $field = miniBoard[position];
    const marker = getMarkerBySymbol(symbol);
    markField($field, marker);
}

function setupAutoReloading(timeout) {
    setTimeout(function () {
        window.location.reload(true);
    }, timeout);
}

const AUTO_RELOADING_TIMEOUT = 1000; // ms


function setupNewGameLink(game) {
    if (!isGameRunning(game)) {
        var link = $('#new-game-link');
        link.show();
    }
}


function setupSymbolIcon(symbol) {
    var elementSelector = '#symbol-icon-' + getSymbolName(symbol);
    var $icon = $(elementSelector);
    $icon.show();
}


$(function () {
    const gameState = getDataFromScript("game-state");
    // const gameState = {"moves": [1, 1], "result": null, "your_symbol": "X"};
    setupMessageDisplayer(getMessageFromGame(gameState));
    setupSymbolIcon(gameState['your_symbol'])
    setupNewGameLink(gameState);
//    setupAutoReloading(AUTO_RELOADING_TIMEOUT);

//     onServer(function (event) {

//     });

    setupBoard(gameState['moves'], function (board, $field, boardNr, position) {
        lockBoardContext(board, function (unlockBoard) {
            console.log("klikni??to", boardNr, position)
            sendUpdateBoardRequest(boardNr, position, function (response) {
                if (response.status === 200) {
                    updateBoard(board, boardNr, position, gameState['your_symbol']);
                }
                window.location.reload(true);
                unlockBoard();
            });
        });
    });
});