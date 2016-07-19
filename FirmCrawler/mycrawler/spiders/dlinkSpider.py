# -*- coding: UTF-8 -*-

from sets import Set
import logging

from scrapy.spiders import Spider
from scrapy.http import Request
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait

import mycrawler.items as MI
import time


class DlinkSpider(Spider):
    name = "dlink"
    timeout = 8
    trytimes = 3
    start_urls = ["ftp://ftp2.dlink.com/PRODUCTS"]
    handle_httpstatus_list = [404]

    # must be lower character
    suffix = ["zip", "obj", "drv", "com", "lan",
              "dlf", "tar", "tgz", "gz", "iso", "img", "dmg"]




    allsuffix = Set()

    def start_requests(self):
        for url in DlinkSpider.start_urls:
            yield Request(url, meta={'ftp_user': 'anonymous', 'ftp_password': ''})

    def _loadcomplete(self, x):
        if len(x.find_elements_by_xpath("html/body/table/tbody/tr")) == self.finds:
            return True
        self.finds = len(x.find_elements_by_xpath("html/body/table/tbody/tr"))
        return False

    def parse(self, response):

        router = ["WBR","DIR","DSR","DI","DVG","DGL","DXN","DSR","DVX","DWC","EBR","TM"]

        switch = ["DGS","DES","DXS","DWS"]

        camera = ["DCS"]

        modem = ["DHP","DSL","DCM"]

        gateway = ["DSA","DG"]

        firewall = ["DFC"]

        hub = ["DFE"]

        ap = ["DWL","DAP"]


        browser = webdriver.Firefox()
        browser.implicitly_wait(DlinkSpider.timeout)
        browser.set_page_load_timeout(DlinkSpider.timeout)

        t = DlinkSpider.trytimes
        try:
            browser.get(response.url)
        except TimeoutException:
            pass
        self.dirs = Set()
        for i in browser.find_elements_by_xpath("//a[@class='dir']"):
            # print i.get_attribute("href")
            self.dirs.add(i.get_attribute("href"))
            # print len(self.dirs)
        # print self.dirs
        # return
        logging.log(logging.INFO, "Root Fetch:%d", len(self.dirs))
        items = Set()
        while len(self.dirs):
            d = self.dirs.pop()
            t = DlinkSpider.trytimes
            while True:
                try:
                    browser.get(d)
                    self.finds = -1
                    try:
                        WebDriverWait(browser, DlinkSpider.timeout).until(
                            self._loadcomplete)
                    except TimeoutException:
                        pass
                    lines = browser.find_elements_by_xpath(
                        "html/body/table/tbody/tr")
                    logging.log(logging.INFO, "Fetch:%s,len:%d", d, len(lines))
                    for l in lines:
                        a = l.find_element_by_xpath("td[1]//a")
                        if a.get_attribute("class") == "dir":
                            self.dirs.add(a.get_attribute("href"))
                        elif a.get_attribute("class") == "file":
                            filename = a.text

                            filename1 = filename.split("_")
                            filetype = filename.rsplit(
                                ".", 1).pop().strip().lower()
                            DlinkSpider.allsuffix.add(filetype)
                            # print "FileType",filetype
                            if filetype in DlinkSpider.suffix and 'FIRMWARE' in filename1:
                                item = MI.BasicItem()

                                item["ProductVersion"]=""
                                item["PackedTime"]=""
                                item["ProductClass"]=""

                                item["ProductModel"]=""
                                item["Description"]=""



                                item["Manufacturer"] = "Dlink"

                                item["URL"] = a.get_attribute("href").strip()
                                #item["Rawlink"] = item["Link"]
                                item["FirmwareName"] = filename
                                #item["Title"] = item["Filename"]
                                item["Description"] = browser.find_element_by_xpath(
                                    "//h1").text.rsplit("/", 1)[0]

                                item["PackedTime"] = "" #l.find_element_by_xpath(

                                    #  "td[3]").text
                                item["PublishTime"] = l.find_element_by_xpath(
                                    "td[3]").text                # HOUMIANJIA

                                a = item["PublishTime"]
                                a = a.strip()
                                #print a
                                #print"#####################################################"

                                try:
                                    array=time.strptime(a,u"%Y年%m月%d日")
                                    item["PublishTime"] = time.strftime("%Y-%m-%d",array)
                                except Exception, e:
                                    #print"**********************format errror***********************"
                                    print e
                                    #print "************ss"

                                #item["Info"]["Size"] = l.find_element_by_xpath(
                                 #   "td[2]").text

                                item["ProductModel"] = filename1[0]
                                try:
                                    a1 = item["ProductModel"].split("-")[0]
                                    if a1 in router:
                                        item["ProductClass"] = "Router"
                                    elif a1 in switch:
                                        item["ProductClass"] = "Switch"
                                    elif a1 in camera:
                                        item["ProductClass"] = "Camera"
                                    elif a1 in modem:
                                        item["ProductClass"] = "Modem"
                                    elif a1 in gateway:
                                        item["ProductClass"] = "Gateway"
                                    elif a1 in firewall:
                                        item["ProductClass"] = "Firewall"
                                    elif a1 in hub:
                                        item["ProductClass"] = "Hub"
                                    elif a1 in ap:
                                        item["ProductClass"] = "Ap"
                                    else:
                                        item["ProductClass"] = "Other"


                                except:
                                    item["ProductClass"] = "Other"



                                xun = ["WIN","TC","WW","BETA","MAC","EN","RC"]
                                try:

                                    dd = filename.replace(".ZIP",'')
                                    print dd
                                    d = dd.split("_")
                                    if d[-2] == "FIRMWARE":
                                        item["ProductVersion"] = d[-1]


                                    else:
                                        if d[-3] == "FIRMWARE":
                                            item["ProductVersion"] = d[-2] + d[-1]

                                        elif d[-1]  in xun and d[-2] not in xun:
                                            item["ProductVersion"] = d[-2]  + d[-1]

                                        elif d[-1] in xun and d[-2] in xun:
                                            item["ProductVersion"] = d[-3] + d[-2] + "_" + d[-1]

                                        elif d[-2] == "PATCH":
                                            item["ProductVersion"] = d[-1]

                                        #elif d[-2] == "BETA" and d[-1] == "WW":
                                         #   item["Info"]["Version"] = d[-3]

                                        elif d[-2] == "UPDATE" or "UTILITY":
                                            item["ProductVersion"] = d[-1]

                                        elif d[-2] == "US":
                                            item["ProductVersion"] = d[-3]




                                    #else:
                                     #   item["Info"]["Version"] = d[-2] +d[-1]
                                except Exception, e:
                                    print e

                                #item["Info"]["Class"] = filename1[-2]
                                # items.add(item)
                                yield item
                                # return items #debug
                except Exception, e:
                    t -= 1
                    if t == 0:
                        logging.exception(e)
                        break
                    continue
                else:
                    break

        logging.log(logging.CRITICAL, "AllSuffix: %s",
                    str(DlinkSpider.allsuffix))
        logging.log(logging.CRITICAL, "ParseSuffix: %s",
                    str(DlinkSpider.suffix))

        #browser.quit()
        browser.close()
        # return items
