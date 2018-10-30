import json
import re


def read_role_script(name):
    with open("data/meta/{}.role".format(name), "r") as file:
        hero_roles = json.load(file)
    roles = set()
    for i in hero_roles:
        for j in hero_roles[i]:
            roles.add(j)
    role_list = {i: [] for i in roles}
    for i in hero_roles:
        for j in hero_roles[i]:
            role_list[j].append(i)
    return role_list


def read_meta_script(name):
    with open("data/meta/{}.meta".format(name), "r") as file:
        script = file.read()
    role_list = {}
    lines = script.split("\n")
    result = []
    maps = None
    try:
        for i in lines:
            if i == "" or i.isspace():
                continue
            if i.startswith("import "):
                import_meta = i[6:].strip()
                role_list.update(read_role_script(import_meta))
                continue
            elif i.startswith("define "):
                commands = list(map(lambda x: x.strip(), re.split(r"[=+\-]", i[6:])))
                operators = ['+'] + re.findall(r"[+\-]", i[6:])
                temp_list = set()
                for j in range(len(operators)):
                    if operators[j] == "+":
                        temp_list.update(role_list[commands[j + 1]])
                    if operators[j] == "-":
                        for k in role_list[commands[j + 1]]:
                            if k in temp_list:
                                temp_list.remove(k)
                role_list[commands[0]] = temp_list
                continue
            elif i.startswith("map "):
                maps = list(map(lambda x: x.strip(), i[3:].split(",")))
                if i[3:].lstrip().startswith("not"):
                    maps = ["NOT"] + maps
                continue
            elif not i.startswith("  "):
                maps = None
            i = i.strip()
            if i.endswith("*"):
                enforce = len(i) - len(i.rstrip("*"))
                i = i.rstrip("*")
            else:
                enforce = None
            if i.find("=") > 0:
                k = i.find("=")
                sign = 0
            elif i.find(">") > 0:
                k = i.find(">")
                sign = 1
            elif i.find("<") > 0:
                k = i.find("<")
                sign = -1
            else:
                raise ValueError("No comparison found.")
            role = i[0:k].strip()
            value = int(i[k+1:].strip())
            result.append((role, sign, value, maps, enforce))
    #except ValueError:
    #    return None
    #except IndexError:
    #    return None
    except ArithmeticError:
        return None
    return role_list, result


def accepted_hero_list(name, picks, hero_list, map=None):
    roles, script = read_meta_script(name)
    result = []
    for i in hero_list:
        accepted = True
        for role, sign, value, maps, _ in script:
            if map is not None:
                if maps[0] == "NOT" and map in maps:
                    pass
                elif map not in maps:
                    pass
            count = 1 if i in roles[role] else 0
            for j in picks:
                if j in roles[role]:
                    count += 1
            if sign > 0:
                if 4 - len(picks) < value - count:
                    accepted = False
                    break
            elif sign < 0:
                if count >= value:
                    accepted = False
                    break
            else:
                if 4 - len(picks) < value - count or count > value:
                    accepted = False
                    break
        if accepted:
            result.append(i)
    return result









