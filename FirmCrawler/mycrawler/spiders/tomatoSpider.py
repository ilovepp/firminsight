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
class tomatoSpider(Spider):
    name = "tomato"
    timeout = 8
    trytimes = 3
    start_urls = ["http://tomato.groov.pl/download"]
    handle_httpstatus_list = [404]
    # must be lower character
    suffix = ["bin", "elf", "fdt", "imx", "chk", "trx","zip","gz"]
    allsuffix = Set()
    def start_requests(self):
        for url in tomatoSpider.start_urls:
            yield Request(url, meta={"build": "build", "product": "product"})
    def _loadcomplete(self, x):
        if len(x.find_elements_by_xpath("html/body/div/div/ul/li")) == self.finds:
          return True
        self.finds = len(x.find_elements_by_xpath("html/body/div/div/ul/li"))
        return False
    def parse(self, response):
        browser = webdriver.Firefox()
        browser.implicitly_wait(tomatoSpider.timeout)
        browser.set_page_load_timeout(tomatoSpider.timeout)
        t = tomatoSpider.trytimes
        try:
            browser.get(response.url)
        except TimeoutException:
            pass
        self.dirs = Set()
        for i in browser.find_elements_by_xpath('//li[@class="item folder"]/a'):
            # print i.get_attribute("href")
            self.dirs.add(i.get_attribute("href"))

            print len(self.dirs)
        # print self.dirs
        # return
        logging.log(logging.INFO, "Root Fetch:%d", len(self.dirs))
        items = Set()
        while len(self.dirs):
            d = self.dirs.pop()
            t = tomatoSpider.trytimes
            while True:
                try:
                    browser.get(d)
                    self.finds = -1
                    try:
                        WebDriverWait(browser, tomatoSpider.timeout).until(
                            self._loadcomplete)
                    except TimeoutException:
                        pass
                    lines = browser.find_elements_by_xpath(
                        "//li")
                    logging.log(logging.INFO, "Fetch:%s,len:%d", d, len(lines))
                    for l in lines:
                        #a = l.find_element_by_xpath("//li")
                        if l.get_attribute("class") == "item folder":
                            sxx = l.find_element_by_xpath('./a')  #'//li[@class="item folder"]/a'
                            self.dirs.add(sxx.get_attribute("href"))
                            #print"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
                        if l.get_attribute("class") == "item file":
                            print "............begin  file.............."
                            sx = l.find_element_by_xpath("./a")
                            link = sx.get_attribute("href")
                            print link

                            filenamee = sx.find_element_by_xpath("./span[@class='label']").text
                            #print "##########################################"
                            print filenamee
                            published = sx.find_element_by_xpath("./span[@class='date']").text
                            size = sx.find_element_by_xpath("./span[@class='size']").text
                             #   published =""
                              #  published = a.text


                            filename1 = filenamee.split("-")
                            print filename1


                            filetype = filenamee.rsplit(
                                ".", 1).pop().strip().lower()
                            print "filetype:%s"%filetype
                            tomatoSpider.allsuffix.add(filetype)
                            xun = 10
                            # print "FileType",filetype
                            if filetype in tomatoSpider.suffix and 'tomato' in filename1:   #用tomato替换FIRMWARE
                            #if xun > 0:
                                print"*********************************************"
                                item = MI.BasicItem()
                                #item["Info"] = {}
                                item["ProductVersion"]=""
                                item["PackedTime"]=""
                                item["ProductClass"]=""
                                #item["Info"]["Size"]=""
                                item["ProductModel"]=""
                                item["Description"]=""
                                item["Manufacturer"] = "Tomato"
                                item["URL"] = link
                                #item["Rawlink"] = item["Link"]
                                item["FirmwareName"] = filenamee
                                #item["Title"] = item["Filename"]
                                item["Description"] = filenamee

                                aaa= filenamee.split("-")
                                item["ProductModel"] = aaa[1]
                                #item["Descr"] = browser.find_element_by_xpath(
                                  #  "//h1").text.rsplit("/", 1)[0]
                                item["PackedTime"] = [""] #l.find_element_by_xpath(
                                    #  "td[3]").text
                                item["PublishTime"] = published             # HOUMIANJIA
                                a = item["PublishTime"]

                                try:

                                    array=time.strptime(a,u"%Y-%m-%d %H:%M")
                                    item["PublishTime"] = time.strftime("%Y-%m-%d",array)
                                except:
                                    print"**********************format errror***********************"

                                    #print "************ss"
                                #item["Info"]["Size"] = size
                                #item["Info"]["Model"] = filename1[0]
                                #item["Info"]["Version"] = filename1[-1]
                                #item["Info"]["Class"] = filename1[-2]

                                # items.add(item)

                                print"#############################**************************"
                                yield item
                                print "item   bei  cun  jin  qu"
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
                    str(tomatoSpider.allsuffix))
        logging.log(logging.CRITICAL, "ParseSuffix: %s",
                    str(tomatoSpider.suffix))
        #browser.quit()
        browser.close()
        # return items

