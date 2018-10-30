import urllib.request
import json


def get_full_hero_list():
    hero_list_response = urllib.request.urlopen("https://api.hotslogs.com/Public/Data/Heroes")
    return json.loads(hero_list_response.read())


def get_hero_list():
    hero_list = get_full_hero_list()
    result = []
    for i in hero_list:
        result.append(i["PrimaryName"])
    return result


def get_full_map_list():
    hero_list_response = urllib.request.urlopen("https://api.hotslogs.com/Public/Data/Maps")
    return json.loads(hero_list_response.read())


def get_map_list():
    hero_list = get_full_map_list()
    result = []
    for i in hero_list:
        result.append(i["PrimaryName"])
    return result


def get_player_id(tag, number, region=1):
    response = urllib.request.urlopen("https://api.hotslogs.com/Public/Players/{}/{}_{}".format(region, tag, number))
    return json.loads(response.read())["PlayerID"]
