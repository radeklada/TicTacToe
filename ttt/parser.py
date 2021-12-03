empty = '''
...|...|...*...|...|...*...|...|...
...|...|...*...|...|...*...|...|...
...|...|...*...|...|...*...|...|...
*** *** *** *** *** *** *** *** ***
...|...|...*...|...|...*...|...|...
...|...|...*...|...|...*...|...|...
...|...|...*...|...|...*...|...|...
*** *** *** *** *** *** *** *** ***
...|...|...*...|...|...*...|...|...
...|...|...*...|...|...*...|...|...
...|...|...*...|...|...*...|...|...
'''


MINI_BOARD_SEP = '*'
EMPTY_FIELD = '...'
FIELD_SEP = '|'
MINI_BOARD_SIZE = 9


def _next_symbol(s):
    if s == 'X':
        return 'O'
    return 'X'


def _parse_lines(text):
    lines = []
    for line in text.split():
        lines.append(line.strip())
    return lines


def _parse_field(text):
    if text == EMPTY_FIELD:
        return None
    symbol = text[0]
    order = int(text[1:])
    return text, symbol, order


def _parse_fields(text):
    rows = []
    for line in _parse_lines(text):
        if FIELD_SEP in line:
            row = []
            parts = line.replace(FIELD_SEP, MINI_BOARD_SEP).split(MINI_BOARD_SEP)
            for part in parts:
                row.append(_parse_field(part))
            rows.append(row)
    return rows


def _mini_board_nr(row_index, col_index):
    index = (row_index // 3 * 3 + col_index // 3)
    return index + 1


def _mini_board_pos(row_index, col_index):
    index = (row_index % 3) * 3 + (col_index % 3)
    return index + 1


def _check_order(steps):
    for order, step in enumerate(steps, start=1):
        if order != step['order']:
            raise ValueError('Invalid order in step: {}'.format(step))


def _check_interleave_symbols(steps):
    if not steps:
        return

    symbol = steps[0]['symbol']

    for order, step in enumerate(steps, start=1):
        if symbol != step['symbol']:
            raise ValueError('Invalid symbol in step: {}'.format(step))
        symbol = _next_symbol(symbol)


def parse_steps(scenario, ensure_valid=True):
    steps = []
    for row_index, row in enumerate(_parse_fields(scenario)):
        for col_index, field in enumerate(row):
            if field:
                steps.append({
                    'code': field[0],
                    'symbol': field[1],
                    'order': field[2],
                    'board_nr': _mini_board_nr(row_index, col_index),
                    'position': _mini_board_pos(row_index, col_index)
                })
    steps.sort(key=lambda s: s['order'])
    if ensure_valid:
        _check_order(steps)
        _check_interleave_symbols(steps)
    return steps


if __name__ == '__main__':
    test_scenario = '''
    ...|...|...*...|...|...*...|...|...
    ...|...|...*...|...|...*...|X05|...
    ...|...|...*...|...|...*...|...|...
    *** *** *** *** *** *** *** *** ***
    ...|...|...*...|...|O04*...|...|...
    ...|...|...*...|X01|...*...|...|...
    ...|...|...*O02|...|...*...|...|...
    *** *** *** *** *** *** *** *** ***
    ...|...|...*...|...|...*...|...|...
    ...|X03|...*...|...|...*...|...|...
    ...|...|...*...|...|...*...|...|...
    '''

    assert parse_steps(test_scenario) == [
        {'code': 'X01', 'symbol': 'X', 'order': 1, 'board_nr': 5, 'position': 5},
        {'code': 'O02', 'symbol': 'O', 'order': 2, 'board_nr': 5, 'position': 7},
        {'code': 'X03', 'symbol': 'X', 'order': 3, 'board_nr': 7, 'position': 5},
        {'code': 'O04', 'symbol': 'O', 'order': 4, 'board_nr': 5, 'position': 3},
        {'code': 'X05', 'symbol': 'X', 'order': 5, 'board_nr': 3, 'position': 5}
    ]
