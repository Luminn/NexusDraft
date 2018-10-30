import json
import nexusdraft.meta.metascript as metascript
import os


def get_meta_list():
    files = os.listdir("data/meta/")
    result = []
    for i in files:
        if i.endswith(".meta"):
            result.append(i.split("/")[-1][:-5])
    return result


def load_meta_files(meta_name):
    with open("data/meta/" + meta_name + ".role", "r") as file:
        role_file = json.load(file)
    with open("data/meta/" + meta_name + ".meta", "r") as file:
        meta_file = metascript.read_meta_script(file.read())
    return role_file, meta_file


def create_empty_meta_file(meta_name, hero_list):
    with open("data/meta/" + meta_name + ".meta", "w"):
        pass


def create_empty_role_file(meta_name, hero_list):
    with open("data/meta/" + meta_name + ".role", "w") as file:
        file.write(role_file_template(hero_list))

def role_file_template(hero_list):
    result = ["{\n"]
    for i in hero_list:
        result.append('    "{}":[""],\n'.format(i))
    result[-1] = result[-1][:-2] + "\n"
    result.append("}\n")
    return "".join(result)

import hotslogs.api
create_empty_role_file("banned", hotslogs.api.get_hero_list())