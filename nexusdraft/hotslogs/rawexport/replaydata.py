game_modes = ("", "", "", "Quick Match", "Hero League", "Team League", "Unranked Draft")


def conv_int(string):
    if string == "":
        return 0
    else:
        return int(string)


class ReplayData:

    def __init__(self, hero, is_win):
        self.hero = hero
        self.is_win = bool(int(is_win))
        self.kills = self.deaths = 0
        self.hero_damage = self.siege_damage = self.healing = 0
        self.self_healing = self.damage_taken = self.experience = 0
        self.game_mode = self.map = ""
        self.game_length = 0
        self.date = [0, 0, 0]

    def set_kd_data(self, kills, deaths):
        self.kills = conv_int(kills)
        self.deaths = conv_int(deaths)

    def set_stat_data(self, hero_damage, siege_damage, healing, self_healing, damage_taken, experience):
        self.hero_damage = conv_int(hero_damage)
        self.siege_damage = conv_int(siege_damage)
        self.healing = conv_int(healing)
        self.self_healing = conv_int(self_healing)
        self.damage_taken = conv_int(damage_taken)
        self.experience = conv_int(experience)

    def set_map_data(self, game_mode, map, game_length, date):
        self.game_mode = game_modes[int(game_mode)]
        self.map = map
        self.game_length = int(game_length.split(":")[1])
        #self.date = list(map(lambda x: int(x), game_length.split(" ")[0].split("/")))
