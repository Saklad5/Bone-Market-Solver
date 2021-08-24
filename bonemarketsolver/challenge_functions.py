# This is a constant used to calculate difficulty checks. You almost certainly do not need to change this.
DIFFICULTY_SCALER = 0.6

def narrow_challenge(difficulty_level: int, stat: int):
    offset = 6 - difficulty_level
    stat += offset

    if stat > 9:
        return 1
    elif stat < 2:
        return .1
    else:
        return stat/10

def broad_challenge(difficulty_level: int, stat: int):
    chance = DIFFICULTY_SCALER*stat//difficulty_level

    return chance

def mean_outcome(success: int, failure: int, chance: float):
    mean_success = success*chance
    mean_failure = failure*(1-chance)
    combined_mean_outcome = mean_success + mean_failure

    return combined_mean_outcome
