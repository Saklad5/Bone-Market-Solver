def narrow_challenge(difficulty_level: int, stat: int):
    offset = 6 - difficulty_level
    stat += offset

    if stat > 9:
        return 1
    elif stat < 2:
        return .1
    else:
        return stat/10

def mean_outcome(success: int, failure: int, chance: float):
    mean_success = success*chance
    mean_failure = failure*(1-chance)
    combined_mean_outcome = mean_success + mean_failure

    return combined_mean_outcome
