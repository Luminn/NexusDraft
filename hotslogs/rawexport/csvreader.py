import csv
import hotslogs.rawexport.update as dir
from hotslogs.rawexport import replaydata


def read_hero_list(file_name):
    csv_file = open(file_name, 'r', newline="")
    reader = csv.reader(csv_file, delimiter=',')
    result = []
    next(reader)
    next(reader)
    for i in reader:
        if int(i[0]) < 1000:
            result.append([i[0], i[1]])
    return result

def read_hero_role(file_name):
    csv_file = open(file_name, 'r', newline="")
    reader = csv.reader(csv_file, delimiter=',')
    result = []
    next(reader)
    next(reader)
    for i in reader:
        if int(i[0]) < 1000:
            result.append([i[0], i[1], i[3], i[4]])
    return result


def read_map_list(file_name):
    csv_file = open(file_name, 'r', newline="")
    reader = csv.reader(csv_file, delimiter=',')
    result = []
    next(reader)
    for i in reader:
        if int(i[0]) >= 1000:
            result.append([i[0], i[1]])
    return result


def id_to_data(index, names):
    for i in names:
        if i[0] == index:
            return i
    return None


def read_replay_data(file_name, map_list):
    csv_file = open(file_name, 'r', newline="")
    reader = csv.reader(csv_file, delimiter=',')
    next(reader)
    result = []
    for i in reader:
        if i[0].isdigit() and int(i[0]) >= 1000:
            temp = i
            temp[2] = id_to_data(temp[2], map_list)[1]
            result.append(temp)
    return result


def read_data(file_name, hero_list, replay_list, reads):
    csv_file = open(file_name, 'r', newline="")
    reader = csv.reader(csv_file, delimiter=',')
    replay_index = 0
    result = []
    hero_dict = {x[0]: x[1] for x in hero_list}
    for i in reader:
        if i[0].isdigit():
            item = replaydata.ReplayData(hero_dict[i[2]], i[4])
            if i[0] != replay_list[replay_index][0]:
                replay_index += 1
            item.set_kd_data(i[7], i[10])
            item.set_stat_data(i[12], i[13], i[14], i[15], i[16], i[17])
            item.set_map_data(replay_list[replay_index][1], replay_list[replay_index][2], replay_list[replay_index][3],
                              replay_list[replay_index][4])
            result.append(item)
    return result


def read_teams(file_name, hero_list, exit_count=-1):
    csv_file = open(file_name, 'r', newline="")
    reader = csv.reader(csv_file, delimiter=',')
    next(reader)
    replay_index = 0
    teams = []
    temp_team = [], []
    hero_dict = {x[0]: x[1] for x in hero_list}
    for i in reader:
        exit_count -= 1
        hero = hero_dict[i[2]]
        win = int(i[4])
        temp_team[win].append(hero)
        if len(temp_team[0]) > 4 and len(temp_team[1]) > 4:
            teams.append(temp_team)
            temp_team = [], []
            if len(temp_team[0]) > 5 and len(temp_team[1]) > 5:
                raise Exception
        if exit_count == 0:
            break
    csv_file.close()
    return teams

