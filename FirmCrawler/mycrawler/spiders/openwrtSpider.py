# -*- coding: UTF-8 -*-

from sets import Set

from scrapy.spiders import Spider
import scrapy

import mycrawler.items as MI
import re
import time

class OpenwrtSpider(Spider):
    name = "openwrt"
    timeout = 8
    trytimes = 3
    start_urls = [
        "http://downloads.openwrt.org.cn/OpenWrt-DreamBox/",
        "http://downloads.openwrt.org.cn/PandoraBox/",
        "http://downloads.openwrt.org.cn/openwrtcn_img/",
        "http://downloads.openwrt.org.cn/ar_series_img/",
        "http://downloads.openwrt.org.cn/zjhzzyf_img/",
    ]

    # must be lower character
    suffix = ["bin", "bix", "trx", "img", "dlf", "tfp", "rar", "zip"]
    allsuffix = Set()

    def parse(self, response):
        request = scrapy.Request(response.url, callback=self.parse_page)
        request.meta["prototype"] = MI.BasicItem()
        #request.meta["prototype"]["Info"] = {}
        request.meta["prototype"]["Manufacturer"] = "Openwrt"
        yield request

    def parse_page(self, response):
        r = response.selector.xpath(
            "//pre").re("<a[ ]*href=\"(.*)\".*>.*</a>[ ]*(.*:.*)\r\n")  # [0-9]{2}

        i = 0
        prototype = response.meta['prototype']
        #prototype["Title"] = response.selector.xpath(
         #   "//h1/text()").extract().pop()
        while i < len(r):
            if r[i][-1] == "/":
                request = scrapy.Request(
                    response.url + r[i], callback=self.parse_page)
                request.meta["prototype"] = response.meta["prototype"]
                yield request
            elif r[i].rsplit(".").pop().lower() in OpenwrtSpider.suffix:
                item = MI.BasicItem(prototype)
                item["FirmwareName"] = r[i]
                #reg = r'((20)\d{2})\d{2}\d{2}'
                #item["Info"]["Published"] = re.match('((20)\d{2})\d{2}\d{2}',item["Filename"]).group()
                item["URL"] = response.url + r[i]
                #item["Rawlink"] = item["Link"]



                ######################　名字中提取######################
                name4 = item["FirmwareName"]
                if name4.split("-")[0]== "110829":
                    try:
                    	date1 = name4.split("-")[4]
                    	date2 = name4.split("-")[5]

                    	date = date1+ "-" +date2
                    except:
                        date = name4.split("-")[4]

                elif name4.split("-")[0] == "openwrt" and name4.split("-")[1] == "ar71xx":
                    try:
                     
                    	date1=name4.split("-")[3]
                    	date2 = name4.split("-")[4]
                    	date = date1 + "-" + date2
                    except:
                        date = name4.split("-")[1]

                elif name4.split("-")[0] == "openwrt" and name4.split("-")[1] != "ar71xx" and name4.split("-")[1] != "ramips":
                    date = name4.split("-")[1]

                elif name4.split("-")[0] == "openwrt" and name4.split("-")[1] == "ramips":
                    if len(name4.split("-")) > 5:

                        date1=name4.split("-")[2]
                        date2 = name4.split("-")[3]
                        date3 = name4.split("-")[4]
                        date = date1 + "-" + date2 + "-" +date3
                    else:
                         date = name4.split("-")[2]

                elif name4.split("-")[0] == "PandoraBox" :
                    date1=name4.split("-")[1]
                    date2 = name4.split("-")[2]
                    date = date1 + "-" +date2




                elif name4.split("-")[0] == "db120":
                    date = 'db120'

                else:
                    date = ""


                item["ProductModel"] = date
                item["ProductClass"] = "Router"


#################################################################################

                #item["Release_time"] =

                try:
                    p_s = r[i + 1].split(" ")
                    item["PublishTime"] = p_s[0]
                    print "**************************************************"
                    print item["PublishTime"]
                    #item["Info"]["Published"] = p_s[0]
                    reg = re.compile(r'[0-1][0-9][0-1][0-9][0-3][0-9]')
                    regs = reg.search(item["Filename"])
                    if regs !=None:
                        item["PackedTime"] = regs.group()
                    if regs ==None:
                        item["PackedTime"] = ""


                    a = item["PublishTime"]
                    a = a.strip()

                    #print a
                    #print"#####################################################"

                    try:
                        array=time.strptime(a,u"%d-%b-%Y")
                        item["PublishTime"] = time.strftime("%Y-%m-%d",array)
                    except Exception, e:
                        #print"**********************format errror***********************"
                        print e
                                    #print "************ss"


                    #item["Info"]["Size"] = p_s[-1]
                except:
                    #item["Info"]["Size"] = None
                    print ""

                yield item
                print item["PublishTime"]

            i += 2

        return
