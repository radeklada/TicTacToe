from random import choice
from math import inf
from copy import deepcopy

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
    elif None not in list(board.values()):
        return DRAW
    else:
        return None

def init_board():
    return {pos: None for pos in range(MIN_POS, MAX_POS + 1)}


def make_board(iterable, mini):
    board = init_board()
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


def to_boards(moves):
    boards = {board_nr: init_board() for board_nr in
              range(MIN_BOARD_NR, MAX_BOARD_NR + 1)}
    for m in moves:
        boards[m.board_nr][m.position] = m.value
    return boards


def next_board_nr(moves):
    for m in moves[::-1]:
        if m.board_nr != MAIN_BOARD_NR:
            return m.position
    return None


def _get_empty_cells(board):
    cells = []
    for pos, val in board.items():
        if val is None:
            row = (pos - 1) // 3
            col = (pos - 1) % 3
            cells.append((row, col))
    return cells


def _heuristic(board, depth, comp_symbol, human_symbol):
    if _is_line(board, comp_symbol):
        score = depth + 1
    elif _is_line(board, human_symbol):
        score = -(depth + 1)
    else:
        score = 0
    return score


def minimax(board, depth: int, player, comp_symbol, human_symbol):
    if depth == 9:
        row = choice([0, 1, 2])
        col = choice([0, 1, 2])
        return [row, col, 0]

    if player == comp_symbol:
        best = [-1, -1, -inf]
    else:
        best = [-1, -1, inf]

    if depth == 0 or _is_line(board, comp_symbol) or _is_line(board, human_symbol):
        score = _heuristic(board, depth, comp_symbol, human_symbol)
        return [-1, -1, score]

    for row, col in _get_empty_cells(board):
        pos = _row_col_to_pos(row, col)
        previous = board[pos]
        board[pos] = player
        result = minimax(board, depth - 1, next_symbol(player), comp_symbol, human_symbol)
        board[pos] = previous
        result[0], result[1] = row, col

        if player == comp_symbol:
            if result[2] > best[2]:
                best = result
        else:
            if result[2] < best[2]:
                best = result

    return best


def _is_symbol(x):
    return x == CROSS_SYMBOL or x == CIRCLE_SYMBOL


def _is_full(board):
    return 9 == sum([1 for v in board.values() if _is_symbol(v)])


def _is_playable(board):
    return (
        not _is_full(board) and
        not _is_line(board, CIRCLE_SYMBOL) and
        not _is_line(board, CROSS_SYMBOL)
    )


def _row_col_to_pos(row, col):
    index = row * 3 + col
    return index + 1


def bot_turn(boards, comp_symbol, next_board_nr):
    human_symbol = next_symbol(comp_symbol)

    if next_board_nr is not None and _is_playable(boards[next_board_nr]):
        mini_board = boards[next_board_nr]
        board_nr = next_board_nr
    else:
        row, col, _ = minimax(
            board=deepcopy(boards[MAIN_BOARD_NR]),
            depth=len(_get_empty_cells(boards[MAIN_BOARD_NR])),
            player=comp_symbol,
            comp_symbol=comp_symbol,
            human_symbol=human_symbol
        )
        board_nr = _row_col_to_pos(row, col)
        mini_board = boards[board_nr]


    row, col, _ = minimax(
        board=deepcopy(mini_board),
        depth=len(_get_empty_cells(mini_board)),
        player=comp_symbol,
        comp_symbol=comp_symbol,
        human_symbol=human_symbol
    )
    pos = _row_col_to_pos(row, col)

    return board_nr, pos
