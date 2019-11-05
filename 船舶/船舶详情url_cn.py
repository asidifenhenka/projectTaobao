# coding=utf8
import pymongo
import requests
import time
from bs4 import BeautifulSoup

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.mydb
chuanbojl_cn = db.chuanbojl_cn
chuanbo_cn = db.chuanbo_cn

def get_registrationId():

    cjdjh = chuanbojl_cn.find({}, {'_id': 0, 'CJDJH': 1})
    cjdjh_list = []
    for cjdjh in cjdjh:
        cjdjh_list.append(cjdjh['CJDJH'])
    return cjdjh_list


def get_url(cjdjh_list):
    url_list = []
    link = 'https://csm.ccs.org.cn/busInformation/registrationDetail?registrationId={}'
    for cjdjh in cjdjh_list:
        url = link.format(cjdjh)
        url_list.append(url)
    return url_list


def get_response(url_list):
    headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    for url in url_list:
        td_list = []
        th_list = []
        print(url)
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            text = response.text
            soup = BeautifulSoup(text, 'lxml')
            tds = soup.find_all("td")
            ths = soup.find_all("th")
            print(ths)
            for td in tds:
                td_list.append(td.get_text().strip())
            for th in ths:
                th_list.append(th.get_text().strip())
            data = dict(zip(th_list,td_list))
            data['IMO No'] = data.pop('IMO NO.')
            data['CCS NO'] = data.pop('CCS NO.')

            chuanbo_cn.insert(data)
        else:
            print(response.status_code)
    print('ok')






if __name__ == '__main__':
    cjdjh_list = get_registrationId()
    url_list = get_url(cjdjh_list)
    get_response(url_list)