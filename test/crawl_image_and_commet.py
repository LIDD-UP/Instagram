from scrapy import Selector
import requests
import pymysql


def get_image_from_BaoXiaoYiKe():
    response = requests.get()