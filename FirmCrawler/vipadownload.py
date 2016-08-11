#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import urllib2
import sys
import time

import pymongo
import hashlib


reload(sys)
sys.setdefaultencoding('utf-8')
from mycrawler.settings import firmlist_fc, MONGO_URI,dirs_root,MONGO_DATABASE,MONGO_COLLECTION,file_size


import multiprocessing
file_size = int(file_size)



conn = pymongo.MongoClient(MONGO_URI)
print "################"
db = conn.get_database(MONGO_DATABASE)  # 使用数据库名为firmware
#print type(db)
#print type(MONGO_DATABASE)
#collection = db.scrapy_items  # 使用集合scrapy_items
collection = db.get_collection(MONGO_COLLECTION)
#collectionB = db.firmware_info  # 使用集合firmware_innfo

#dirs_root = "/home/byfeelus/firmware/Druid/"
#file_size = 104857600  # 默认文件大小是100m
# 加header，模拟浏览器
header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}





def has_keys(_dict, _iter):
    _l = []
    for x in _iter:
        _l.append(_dict.has_key(x))
    return all(_l)


def download_url(cur):
    if not has_keys(cur, ['URL', 'Manufacturer', 'FirmwareName']):
        collection.update(
            {"_id": cur['_id']}, {"$set": {'Status': 3}})

        print "no Link or Firm or Filename"
        return

    name = cur['FirmwareName']  # 把文件名赋值给name
    mylink = cur['URL']  # 把link赋值给mylink
    firm = cur['Manufacturer']  # 把firm赋值给firmname
    #fileclass = cur["ProductClass"]

    dirs1 = os.path.join(dirs_root, firm)  # 在FIRMWARE下根据厂商名建立新文件夹
    if not os.path.exists(dirs1):
        os.makedirs(dirs1)

    #dirs = os.path.join(dirs1,fileclass)
    #if not os.path.exists(dirs):
     #   os.makedirs(dirs)

    m = hashlib.md5()
    m.update(mylink)
    a = m.hexdigest()
    #b =  a[0] +a[1] +a[2]

    name1 = a + name
    filename = os.path.join(dirs1, name1)   # 定义文件的绝对路径

    # 判断文件是否已经存在，若不存在，继续下载，若存在，输出路径不下载
    if cur.has_key("Path") and cur["Path"] == filename:

        if os.path.exists(filename) and os.path.getsize(filename) > 1:
            print filename, '已经存在'  # 已经下载过的文件，修改status值

            collection.update({'_id': cur["_id"]}, {"$set": {'Status': 0}})
            return

    print "download", mylink
    trytime = 3
    z=0
    while trytime > 0:
        try:
            res = urllib2.urlopen(urllib2.Request(
                mylink, None, header), timeout=45)  # 15

            try:
                fsize = res.headers["content-length"]
                print fsize
                print "#################################"
                fsize = int(fsize)
                if fsize < file_size:
                    with open(filename, 'wb') as f:
                        print "开始将数据写到文件中"
                        cc = res.read()
                        print "写ｃｃ"
                        f.write(cc)
                        print "关文件"
                        f.close()
                        print"数据已经被写进文件中"

                        model = '%Y-%m-%d %X'
                        #date = time.strftime(model,time.localtime())
                        print" 已经走到这一步了"

                        collection.update({'_id': cur['_id']}, {
                            "$set": {
                                'Path': filename,
                                'Status': 0,
                                'Firmtype': 'FactoryControl' if firm in firmlist_fc else 'Not_FactoryControl',
                                'Size': os.path.getsize(filename),  # 　取大小
                                'Down_date': time.strftime(model, time.localtime())}})  # 取时间
                        print"第一次修改成功"
                        '''
                        collectionB.update({'Par_path': filename}, {
                            "$set": {
                                "Filename": cur.get("Filename"),

                                "Model": cur.get("Info").get("Model"),
                                # "Series": cur.get("Info").get("Series"),
                                "Version": cur.get("Info").get("Version"),
                                "Published": cur.get("Published"),
                                "Firm": cur.get("Firm"),
                                "Status": 1, "Flag": 0,
                                "Size":fsize,
                                "Descr": cur.get("Descr")}}, True)
                        print "插入新数据库成功"
                        '''
                        # "Firmname":cur["Filename"]}})
                        # "Class": cur.get("Info").get("Class"),
                        # 'Firmtype': 'FactoryControl' if firm in firmlist_fc else 'Not_FactoryControl'}}, True)

                        #print "插入完成"
                    break
                else:
                    print "size  over"
                    collection.update({'_id': cur['_id']}, {
                        "$set": {

                            'Status': 4,
                            }})
            except Exception,e:
                if trytime == 0:
                    collection.update({'_id': cur['_id']}, {
                        "$set": {

                            'Status': 3,
                        }})
                else:
                    pass

                print e
        except Exception, e:
            print e
            trytime -= 1
    else:
        print "status3"
        collection.update(
            {"_id": cur['_id']}, {"$set": {'Status': 3}})
        return

    print "download over........."


