import csv
import hotslogs.rawexport.update as dir

eps = 0.000000000000001


def read_main_table(file_name):
    data = {}
    with open(file_name, "r") as file:
        reader = csv.DictReader(file, delimiter=',')
        for i in reader:
            data[i["Hero"]] = [int(i["Picks"]), int(i["Wins"])]
    return data


def conv_main_winrate_table(table):
    if type(table) is dict:
        table = [[i] + table[i] for i in table]
    sum = 0
    for i in table:
        sum += i[1]
        i[2] = float(i[2]) / (i[1] + eps)
    for i in table:
        i[1] = float(i[1]) / sum
    return {i[0]: [i[1], i[2]] for i in table}


def read_matchup_table(file_name):
    data = {}
    with open(file_name, "r") as file:
        reader = csv.DictReader(file, delimiter=",")
        hero_list = sorted([i for i in reader.fieldnames])
        hero_list.remove("Hero")
        for i in reader:
            data[i["Hero"]] = {x: tuple(map(int, i[x].split(":"))) for x in hero_list}
    return data


def conv_matchup_winrate_table(table):
    return {i: {j: [table[i][j][0], table[i][j][1] / (table[i][j][0] + eps)] for j in table[i]} for i in table}
