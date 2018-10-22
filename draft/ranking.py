import draft.calc as calc
import hotslogs.rawexport.countertable as ct


hero_list = {}
main_list = {}
duo_list = {}
counter_list = {}
map_list = {}


def init():
    global hero_list, main_list, duo_list, counter_list, map_list
    main_list = ct.conv_main_winrate_table(ct.read_main_table("data/hero.csv"))
    hero_list = sorted([i for i in main_list])
    duo_list = ct.conv_matchup_winrate_table(ct.read_matchup_table("data/duo.csv"))
    counter_list = ct.conv_matchup_winrate_table(ct.read_matchup_table("data/counter.csv"))
    map_list = ct.conv_matchup_winrate_table(ct.read_matchup_table("data/map.csv"))


init()

UNIFORM_PLAYER_PROFILE = {i: [1 / len(hero_list), 0.5] for i in hero_list}


def hero_ranking(player_profile=None, map=None, friendly=None, enemy=None, formula="std", scale=(1, 1, 1)):

    profile = {i: 0 for i in hero_list}
    if formula == "uni":
        for i in hero_list:
            profile[i] = 0.5
    elif player_profile is None:
        for i in hero_list:
            profile[i] = calc.hero_power(main_list[i][0], main_list[i][1], len(hero_list)) / 2
    else:
        if formula == "exp":
            for i in player_profile:
                profile[i] = calc.personal_experience(player_profile[i][0], player_profile[i][1])
        else:
            for i in player_profile:
                profile[i] = calc.personal_power(player_profile[i][0], player_profile[i][1])
    if map is not None and map != "":
        for i in hero_list:
            profile[i] += calc.map_score(main_list[i][1], map_list[i][map][0], map_list[i][map][1],
                                         len(hero_list)) * scale[2]
    if friendly is not None:
        for i in hero_list:
            for j in friendly:
                if j in hero_list:
                    profile[i] += calc.duo_score(main_list[i][1], main_list[j][1], duo_list[i][j][1],
                                                 duo_list[i][j][0], len(hero_list)) * scale[0]
    if enemy is not None:
        for i in hero_list:
            for j in enemy:
                if j in hero_list:
                    profile[i] += calc.counter_score(main_list[i][1], main_list[j][1], counter_list[i][j][1],
                                                     counter_list[i][j][0], len(hero_list)) * scale[1]
    if friendly is not None:
        for i in friendly:
            profile.__delitem__(i) if i in profile else None
    if enemy is not None:
        for i in enemy:
            profile.__delitem__(i) if i in profile else None
    return [i[0] for i in sorted([(i, profile[i]) for i in profile], key=lambda x: x[1], reverse=True)]







