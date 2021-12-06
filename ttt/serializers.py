def serialized_moves(moves):
    results = []
    for move in moves:
        results.append({
            'board_nr': move.board_nr,
            'position': move.position,
            'value': move.value
        })
    return results
