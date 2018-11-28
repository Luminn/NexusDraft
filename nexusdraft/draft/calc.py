import math


def exp_squash(x, max, threshold):
    """Exponentially reduce large numbers to a constant"""
    return max * (1 - 10 ** (- math.fabs(x) / threshold)) * (-1 if x < 0 else 1)


def scale_winrate(winrate, scale):
    """Reduce inflated personal win rate"""
    result = (winrate - 0.5) * scale + 0.5
    return result if 1 >= result >= 0 else 0 if result < 0 else 1


def hero_power(pickrate, winrate, num_heroes):
    """Determine a hero's power level based on global pick rate and win rate"""
    return combine(winrate, pickrate * 2 + 0.45)

def combine(wr1, wr2):
    """Combine two close to 50% win rate by multiplying them"""
    return wr1 * wr2 * 2


def counter_score(winrate_1, winrate_2, real_winrate, scaler=1):
    """Find the level of counter by comparing win rates"""
    try:
        score = real_winrate / combine(winrate_1, 1 - winrate_2)
        return (score - 1) * scaler + 1
    except ZeroDivisionError:
        return 0


def legacy_counter_score(winrate_1, winrate_2, real_winrate):
    """Find the level of counter by comparing win rates"""
    return real_winrate - combine(winrate_1, 1 - winrate_2)


def duo_score(winrate_1, winrate_2, real_winrate, scaler=1):
    """ Find the level of synergy by comparing win rates """
    try:
        score = real_winrate / combine(winrate_1, winrate_2)
        return (score - 1) * scaler + 1
    except ZeroDivisionError:
        return 0


def map_score(winrate, map_winrate):
    """Find the power level of a hero on a certain map by comparing win rates """
    try:
        return map_winrate / winrate
    except ZeroDivisionError:
        return 0


def personal_power(picks, pickrate, winrate):
    """Determine a player's hero proficiency based on his pick rate and win rate """
    pow = scale_winrate(winrate, 1.1) * max(exp_squash(picks, 1, 40), exp_squash(pickrate, 1, 0.04))
    if pow < 0.55:
        pow += (0.55 - pow) * exp_squash(picks, 1, 100)
    return pow


def personal_experience(picks, pickrate):
    """Determine a player's hero proficiency based only on pick rate """
    return max(exp_squash(picks, 0.5, 50), exp_squash(pickrate, 0.5, 0.05))


def counter_score_scaler(pickrate):
    """Attempt to make counter score more evenly distributed"""
    return 1 / ((1 / (pickrate + 0.00001) / 200 + 1.5) / 2)