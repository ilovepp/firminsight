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
import re


class Siemens1Spider(Spider):
    name = "siemens"
    timeout = 10
    trytimes = 3
    start_urls = [
        "https://support.industry.siemens.com/cs/search?ps=100&search=%E5%9B%BA%E4%BB%B6&type=Download&lc=zh-CN"
        ,
        "https://support.industry.siemens.com/cs/search?ps=100&p=1&search=%E5%9B%BA%E4%BB%B6&type=Download&lc=zh-CN",
        "https://support.industry.siemens.com/cs/search?ps=100&p=2&search=%E5%9B%BA%E4%BB%B6&type=Download&lc=zh-CN",
        "https://support.industry.siemens.com/cs/search?ps=100&p=3&search=%E5%9B%BA%E4%BB%B6&type=Download&lc=zh-CN"
        ]
    handle_httpstatus_list = [404]


    # must be lower character
    suffix = ["zip", "obj", "drv",  "com", "lan",
              "dlf", "tar", "tgz", "gz", "iso", "img", "dmg","exe"]

    allsuffix = Set()

    def start_requests(self):
        for url in Siemens1Spider.start_urls:
            yield Request(url)



    def _loadcomplete(self, x):
        if len(x.find_elements_by_xpath('//*[@id="content"]/div/div/div[2]/div[3]/div[4]/div/div/div[2]/span[1]/a')) == self.finds:
            return True
        self.finds = len(x.find_elements_by_xpath('//*[@id="content"]/div/div/div[2]/div[3]/div[4]/div/div/div[2]/span[1]/a'))
        return False



    def parse(self, response):

        s_url = "https://support.industry.siemens.com"
        browser = webdriver.Firefox()
        browser.implicitly_wait(Siemens1Spider.timeout)
        browser.set_page_load_timeout(Siemens1Spider.timeout)

        t = Siemens1Spider.trytimes
        try:
            browser.get(response.url)
        except TimeoutException:
            pass
        self.dirs = Set()
        #print "mashangtiqushujv"
        for i in browser.find_elements_by_xpath('//a[@data-bind="attr: { href: getDetailLink() }"]'):
            #print i.get_attribute("href")
            self.dirs.add(i.get_attribute("href"))
            print "##########################"
            print i.get_attribute("href")
            print "**************************"
            # print len(self.dirs)
        # print self.dirs
        # return
        logging.log(logging.INFO, "Root Fetch:%d", len(self.dirs))
        items = Set()
        while len(self.dirs):
            d = self.dirs.pop()
            t = Siemens1Spider.trytimes
            while True:
                try:
                    browser.get(d)
                    self.finds = -1
                    try:
                        WebDriverWait(browser, Siemens1Spider.timeout).until(
                            self._loadcomplete)
                    except TimeoutException:
                        pass
                    lines = browser.find_elements_by_xpath(
                        '//a[@data-file-download=""]')
                    logging.log(logging.INFO, "Fetch:%s,len:%d", d, len(lines))
                    for l in lines:
                        #a = l.find_element_by_xpath("td[1]//a")
                        #if a.get_attribute("class") == "dir":
                         #   self.dirs.add(a.get_attribute("href"))
                        #elif a.get_attribute("class") == "file":
                        link = l.get_attribute("href")

                        filename = link.split("/")[-1]
                        filetype = filename.split(".")[-1]
                        print "@####################"+ filetype +"!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                        filename1 = filename.replace("." + filetype,"")




                        if filetype in Siemens1Spider.suffix :

                            item = MI.BasicItem()
                            #item["Info"] = {}
                            item["ProductVersion"] = ""
                            item["PackedTime"] = ""
                            item["ProductClass"] = ""
                            item["ProductModel"] = ""
                            item["Description"] = ""

                            item["Manufacturer"] = "Siemens"

                            item["URL"] = link#l.get_attribute("href").strip
                            item["FirmwareName"] = filename
                            item["ProductModel"] = filename1.split("_")[0]
                            patt = re.compile(r"(V|v)[1-9]+")
                            ma = patt.search(filename)

                            if ma:
                                item["ProductVersion"] = ma.group()


                                print "!!!!!!!!!!!!!!!!!!!!!!!!!match!!!!!!!!!!!!!!!!!!!!!!!!!!"




                            print item
                            #items.add(item)
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
                    str(Siemens1Spider.allsuffix))
        logging.log(logging.CRITICAL, "ParseSuffix: %s",
                    str(Siemens1Spider.suffix))

        browser.close()
        #return items
