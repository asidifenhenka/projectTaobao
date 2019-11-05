import pandas as pd
import pymongo
client = pymongo.MongoClient('127.0.0.1', 27017)
db = client.mydb
chuanbo = db.chuanbojl_cn
df1 = pd.DataFrame(list(chuanbo.find()))
df1.to_csv('data_cn.csv')
