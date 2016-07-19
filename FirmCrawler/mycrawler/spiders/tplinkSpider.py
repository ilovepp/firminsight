# -*- coding: UTF-8 -*-

from sets import Set
import logging
import re
import time

from scrapy.spiders import Spider
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from mycrawler.items import BasicItem


class TplinkSpider(Spider):
    name = "tplink"
    start_urls = [
        "http://service.tp-link.com.cn/list_download_software_1_0.html"
    ]
    timeout = 5
    trytimes = 3

    def parse(self, response):


        browser = webdriver.Firefox()
        browser.implicitly_wait(TplinkSpider.timeout)
        browser.set_page_load_timeout(TplinkSpider.timeout)

        t = TplinkSpider.trytimes
        try:
            browser.get(response.url)
        except TimeoutException:
            pass

        page = u"0"
        t = TplinkSpider.trytimes
        links = Set()
        while True:
            try:
                tmpfunc = lambda d: page != (d.find_element_by_id(
                    "paging").find_element_by_class_name("selected").text)
                WebDriverWait(browser, TplinkSpider.timeout) \
                    .until(tmpfunc)
            except WebDriverException, e:
                try:
                    browser.find_element_by_id("paging") \
                        .find_element_by_xpath("a[last()]").click()
                except TimeoutException:
                    pass
                if t == 0:
                    browser.quit()
                    raise e
                t -= 1
                continue
            else:
                page = browser.find_element_by_id("paging") \
                    .find_element_by_class_name("selected").text

            try:
                table = browser.find_element_by_id("mainlist")
            except NoSuchElementException, e:
                t -= 1
                if t == 0:
                    browser.quit()
                    raise e

            t = TplinkSpider.trytimes
            rows = table.find_elements_by_xpath("//tr[position()>1]")

            for tr in rows:
                # links.add(tr.find_element_by_xpath(
                # 'td[1]/a').get_attribute("href"))

                t = TplinkSpider.trytimes
                while True:
                    try:
                        nbrowser = webdriver.Firefox()
                        yield self.parse_page(tr.find_element_by_xpath(
                            'td[1]/a').get_attribute("href"), nbrowser)
                    except WebDriverException, e:
                        t -= 1
                        nbrowser.quit()
                        if t == 0:
                            logging.exception(e)
                            break
                    else:
                        nbrowser.quit()
                        break

            if browser.find_element_by_id("paging") \
                    .find_element_by_xpath("a[last()-1]").get_attribute("class") == "selected":
                break
            # break #debug

            logging.log(
                logging.INFO, "Page %s finished: Total %d links", page, len(links))

            try:
                browser.find_element_by_id("paging") \
                    .find_element_by_xpath("a[last()]").click()
            except TimeoutException:
                pass
            t = TplinkSpider.trytimes

        files = Set()
        i = 0
        for link in links:
            break
            t = TplinkSpider.trytimes
            while True:
                try:
                    nbrowser = webdriver.Firefox()
                    files.update(self.parse_page(link, nbrowser))
                except WebDriverException, e:
                    t -= 1
                    nbrowser.quit()
                    if t == 0:
                        logging.log(logging.ERROR,
                                    "Link %s parse failed", link)
                        logging.exception(e)
                        break
                else:
                    nbrowser.quit()
                    break
            i += 1
            logging.log(
                logging.INFO, "[Progress] Link %d/%d parse finished, get %d items", i, len(links), len(files))
        browser.quit()
        # return files

    def parse_page(self, link, browser):

        router = ["TL-WR","TL-R1","TD-W8","TL-MR","TL-WV","TL-WD","TL-ER","TL-TR","TL-H2","TL-CP","TL-PW"]

        modem = ["TD-89","TD-86","TD-88","TD-87"]

        camera = ["TL-SC"]

        switch = ["TL-SG","TL-SL"]

        ap = ["TL-WA","TL-AC","TL-AP"]

        printing_server = ["TL-PS"]

        browser.implicitly_wait(TplinkSpider.timeout)
        browser.set_page_load_timeout(TplinkSpider.timeout)
        try:
            browser.get(link)
        except TimeoutException:
            pass

        element = WebDriverWait(browser, TplinkSpider.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "download")))
        lines = element.find_elements_by_xpath(
            "table/tbody/tr[position()<last()]")
        item = BasicItem()
        item["Manufacturer"] = "Tplink"
        #item["Info"] = {}
        item["ProductVersion"]=""
        item["PackedTime"]=""
        item["ProductClass"]=""
        #item["Info"]["Size"]=""
        item["ProductModel"]=""
        item["Description"]=""


        for l in lines:
            key = l.find_element_by_xpath("td[1]").text.lstrip()
            val = l.find_element_by_xpath("td[2]")
            if key == u"立即下载":
                item["URL"] = val.find_element_by_xpath(
                    "a").get_attribute("href")
                #item["Rawlink"] = item["Link"]
                item["FirmwareName"] = item["URL"].rsplit("/", 1).pop()

                reg = re.compile(r'20[0-1][0-9][0-1][0-9][0-3][0-9]')
                regs = reg.search(item["FirmwareName"])
                if regs !=None:
                        item["PackedTime"] = regs.group()
                if regs ==None:
                        item["PackedTime"] = ""
            elif key == u"软件名称":
                b = val.text

                try:
                    a = b


                    m = a.replace(re.split(r'\w*', a)[-1], "").split(" ")
                    item['ProductModel'] = m[0]

                    c= re.search(r'V[0-9]+.[0-9]',a).group()  #m[-1].split("_")[0]
                    if c[-2] == "_":
                        cc = c.split("_")
                        item['ProductVersion'] = cc[0]
                    else:
                        item['ProductVersion'] = c





                    #item["Published"] = m[-1].split("_")[-1]
                    #item["Info"]['Published'] = m[-1].split("_")[-1]
                    #a = item["Published"]
                    #a = a.strip()
                                #print a
                                #print"#####################################################"

                    #try:
                     #   array=time.strptime(a,u"%y%m%d")
                      #  item["Published"] = time.strftime("%Y-%m-%d",array)
                    #except Exception, e:
                                    #print"**********************format errror***********************"
                     #   print e
                                    #print "************ss"

                except:
                    pass

            elif key == u"软件简介":
                item["Description"] = val.text

            #elif key == u"软件大小":
             #   item["Info"]['Size'] = val.text

            elif key == u"上传日期":
                item["PublishTime"] = val.text

                a = item["PublishTime"]
                a = a.strip()
                print a
            try:
                a1 = item["ProductModel"]
                #item["Info"]["Class"] = "Other"
                a2 = re.compile(r"T(L|D)-..")
                a3 = a2.match(a1)
                if a3:
                    a4 = a3.group()
                    if a4 in router:
                        item["ProductClass"] = "Router"
                    elif a4 in switch:
                        item["ProductClass"] = "Switch"
                    elif a4 in camera:
                        item["ProductClass"] = "Camera"
                    elif a4 in modem:
                        item["ProductClass"] = "Modem"
                    elif a4 in ap:
                        item["ProductClass"] = "Ap"
                    elif a4 in printing_server:
                        item["ProductClass"] = "Printing_server"

                    else:
                        item["ProductClass"] = "Other"

                else:
                    item["ProductClass"] = "Other"
            except:
                item["ProductClass"] = "Other"

                                #print"#####################################################"

                try:
                   array=time.strptime(a,"%Y/%m/%d")
                   item["PublishTime"] = time.strftime("%Y-%m-%d",array)
                except Exception, e:
                                    #print"**********************format errror***********************"
                   print e

        return item
