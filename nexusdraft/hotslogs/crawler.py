import urllib.request
import urllib.parse
import nexusdraft.hotslogs.api as api
from html.parser import HTMLParser


def get_attr(tuple_list, attr):
    for i in tuple_list:
        if i[0] == attr:
            return i[1]
    return None


class HotslogsPersonalPageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.depth = 0
        self.hero_depth = 0
        self.list = []
        self.temp_result = []
        self.expect_item = 0

    def handle_starttag(self, tag, attrs):
        if self.depth > 0:
            self.depth += 1
        if self.hero_depth > 0:
            self.hero_depth += 1
        if get_attr(attrs, 'id') == "heroStatistics":
            self.depth = 1
        if self.depth > 0 and (get_attr(attrs, 'class') == 'rgRow' or get_attr(attrs, 'class') == 'rgAltRow'):
            self.hero_depth = 1
        if self.depth > 1 and tag == "td" and self.temp_result != []:
            self.expect_item = 1

    def handle_endtag(self, tag):
        if self.depth > 0:
            self.depth -= 1
        if self.hero_depth > 0:
            self.hero_depth -= 1
            if tag == "td" and self.expect_item == 1:
                self.temp_result.append("0")
                self.expect_item = 0
            if self.hero_depth == 0 and self.temp_result != 0:
                self.list.append(self.temp_result)
                self.temp_result = []

    def handle_data(self, data):
        if self.hero_depth > 0 and not data.isspace():
            self.temp_result.append(data)
            self.expect_item = 0

    def get_result(self):
        return self.list


def string_table_to_num(table):
    for i in range(len(table)):
        for j in range(len(table[i])):
            if table[i][j][0].isdigit():
                if table[i][j][-1] == "%":
                    table[i][j] = float(table[i][j][:-1].rstrip()) / 100.0
                elif ":" in table[i][j]:
                    continue
                else:
                    table[i][j] = int(table[i][j].replace(",", ""))
    return table


def get_personal_hero_table(tag, num, region=1):
    id = api.get_player_id(tag, num, region)
    page = urllib.request.urlopen("https://www.hotslogs.com/Player/Profile?PlayerID={}".format(id)).read()
    parser = HotslogsPersonalPageParser()
    parser.feed(page.decode('utf-8'))
    table = string_table_to_num(parser.get_result())
    result = {}
    for x in table:
        if len(x) > 4:
            result[x[0]] = (x[2], x[4])
        else:
            result[x[0]] = (x[2], 0.0)
    return result
