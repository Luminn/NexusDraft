import math

""" Use an exponential function to make small numbers more relevant """
def exp_squash(x, max, threshold):
    return max * (1 - 10 ** (- x / threshold))


""" reduce inflated personal win rate """
def real_winrate(winrate):
    return exp_squash(winrate - 0.5, 0.15, 0.15) + 0.5


""" Determine a hero's power level based on global pick rate and win rate """
def hero_power(pickrate, winrate, num_heroes):
    return winrate * winrate * 2 * exp_squash(pickrate, 1, 1 / num_heroes) * 1.5


""" Combine two close to 50% win rate by multiplying them """
def combine(wr1, wr2):
    return wr1 * wr2 * 2


""" Find the level of counter by comparing win rates """
def counter_score(winrate_1, winrate_2, real_winrate, pickrate, total):
    return (real_winrate - combine(winrate_1, 1 - winrate_2)) * exp_squash(pickrate, 1, 1 / total)


""" Find the level of synergy by comparing win rates """
def duo_score(winrate_1, winrate_2, real_winrate, pickrate, total):
    return (real_winrate - combine(winrate_1, winrate_2)) * exp_squash(pickrate, 1, 1 / total)


""" Find the power level of a hero on a certain map by comparing win rates """
def map_score(winrate, map_winrate, pickrate, total):
    return (map_winrate - winrate) * exp_squash(pickrate, 1, 1 / total)


""" Determine a player's hero proficiency based on his pick rate and win rate """
def personal_power(pickrate, winrate):
    return real_winrate(winrate) * exp_squash(pickrate, 1, 0.02)


""" Determine a player's hero proficiency based only on pick rate """
def personal_experience(pickrate, winrate):
    return exp_squash(winrate, 1, 0.4) * exp_squash(pickrate, 0.6, 0.04) * 0.5
