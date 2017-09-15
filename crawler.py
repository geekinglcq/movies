# -*- coding: utf-8 -*-

import json
import requests
import sys
import time


def get_movies_info_by_year(year):
    url = 'http://www.cbooo.cn/Mdata/getMdata_movie?area=50&type=0&year=%s&initial=%%E5%%85%%A8%%E9%%83%%A8&pIndex='%(year)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    page_count = json.loads(requests.get(url + '1', headers=headers).text)["tPage"]
    movies_info = {}
    for index in range(1, page_count + 1):
        current_info = requests.get(url + str(index), headers=headers).text
        data = json.loads(current_info)["pData"]
        for i in data:
            temp = {}
            temp["Name"] = i["MovieName"]
            temp["EnName"] = i["MovieEnName"]
            temp["Year"] = i["releaseYear"]
            temp["BoxOffice"] = i["BoxOffice"]
            movies_info[i["ID"]] = temp

    return movies_info

def get_douban_related_movie_info(name, year):
    search_url = 'https://api.douban.com/v2/movie/search?q=%s %s'%(name, year)
    respone = requests.get(search_url)
    if respone.ok:
        info = json.loads(respone.text)
        if len(info['subjects']) > 0:
            info = info["subjects"][0]
            return info
        else:
            return None
    else:
        return None
def get_douban_score(name, year):
    try:
        info = get_douban_related_movie_info(name, year)
        score = info.get('rating').get('average')
        return score
    except Exception as e:
        return -1
def extract_info():
    with open('movie_basic_info.json') as f:
        data = json.load(f)
    for i in data.keys():
        print(data[i]['Name'])
        time.sleep(15)
        advanced_info = get_douban_related_movie_info(data[i]["Name"], data[i]["Year"])
        if advanced_info != None:
            data[i].update(advanced_info)
            data[i]["douban"] = 1
        else:
            data[i]["douban"] = 0
    with open('movie_advanced_info.json', 'w') as f:
        json.dump(data, f)
