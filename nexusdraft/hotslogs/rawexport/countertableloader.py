import csv
from nexusdraft.hotslogs.rawexport import csvreader


class CounterTableGenerator:

    def __init__(self):
        pass

    def _init(self):
        self.hero_list = csvreader.read_hero_list("../data/HeroIDAndMapID.csv")
        self.hero_dict = {i[0]: i[1] for i in self.hero_list}
        self.hero_list = list(sorted(map(lambda x: x[1], self.hero_list)))
        self.map_list = csvreader.read_map_list("../data/HeroIDAndMapID.csv")
        self.map_dict = {i[0]: i[1] for i in self.map_list}
        self.map_list = list(sorted(map(lambda x: x[1], self.map_list)))
        self.winrate_list = {i: [0, 0] for i in self.hero_list}
        self.map_picks = {i: {j: [0, 0] for j in self.map_list} for i in self.hero_list}
        self.counter_picks = {i: {j: [0, 0] for j in self.hero_list} for i in self.hero_list}
        self.duo_picks = {i: {j: [0, 0] for j in self.hero_list} for i in self.hero_list}

    def clear_counter_lists(self):
        winrate_list = {i: [0, 0] for i in self.hero_list}
        map_picks = {i: {j: [0, 0] for j in self.map_list} for i in self.hero_list}
        counter_picks = {i: {j: [0, 0] for j in self.hero_list} for i in self.hero_list}

    def generate_counter_lists(self, gamemode_filter=(4, 5, 6), mmr_floor=0, mmr_ceiling=0):
        self._init()
        chara_csv_file = open("../data/ReplayCharacters.csv", "r")
        replay_csv_file = open("../data/Replays.csv", "r")
        chara_reader = csv.reader(chara_csv_file, delimiter=",")
        replay_reader = csv.reader(replay_csv_file, delimiter=",")
        next(chara_reader, None)
        next(replay_reader, None)

        counter = 0
        heroes_temp = []
        for row in chara_reader:
            heroes_temp.append([self.hero_dict[row[2]], int(row[4])])
            counter += 1
            if counter == 10:
                game = next(replay_reader, None)
                if int(game[1]) in gamemode_filter:
                    for h1 in heroes_temp:
                        self.winrate_list[h1[0]][0] += 1
                        self.winrate_list[h1[0]][1] += h1[1]
                        self.map_picks[h1[0]][self.map_dict[game[2]]][0] += 1
                        self.map_picks[h1[0]][self.map_dict[game[2]]][1] += h1[1]
                        for h2 in heroes_temp:
                            if h1 != h2:
                                if h1[1] == h2[1]:
                                    self.duo_picks[h1[0]][h2[0]][0] += 1
                                    self.duo_picks[h1[0]][h2[0]][1] += h1[1]
                                else:
                                    self.counter_picks[h1[0]][h2[0]][0] += 1
                                    self.counter_picks[h1[0]][h2[0]][1] += h1[1]
                counter = 0
                heroes_temp = []
        chara_csv_file.close()
        replay_csv_file.close()

    def get_active_map_list(self):
        maps = []
        picks = self.map_picks.__iter__()
        h1 = self.map_picks[next(picks)]
        h2 = self.map_picks[next(picks)]
        for map in self.map_list:
            if h1[map][0] != 0 or h2[map][0] != 0:
                maps.append(map)
        return maps

    def export_counter_score(self):
        wrlist = [self.winrate_list[x] for x in self.hero_list]
        maplist = [[self.map_picks[i][j] for j in self.get_active_map_list()] for i in self.hero_list]
        duolist = [[self.duo_picks[i][j] for j in self.hero_list] for i in self.hero_list]
        counterlist = [[self.counter_picks[i][j] for j in self.hero_list] for i in self.hero_list]

        hero_header = ["Hero"] + self.hero_list
        map_header = ["Hero"] + self.get_active_map_list()
        winrate_header = ["Hero", "Picks", "Wins"]

        colon_format = lambda x: "{}:{}".format(x[0], x[1])

        with open("../data/hero.csv", "w") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerow(winrate_header)
            for i in range(len(self.hero_list)):
                writer.writerow([self.hero_list[i]] + wrlist[i])

        with open("../data/map.csv", "w") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerow(map_header)
            for i in range(len(self.hero_list)):
                writer.writerow([self.hero_list[i]] + [colon_format(x) for x in maplist[i]])

        with open("../data/duo.csv", "w") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerow(hero_header)
            for i in range(len(self.hero_list)):
                writer.writerow([self.hero_list[i]] + [colon_format(x) for x in duolist[i]])

        with open("../data/counter.csv", "w") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerow(hero_header)
            for i in range(len(self.hero_list)):
                writer.writerow([self.hero_list[i]] + [colon_format(x) for x in counterlist[i]])


