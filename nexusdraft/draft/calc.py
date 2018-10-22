import math


def exp_squash(x, max, threshold):
    """Exponentially reduce large numbers to a constant"""
    return max * (1 - 10 ** (- x / threshold))


def real_winrate(winrate):
    """Reduce inflated personal win rate"""
    return exp_squash(winrate - 0.5, 0.15, 0.15) + 0.5


def hero_power(pickrate, winrate, num_heroes):
    """Determine a hero's power level based on global pick rate and win rate"""
    return winrate * winrate * 2 * exp_squash(pickrate, 1, 1 / num_heroes) * 1.5


def combine(wr1, wr2):
    """Combine two close to 50% win rate by multiplying them"""
    return wr1 * wr2 * 2


def counter_score(winrate_1, winrate_2, real_winrate, pickrate, total):
    """Find the level of counter by comparing win rates"""
    return (real_winrate - combine(winrate_1, 1 - winrate_2)) * exp_squash(pickrate, 1, 1 / total)


def duo_score(winrate_1, winrate_2, real_winrate, pickrate, total):
    """ Find the level of synergy by comparing win rates """
    return (real_winrate - combine(winrate_1, winrate_2)) * exp_squash(pickrate, 1, 1 / total)


def map_score(winrate, map_winrate, pickrate, total):
    """Find the power level of a hero on a certain map by comparing win rates """
    return (map_winrate - winrate) * exp_squash(pickrate, 1, 1 / total)


def personal_power(pickrate, winrate):
    """Determine a player's hero proficiency based on his pick rate and win rate """
    return real_winrate(winrate) * exp_squash(pickrate, 1, 0.02)


def personal_experience(pickrate, winrate):
    """Determine a player's hero proficiency based only on pick rate """
    return exp_squash(winrate, 1, 0.4) * exp_squash(pickrate, 0.6, 0.04) * 0.5
