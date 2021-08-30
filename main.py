import requests
import re
import os
import csv
from bs4 import BeautifulSoup
# 准备一个url
import random
import chardet

## 获取所有的省份，并写入csv文件
headers = {'Connection': 'close', }


def getAllProvince():
    list = []
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/index.html'
    html = requests.get(url, headers=headers)
    html = html.text.encode('ISO-8859-1').decode('gb18030', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    data = soup.select('.provincetr td a')

    for item in data:
        provinceResult = {
            'title': item.get_text(),
            'code': item.get('href').replace('.html', ''),
            'linkCode': item.get('href'),
            'level': '1'
        }
        list.append(provinceResult)
    return list


def getCity(linkCode):
    list = []
    cityUrl = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/' + linkCode
    cityHtml = requests.get(cityUrl, headers=headers)
    cityHtml = cityHtml.text.encode('ISO-8859-1').decode('gb18030', 'ignore')
    citySoup = BeautifulSoup(cityHtml, 'lxml')
    cityData = citySoup.select('.citytr td')
    for cityItem in cityData:
        if cityItem.get_text().endswith('0'):
            continue
        cityResult = {
            'title': cityItem.get_text(),
            'code': cityItem.previous_sibling()[0].get_text(),
            'linkCode': cityItem.select('a')[0].get('href'),
            'level': '2'
        }
        list.append(cityResult)
    return list


def getDistrict(linkCode):
    list = []
    cityUrl = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/' + linkCode
    cityHtml = requests.get(cityUrl, headers=headers)
    cityHtml = cityHtml.text.encode('ISO-8859-1').decode('gb18030', 'ignore')
    citySoup = BeautifulSoup(cityHtml, 'lxml')
    cityData = citySoup.select('.countytr td')
    for cityItem in cityData:
        if cityItem.get_text().endswith('0'):
            continue
        cityResult = {
            'title': cityItem.get_text(),
            'code': cityItem.previousSibling.get_text(),
            'level': '3'
        }
        linkCode = ""
        if (len(cityItem.select('a')) > 0):
            linkCode = cityItem.select('a')[0].get('href')
        cityResult["linkCode"] = linkCode
        print(cityResult)
        list.append(cityResult)
    return list


def getTown(linkCode):
    list = []
    cityUrl = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/' + linkCode
    cityHtml = requests.get(cityUrl, headers=headers)
    cityHtml = cityHtml.text.encode('ISO-8859-1').decode('gb18030', 'ignore')
    citySoup = BeautifulSoup(cityHtml, 'lxml')
    cityData = citySoup.select('.towntr td')
    for cityItem in cityData:
        if re.compile(r".*[0-9]$").match(cityItem.get_text()):
            continue
        cityResult = {
            'title': cityItem.get_text(),
            'code': cityItem.previousSibling.get_text(),
            'level': '4'
        }
        linkCode = ""
        if (len(cityItem.select('a')) > 0):
            linkCode = cityItem.select('a')[0].get('href')
        cityResult["linkCode"] = linkCode
        print(cityResult)
        list.append(cityResult)
    return list


def getVillage(linkCode):
    list = []
    cityUrl = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/' + linkCode
    cityHtml = requests.get(cityUrl, headers=headers)
    cityHtml = cityHtml.text.encode('ISO-8859-1').decode('gb18030', 'ignore')
    citySoup = BeautifulSoup(cityHtml, 'lxml')
    cityData = citySoup.select('.villagetr td')
    for cityItem in cityData:
        if re.compile(r".*[0-9]$").match(cityItem.get_text()):
            continue
        cityResult = {
            'title': cityItem.get_text(),
            'code': cityItem.previousSibling.previousSibling.get_text(),
            'linkCode': '',
            'level': '5'
        }
        print(cityResult)
        list.append(cityResult)
    return list


with open("area.csv", mode='w', encoding='utf-8', newline='') as area:
    header = ['title', 'code', 'linkCode', 'level']
    writer = csv.DictWriter(area, fieldnames=header)  # 提前预览列名，当下面代码写入数据时，会将其一一对应。
    writer.writeheader()  # 写入列名
    provinceList = getAllProvince()
    writer.writerows(provinceList)  # 写入数据
    area.close()
for province in provinceList:
    if os.path.exists(province["title"] + ".csv"):
        continue
    with open(province["title"] + ".csv", mode='w', encoding='utf-8', newline='') as provinceArea:
        writer = csv.DictWriter(provinceArea, fieldnames=header)  # 提前预览列名，当下面代码写入数据时，会将其一一对应。
        writer.writeheader()  # 写入列名
        provinceLinkCode = province["linkCode"]
        cityList = getCity(provinceLinkCode)
        writer.writerows(cityList)  # 写入数据
        for city in cityList:
            cityLinkCode = city["linkCode"]
            districtList = getDistrict(cityLinkCode)
            writer.writerows(districtList)  # 写入数据
            for district in districtList:
                districtLinkCode = cityLinkCode.replace(".html", "")[: -4] + district['linkCode']
                if district['linkCode'] != '':
                    townList = getTown(districtLinkCode)
                    writer.writerows(townList)  # 写入数据
                    for town in townList:
                        if town['linkCode'] != '':
                            villageList = getVillage(districtLinkCode.replace(".html", "")[: -6] + town['linkCode'])
                            writer.writerows(villageList)  # 写入数据
        provinceArea.close()
