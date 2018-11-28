
import datetime
import json

CACHE_ROOT = "data/cache/"
DEFAULT_TIME_LIMIT = datetime.timedelta(days=7)


def cache(file_name, data):
    jsdict = {"data": data, "time": datetime.datetime.now().strftime("%b %d %Y %I:%M%p")}
    with open("data/cache/" + file_name, "w`` ") as file:
        json.dump(jsdict, file)


def get_data(file_name, update_timer=DEFAULT_TIME_LIMIT):
    if isinstance(update_timer, int):
        update_timer = datetime.timedelta(days=update_timer)
    try:
        with open("data/cache/" + file_name) as file:
            jsdict = json.load(file)
    except FileNotFoundError:
        return None
    if update_timer < datetime.datetime.now() - datetime.datetime.strptime(jsdict["time"], "%b %d %Y %I:%M%p"):
        return None
    return jsdict["data"]


def get_data_or_save(file_name, alternate_source, update_timer=DEFAULT_TIME_LIMIT):
    data = get_data(file_name, update_timer)
    if data is None:
        data = alternate_source()
        cache(file_name, data)
    return data






