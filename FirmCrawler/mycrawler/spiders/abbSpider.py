# -*- coding: UTF-8 -*-
import logging
import mycrawler.items as MI
import time

from scrapy.spiders import Spider
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#from mycrawler.items import BasicItem

class AbbSpider(Spider):
    name = "abb"
    # url_items(name)
    start_urls = [
        "http://www.abb.com/AbbLibrary/DownloadCenter/default.aspx?showresultstab=true&CategoryID=9AAC113401&DocumentKind=Manual&Documentlanguage=zh&DisplayLanguage=en#&&/wEXAQUDa2V5BYMBM8KwOUFBQzE3NzAzM8KxwrHCsVNvZnR3YXJlwrHCsVTCscKxNMKxwrEyOcKxQ07CscKxMsKxVMKxMMKxwrEwwrExwrEyMMKxMjDCsTHCscKxwrHCscKxOUFBQzExMzQwMcKxwrHCscKxMTHCscKxwrHCsTY4wrHCsTDCsUNOwrHCsTB9cE7o9jBIVfA/PfxkFN8NH2/JJQ==",
    ]
    timeout = 5
    trytimes = 3

    def parse(self, response):
        self.no=1
       

        # 使用火狐驱动
        browser = webdriver.Firefox(None, None, 15)
        # 显示声明超时时间
        browser.implicitly_wait(AbbSpider.timeout)
        browser.set_page_load_timeout(AbbSpider.timeout)
        t = AbbSpider.trytimes
        # 检测，加载页面是否能够加载成功，尝试多次加载，失败后退出
        while 1:
            try:
                browser.get(AbbSpider.start_urls[0])
            except TimeoutException:
                pass
            try:
                print "0\n\n\n\n"
                WebDriverWait(browser, AbbSpider.timeout, 1).until(lambda x: x.find_element_by_id(
                    "ctl00_csMainRegion_csContentRegion_MainArea_paging_pagingUl_span2N_2N").text == "Next")
                # "//div[@class='boxfilter']/div/p[@class='value']"
                print "\n\n\n\n"
            except Exception, e:
                print e
                try:
                    WebDriverWait(browser, AbbSpider.timeout).until(lambda x: x.find_element_by_id(
                        "ctl00_csMainRegion_csContentRegion_MainArea_paging_pagingUl_span2N_2N").text == "Next")
                    print "2\n\n\n\n"
                except TimeoutException, e:
                    print e
                    t -= 1
                    logging.log(
                        logging.WARNING, "Switching to PLC page failed(%d)", AbbSpider.trytimes - t)
                    if t == 0:
                        print e
                        browser.quit()
                        return
            else:
                break
        page = "0"
        t = AbbSpider.trytimes
        while 1:
            try:
                # 智能等待和加载，只要until里面为True就成功
                WebDriverWait(browser, AbbSpider.timeout).until(lambda x: page != (
                    x.find_element_by_xpath("//ul[@class='paging']/li/span[@class='current']").text))
            except WebDriverException, e:
                t -= 1
                logging.log(
                    logging.WARNING, "Going to next page failed(%d)", AbbSpider.trytimes - t)
                if t == 0:
                    browser.quit()
                    raise e
                continue
                # 用xpath定位元素
            page = browser.find_element_by_xpath(
                "//ul[@class='paging']/li/span[@class='current']").text
            t = AbbSpider.trytimes
            while 1:
                # 运行js脚本
                browser.execute_script(
                    "javascript:__doPostBack('ctl00$csMainRegion$csContentRegion$MainArea$inner$expcolall','')")
                try:
                    WebDriverWait(browser, AbbSpider.timeout).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "share")))
                except TimeoutException:
                    t -= 1
                    logging.log(
                        logging.WARNING, "Expanding all details failed(%d)", AbbSpider.trytimes - t)
                    if t == 0:
                        browser.quit()
                        raise TimeoutException(
                            "Detail for items cannot be expanded")
                else:
                    break
            t = AbbSpider.trytimes
            rows = browser.find_elements_by_xpath(
                "//div[@id='ctl00_csMainRegion_csContentRegion_MainArea_result']/div/div/div/div[@class='details']")


            testone = 1  ###################################################
            for tr in rows:
                item = MI.BasicItem()
               # item["Info"] = {}

                #item["Info"] = {}
                item["ProductVersion"]=""
                item["PackedTime"]=""
                item["ProductClass"]=""
                #item["Info"]["Size"]=""
                item["ProductModel"]=""
                #item["Published"]=""

                item["Manufacturer"] = "Abb"
                #item["Title"] = tr .find_element_by_class_name("title").text
                item["URL"] = tr.find_element_by_xpath(
                    "div[@class='title']/span/a").get_attribute("href")
                #item["Rawlink"] = item["Link"].split("&", 1)[0]
                pros = tr.find_elements_by_xpath(
                    "div[@class='properties']/span[@class='property']")
                vals = tr.find_elements_by_xpath(
                     "div[@class='properties']/span[@class='value']")
                print "##########################",testone,"##########################"
                testone = testone + 1
                i = 0

                testtwo = 1
                while i < len(pros):
                    key = pros[i].text.rsplit(":", 1)[0]
                    if key == "Summary":
                        item["Description"] = vals[i].text
                    elif key == "Doc No":
                        item["FirmwareName"] = vals[i].text
                    elif key == "File type":
                        item["FirmwareName"] += "." + vals[i].text
                    elif key == 'PublishTime':
                        #item["Info"]["Pub_time"] =[""] #vals[i].text
                        item["PublishTime"]= vals[i].text#后面加

                        a = item["PublishTime"]
                        a = a.strip()
                        #print a
                        #print"#####################################################"

                        try:
                            array=time.strptime(a,u"%Y-%m-%d %H:%M:%S")
                            item["PublishTime"] = time.strftime("%Y-%m-%d",array)
                        except Exception, e:
                            #print"**********************format errror***********************"
                            print e
                            #print "************ss"

                    #elif key == 'Size':
                     #   item["Info"]["Size"] = vals[i].text
                    elif key == 'Revision':
                        item["ProductVersion"] = vals[i].text
                    elif key == 'Document kind':
                        item["ProductClass"] = vals[i].text

                    i += 1
                    #i = len(pros)
                   # items.add(item)
                    print"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                    print len(pros)
                    print"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                    
                    print "\n\n\n\n"
                    print "*************",self.no,"*************"

                    print"$$$$$$$$$$$$$$$$$$$$$$$$",testtwo,"$$$$$$$$$$$$$$$$$$$$$$$"
                    testtwo = testtwo+1
                    
                    print "\n\n\n\n"
                    self.no=self.no+1
                    try:
                        if i ==len(pros):
                            yield item
                        else:
                            print "love"
                    except Exception,e:
                        print e

                    #yield item

            if browser.find_element_by_xpath("//ul[@class='paging']/li[position()=last()]").text == "":
                break
            # break #debug
            # logging.log(logging.INFO,"[Progress] Page %s finished: Total %d items",page,len(items))
            try:
                browser.find_element_by_xpath(
                    "//ul[@class='paging']/li/span[@class='arrow']/a").click()
            except TimeoutException:
                pass
            t = AbbSpider.trytimes
        #browser.quit()
        browser.close()
        #return items