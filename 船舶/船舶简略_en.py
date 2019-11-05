#coding=utf8
import json
import requests
import pymongo
import time

client = pymongo.MongoClient(host='localhost',port=27017)
db = client.mydb
chuanbo = db.chuanbo



headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

data = {'ccsno': '',
        'imono': '',
        'flag': '',
        'shipType': '',
        'shipname': '',
        'grossBegin': '',
        'grossEnd': '',
        'owner': '',
        'operator': '',
        'rows': '100',
        'page': '1',
        'sortOrder': 'asc'
        }


url = 'https://csm.ccs.org.cn/busInformation/findInternationalShipsPage'
for i in range(41,43):
    data['page'] = str(i)
    response = requests.post(url, headers=headers, data=data)
    time.sleep(0.5)

    text = response.text
    rows_jsons = json.loads(text)

    for rows_json in rows_jsons['rows']:
        chuanbo.insert(rows_json)
    print(i)

print('ok')