def download1():
    while 1:
        try:
                if collection.find({'Status': 1,'Manufacturer':"Vipa"}).count() > 0:
                    print "下载状态值为１的"
                    r_d = list(collection.find(
                        {'Status': 1,'Manufacturer':"Vipa"}))[:7]
                    if len(r_d) < 7:
                        download_url(r_d[-1])
                    else:
                        for r in r_d[:5]:
                            #print '数量不足七个'

                            multiprocessing.Process(
                                target=download_url, args=(r,)).start()
                        download_url(r_d[-1])
                        download_url(r_d[-2])
                else:
                    return
        except Exception, e:
            print e


def remove():
    collection.remove({"Status":4})
'''
def check():
    print "start check status = 0"
    cs = list(collection.find({'Status': 0}))
    for x in cs:
        aa=x["Path"]
        if os.path.exists(aa) and os.path.getsize(aa)>0:
            print  "normal"

        else:
            print "not exist file or size =0"
            collection.update({'_id': x["_id"]}, {"$set": {'Status': 2}})

    cs = list(collection.find({'Status':3}))
    for x in cs:

        collection.update({'_id': x["_id"]}, {"$set": {'Status': 2}})


    print "check end"
'''



# time.sleep(300)
#check()
download1()
remove()

'''
def download2():
    print "start"
    cs = list(collection.find({'Status': 1, 'Firm': "Rockwell"}))
    for x in cs[:7]:
        print "waiting......"
        download_url(x)
    print "end"

# download2()


def download3():
    cs = list(collection.find({'Status': 1}))
    for cur in cs[:30]:
        collectionB.upsert({'Firmname':"filename"},{
                    "$set": {
                        'par_path': cur["Path"],
                        "Size": cur.get("Info").get("Size"),
                        "Model": cur.get("Info").get("Model"),
                       # "Series": cur.get("Info").get("Series"),
                        "Version": cur.get("Info").get("Version"),
                        "Published": cur.get("Info").get("Published"),
                        "Firm":cur["Firm"],
                        "Firmname":cur["Filename"]}})
                       # "Class": cur.get("Info").get("Class"),
                       # 'Firmtype': 'FactoryControl' if firm in firmlist_fc else 'Not_FactoryControl'}}, True)


# download3()
# for x in collection.find():
#     collection.update({'Status': 1, "Firm": "Tplink"},
#                       {"$set": {'Status': 0}}, False, True)
# download_url('http://support1.toshiba-tro.de/tedd-files2/0/frmwre-20071005144441.zip')
# collection.remove()

# _path = "./media/ubuntu/Elements/test/Tplink/"

# for x in collection.find({'Status': 0, "Firm": "Tplink"}):
    # for dirpath, dirnames, filenames in os.walk(_path):
        # for filename in filenames:
        # filepath = os.path.join(dirpath, filename)
        # filename = os.path.join(_path, x.get("Filename"))
        # collection.update({"Firm": "Tplink"}, {"$set": {'Path': filepath}})


import random


def random_pick(some_list, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability:
            break
    return item

# some_list = ["squashfs", "yaffs2", ""]
# probabilities = [0.6, 0.1, 0.3]
# print random_pick(some_list, probabilities)

# firmware_info = db.firmware_info
# for x in firmware_info.find():
#     firmware_info.update({'_id': x.get("_id")},
#                          {"$set": {
#                           "Filesys": random_pick(some_list, probabilities),
#                           "compression": random_pick(["lzam", "zip", "gzip", "xz"], [0.4, 0.3, 0.2, 0.1])

#                           }})
'''
