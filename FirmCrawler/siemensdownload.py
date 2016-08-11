#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import urllib2
import sys
import time
import pymongo
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import logging
import multiprocessing
import codecs
import hashlib
reload(sys)
sys.setdefaultencoding('utf-8')
from mycrawler.settings import firmlist_fc, MONGO_URI,MONGO_COLLECTION,MONGO_DATABASE,file_size,dirs_root
#from __future__ import with_statement

import ConfigParser
config = ConfigParser.ConfigParser()
configfile = r'./CONFIG.cfg'
globalconfigfile = r'../GLOBAL_CONFIG'
config.readfp(codecs.open(configfile, "r", "utf-8"))
config.readfp(codecs.open(globalconfigfile, "r", "utf-8"))

user = config.get('info',"SIEMENS_DOWNLOAD_ACCOUNT")
pwd = config.get('info',"SIEMENS_DOWNLOAD_PASSWORD")



#user = "sungong"
#pwd = "SUNgong123"

def login_url(timeout):
    #timeout=10
    driver=webdriver.Firefox()
    driver.get("https://support.industry.siemens.com/cs/signin?lc=zh-CN")
    time.sleep(3)

    print "******begin******"

    loginFrame=WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID,"frmLogin")))
    driver.switch_to_frame(loginFrame)


    username=WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID,"ContentPlaceHolder1_TextSiemensLogin")))
    username.send_keys(user)

    driver.find_element_by_id("ContentPlaceHolder1_TextPassword").send_keys(pwd)
    driver.find_element_by_id("ContentPlaceHolder1_LoginRememberUserNamePassword").click()
    driver.find_element_by_id("ContentPlaceHolder1_LoginUserNamePasswordButton").click()

    time.sleep(30)
    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    driver.close()
    cookiestr = ';'.join(item for item in cookie)
    return cookiestr




conn = pymongo.MongoClient(MONGO_URI)
db = conn.get_database(MONGO_DATABASE)  # 使用数据库名为firmware
collection = db.get_collection(MONGO_COLLECTION)  # 使用集合scrapy_items
#collectionB = db.firmware_info  # 使用集合firmware_innfo

#dirs_root = "/home/byfeelus/firmware/Druid/"
#file_size = 104857600  # 默认文件大小是100m

firm = "Siemens"
dir1 = os.path.join(dirs_root,firm)




if not os.path.exists(dir1):

    os.makedirs(dir1)


print "###################"


i = 60

if collection.find({"Manufacturer":"Siemens","Status":1}).count()>0:
    curs = collection.find({"Manufacturer":"Siemens","Status":1}).batch_size(10)
    for cur in curs:
        print "$$$$$$$$$$$$$$$$$$"
        print i
        print "$$$$$$$$$$$$$$$$$"
        if i%60 ==0:
            login_url(30)
            cookiestr = login_url(30)
            headers1 = {'cookie':cookiestr}
            print headers1


        link = cur["URL"]
        m = hashlib.md5()
        m.update(link)
        a = m.hexdigest()


        req = urllib2.Request(link,headers = headers1)
        req.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0')
        print req.get_header('User-agent')
        print req.headers

        print link

        print " try "
        name = cur["FirmwareName"]

        name1 = a + name
        filename = os.path.join(dir1, name1)  # 定义文件的绝对路径

        print filename

        if cur.has_key("Path") and cur["Path"] == filename:

            if os.path.exists(filename) and os.path.getsize(filename) > 1:

                print filename, '已经存在'  # 已经下载过的文件，修改status值

                collection.update({'_id': cur["_id"]}, {"$set": {'Status': 0}})
                continue

        trytime =3
        if trytime > 0:

            try:

                response = urllib2.urlopen(req)
                fsize = response.headers["Content-Length"]
                print fsize
                print "#################################"
                fsize = int(fsize)
                if fsize < 100000000:
                    text = response.read()
                    print"yaokaishixie"



                    with open(filename, 'wb') as f:
                        print "开始将数据写到文件中"
                        f.write(text)
                        f.close()
                        print"数据已经被写进文件中"
                        collection.update({'_id': cur['_id']}, {
                                "$set": {
                                    'Path': filename,
                                    'Status': 0,
                                    'Firmtype': "",
                                    'Size': os.path.getsize(filename),  # 　取大小
                                    'Down_date': "" }}) # 取时间
                        print '第一次修改成功'
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
                        i +=1
                        trytime = 0

                            # "Firmname":cur["Filename"]}})
                            # "Class": cur.get("Info").get("Class"),
                            # 'Firmtype': 'FactoryControl' if firm in firmlist_fc else 'Not_FactoryControl'}}, True)
                else:
                    collection.remove({"_id":cur["_id"]})
                    print "remove over size"
                    i +=1
                    trytime = 0

            except Exception,e:
                print e
                print "meiyou"
                i +=1
                trytime -=1
        else:
            collection.update({'_id': cur['_id']}, {
                                "$set": {'Status': 3, }}) # 取时间
            print 'error'

print "over!!!"



