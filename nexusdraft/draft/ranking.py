import nexusdraft.draft.calc as calc
import nexusdraft.hotslogs.rawexport.countertable as ct
import meta.metascript as metascript

hero_list = {}
main_list = {}
duo_list = {}
counter_list = {}
map_list = {}

meta_script = "default"


def init():
    """Initialize the data needed to compute the hero ranking."""
    global hero_list, main_list, duo_list, counter_list, map_list
    main_list = ct.conv_main_winrate_table(ct.read_main_table("../data/hero.csv"))
    hero_list = sorted([i for i in main_list])
    duo_list = ct.conv_matchup_winrate_table(ct.read_matchup_table("../data/duo.csv"))
    counter_list = ct.conv_matchup_winrate_table(ct.read_matchup_table("../data/counter.csv"))
    map_list = ct.conv_matchup_winrate_table(ct.read_matchup_table("../data/map.csv"))


try:
    init()
except FileNotFoundError:
    pass


def hero_ranking(player_profile=None, map=None, friendly=None, enemy=None, formula="std", scale=(1, 1, 1)):
    """Rank the heroes from most viable to least viable."""
    profile = {i: 0 for i in hero_list}
    if formula == "uni":
        for i in hero_list:
            profile[i] = 0.5
    elif player_profile is None:
        for i in hero_list:
            profile[i] = calc.hero_power(main_list[i][0], main_list[i][1], len(hero_list))
    else:
        if formula == "exp":
            for i in player_profile:
                profile[i] = calc.personal_experience(player_profile[i][0],  player_profile[i][2], player_profile[i][1])
        else:
            for i in player_profile:
                profile[i] = calc.personal_power(player_profile[i][0],  player_profile[i][2], player_profile[i][1])
    if map is not None and map != "":
        for i in hero_list:
            profile[i] += calc.map_score(main_list[i][1], map_list[i][map][0]) * scale[2]

    # compute duo and counter score with friendly and enemy heroes
    for i in hero_list:
        interaction_score = 0
        if friendly is not None:
            for j in friendly:
                if j in hero_list:
                    interaction_score += calc.duo_score(main_list[i][1], main_list[j][1], duo_list[i][j][1]) \
                                          * calc.counter_score_scaler(main_list[j][0]) * scale[0]
        if enemy is not None:
            for j in enemy:
                if j in hero_list:
                    interaction_score += calc.counter_score(main_list[i][1], main_list[j][1], counter_list[i][j][1])\
                                         * calc.counter_score_scaler(main_list[j][0]) * scale[1]
        profile[i] += interaction_score * calc.counter_score_scaler(main_list[i][0]) * 3

    # compute counterability of heroes
    for i in hero_list:
        profile[i] -= counterability(i) * (5 - len(enemy)) * 0.004

    # apply metascript filters
    for i in metascript.accepted_hero_list(meta_script, friendly, hero_list, map):
        profile[i] *= 100

    # delete friendly and enemy heroes from the suggestion list
    if friendly is not None:
        for i in friendly:
            profile.__delitem__(i) if i in profile else None
    if enemy is not None:
        for i in enemy:
            profile.__delitem__(i) if i in profile else None
    return [i[0] for i in sorted([(i, profile[i]) for i in profile], key=lambda x: x[1], reverse=True)]


def counterability(hero):
    """Number of heroes with high counter score"""
    threshold = 0.028 / calc.counter_score_scaler(main_list[hero][0])
    sum = 0
    for i in hero_list:
        cs = calc.counter_score(main_list[i][1], main_list[hero][1], counter_list[i][hero][1]) * calc.counter_score_scaler(main_list[i][0])
        sum += 1 if cs > threshold else 0
    return sum
