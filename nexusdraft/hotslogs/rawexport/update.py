from zipfile import ZipFile
import urllib.request
import os

SOURCE = "https://d1i1jxrdh2kvwy.cloudfront.net/Data/HOTSLogs%20Data%20Export%20Current.zip"


def download():
    urllib.request.urlretrieve(SOURCE, "data/hlexport.zip")


def unzip():
    zip_ref = ZipFile("data/hlexport.zip", "r")
    zip_ref.extractall("data/")
    zip_ref.close()


def clear():
    os.remove("data/hlexport.zip")
    os.remove("data/ReplayCharacters.csv")
    os.remove("data/Replays.csv")
    os.rename("data/HeroIDAndMapID.csv", "data/hero_map.csv")
