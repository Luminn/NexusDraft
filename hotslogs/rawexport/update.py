from zipfile import ZipFile
import urllib.request

SOURCE = "https://d1i1jxrdh2kvwy.cloudfront.net/Data/HOTSLogs%20Data%20Export%20Current.zip"


def download():
    urllib.request.urlretrieve(SOURCE, "data/hlexport.zip")

def unzip():
    zip_ref = ZipFile("data/hlexport.zip", "r")
    zip_ref.extractall("data/")
    zip_ref.close()
