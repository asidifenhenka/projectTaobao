# coding=utf8
import pymongo
import requests
import time
from bs4 import BeautifulSoup

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.mydb
chuanbo = db.chuanbo
chuanbo_en = db.chuanbo_en

def get_registrationId():

    ccsnos = chuanbo.find({}, {'_id': 0, 'CCSNO': 1})
    ccsnos_list = []
    for ccsno in ccsnos:
        ccsnos_list.append(ccsno['CCSNO'])
    return ccsnos_list


def get_url(ccsnos_list):
    url_list = []
    link = 'https://csm.ccs.org.cn/busInformation/registrationInDetail?registrationId={}'
    for ccsnos in ccsnos_list:
        url = link.format(ccsnos)
        url_list.append(url)
    return url_list


def get_response(url_list):
    headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    for url in url_list[557:]:
        print(url)
        td_list = []
        th_list = []
        response = requests.get(url,headers=headers)
        if response.status_code == 200 :
            text = response.text
            soup = BeautifulSoup(text, 'lxml')
            tds = soup.find_all("td")
            ths = soup.find_all("th")
            for td in tds:
                td_list.append(td.get_text().strip())
            for th in ths:
                th_list.append(th.get_text().strip())

            data = dict(zip(th_list,td_list))
            data['IMO No'] = data.pop('IMO No.')
            chuanbo_en.insert(data)

        else:
            print(response.status_code)
    print('ok')



















if __name__ == '__main__':
    ccsnos_list = get_registrationId()
    url_list = get_url(ccsnos_list)
    get_response(url_list)