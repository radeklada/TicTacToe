CROSS_SYMBOL = 'X'
CIRCLE_SYMBOL = 'O'
DRAW = 'DRAW'

MIN_POS = 1
MAX_POS = 9

BOARD_SIZE = 9
MAIN_BOARD_NR = 0
MIN_BOARD_NR = 0
MAX_BOARD_NR = 9

LINES = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],

    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],

    [1, 5, 9],
    [7, 5, 3]
]


def is_symbol(s):
    return s == CIRCLE_SYMBOL or s == CROSS_SYMBOL


def next_symbol(s):
    if s == CROSS_SYMBOL:
        return CIRCLE_SYMBOL
    return CROSS_SYMBOL


def is_pos(n):
    return MIN_POS <= n <= MAX_POS


def is_result(s):
    return s == DRAW or is_symbol(s)


def _is_line(board, symbol):
    for a, b, c in LINES:
        if board.get(a) == board.get(b) == board.get(c) == symbol:
            return True
    return False


def is_mini_board_nr(board_nr):
    return (
        MIN_BOARD_NR <= board_nr <= MAX_BOARD_NR and
        board_nr != MAIN_BOARD_NR
    )


def is_board(board_nr):
    return MIN_BOARD_NR <= board_nr < MAX_BOARD_NR


def get_board_result(board):
    if _is_line(board, CROSS_SYMBOL):
        return CROSS_SYMBOL
    elif _is_line(board, CIRCLE_SYMBOL):
        return CIRCLE_SYMBOL
    elif len(board) == BOARD_SIZE:
        return DRAW
    else:
        return None


def make_board(iterable, mini):
    board = {}
    for pos, v in iterable:
        if not (MIN_POS <= pos <= MAX_POS):
            raise ValueError('Unexpected pos: {}'.format(pos))

        if mini:
            if not is_symbol(v):
                raise ValueError('Unexpected symbol: {}'.format(v))
        else:
            if not is_result(v):
                raise ValueError('Unexpected result: {}'.format(v))

        board[pos] = v

    return board


def mini_board_nr(row_index, col_index):
    index = (row_index // 3 * 3 + col_index // 3)
    return index + 1


def mini_board_pos(row_index, col_index):
    index = (row_index % 3) * 3 + (col_index % 3)
    return index + 1


def all_boards_positions():
    results = []
    for row_index in range(9):
        for col_index in range(9):
            board_nr = mini_board_nr(row_index, col_index)
            pos = mini_board_pos(row_index, col_index)
            results.append((board_nr, pos))
    return results


def to_rows(values, row_size):
    rows = []
    for i in range(0, len(values), row_size):
        rows.append(values[i:i + row_size])
    return rows
