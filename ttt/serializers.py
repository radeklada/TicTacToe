from ttt.ttt import is_mini_board_nr, is_pos


def serialized_moves(moves):
    results = []
    for move in moves:
        results.append({
            'board_nr': move.board_nr,
            'position': move.position,
            'value': move.value
        })
    return results


def _get_board_nr(data):
    value = data.get('boardNr') # todo: !!!
    if not isinstance(value, int) or not is_mini_board_nr(value):
        raise ValueError('invalid board nr')
    return value


def _get_position(data):
    value = data.get('position')
    if not isinstance(value, int) or not is_pos(value):
        raise ValueError('invalid position')
    return value


def deserialized_user_move(data):
    return {
        'board_nr': _get_board_nr(data),
        'position': _get_position(data)
    }