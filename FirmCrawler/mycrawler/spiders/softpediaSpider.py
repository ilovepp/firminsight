# -*- coding: UTF-8 -*-

import urllib2
import re
import logging
from scrapy.spiders import Spider
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.common.exceptions import *

import mycrawler.items as MI
import time


# available since 2.26.0
from selenium.webdriver.support import expected_conditions as EC

header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}


class SoftpediaSpider(Spider):
    num = 0
    name = "softpedia"
    timeout = 10
    trytimes = 3
    start_urls = [
        "http://drivers.softpedia.com/get/FIRMWARE/Sony/"
    ]                                           #Toshiba

    # must be lower character
    suffix = ["zip", "obj", "exe", "drv", "com", "lan",
              "dlf", "tar", "tgz", "gz", "iso", "img", "dmg", "bin"]

    def get_url_info(self, url):
        trytime = 5
        while trytime > 0:
            try:
                res = urllib2.urlopen(urllib2.Request(url, None, header))
                content_type = res.headers.get('content-type').split(r';')
                if len(content_type) == 1:
                    return (content_type[0].split(r'/')[-1], None, res)
                else:
                    c_n = [x.split("name=").pop().strip('"')
                           for x in content_type[1:] if x.find('name=') != -1]
                    if not len(c_n):
                        return (content_type[0].split(r'/')[-1], None, res)
                    return (content_type[0].split(r'/')[-1], c_n.pop(), res)
            except Exception, e:
                print e
                trytime -= 1

    def get_url(self, url):
        urls = []
        if url[-1] != '/':
            url += '/'
        else:
            url += 'index%d.shtml'

        for i in range(1, 37):#####2

            trytime = 5
            while trytime > 0:
                try:
                    res = urllib2.urlopen(
                        urllib2.Request(url % i, None, header))
                    soup = BeautifulSoup(res.read())
                    download_tags = soup.find_all(
                        'div', attrs={"class": "grid_48 idx_drivers_item mgbot_30"})
                    if not download_tags:
                        break
                    for dt in download_tags:
                        href = dt.find('a').attrs.get('href')
                        print href
                        urls.append(href)
                    break
                except Exception, e:
                    print e
                    trytime -= 1

        return urls

    def get_onclick(self, url):
        trytime = 5
        while trytime > 0:
            try:
                res = urllib2.urlopen(urllib2.Request(url, None, header))
                soup = BeautifulSoup(res.read())
                click = soup.find(id='dlbtn1').find('a').attrs.get('onclick')
                return click
            except:
                trytime -= 1

    def get_download_url(self, url):
        trytime = 10
        while trytime > 0:
            browser = webdriver.Firefox()
            browser.implicitly_wait(10)
            browser.set_page_load_timeout(5)

            try:
                browser.get(url)
            except:
                pass

            try:
                try:
                    WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='dlbtn1']/a")))
                except TimeoutException:
                    pass
                try:
 #                   print "\nTEST", browser.find_element_by_xpath("//div[@class='fl']").get_attribute("innerHTML")
                    Published_time = browser.find_element_by_xpath("//div[@class='fl']//dd[3]").text
                    aa = browser.find_element_by_xpath(
                        "//div[@id='dlbtn1']/a").get_attribute('onclick')
                    #################

                    ######################

                    browser.execute_script(aa)
                except Exception,e:
                    logging.log(logging.WARNING,"get published time ERROR")
                    logging.exception(e)
                    pass

                t=3
                while t>0:
                    try:
                        WebDriverWait(browser, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='ov6popup']/div[2]/div[1]/a")))
                    except TimeoutException:
                        pass
                    try:
                        m = browser.find_element_by_xpath(
                            '//div[@id="ov6popup"]/div[2]/div[1]/a').get_attribute('href')
                        break
                    except:
                        aa = browser.find_element_by_xpath(
                        "//div[@id='dlbtn1']/a").get_attribute('onclick')
                        browser.execute_script(aa)
                        t-=1
                        logging.log(logging.WARNING,"Cannot Find ov6popup, re-execute - %d",t)

                try:
                    browser.get(m)
                except:
                    pass

                print "\n\n\n\nmanstart manstart", m
                # WebDriverWait(browser, 2).until(
                # EC.presence_of_element_located((By.XPATH,
                # '//div[@id="manstart"]/a')))

                # print browser.find_element_by_id("manstart"),"\n\n\n"
                # print "\n\n\n\nmanstart"
                durl = browser.find_element_by_xpath(
                    '//div[@id="manstart"]/a').get_attribute('href')
                print durl, "\n\n\n\n\n"

                item = MI.BasicItem()
                item["Manufacturer"] = "Softpedia"
                item["URL"] = durl
                #item["Rawlink"] = item["Link"]
                item["FirmwareName"] = durl.split('/')[-1]
                #item["Title"] = item["Filename"]
                #item["PublishTime"] = Published_time
                #a = item["PublishTime"]

                #item["Info"] = {}
                item["ProductVersion"]=""
                item["PackedTime"]=""
                item["ProductClass"]=""
                #item["Info"]["Size"]=""
                item["ProductModel"]=""
                item["Description"]=""


                reg = re.compile('20[0-1][0-9][0-1][0-9][0-3][0-9]')
                regs = reg.search(item["FirmwareName"])
                if regs !=None:
                    item["PackedTime"] = regs.group()
                if regs ==None:
                    item["PackedTime"] = [""]



                browser.quit()
                print item
                #yield item
                return item
            except Exception, e:
                logging.log(logging.WARNING, "%d-th fetch no data", trytime)
                logging.exception(e)
                browser.quit()
                trytime -= 1
                if trytime==0:
                    logging.log(logging.ERROR,"%s parse Failed",url)

    def parse(self, response):
 #       urls=self.get_url(response.url)
 #       print "\n",urls[0],"\n"
  #      return self.get_download_url(urls[0])
         return [self.get_download_url(url) for url in self.get_url(response.url)]
        # print self.get_url()

        # WebDriverWait(driver, 10).until(EC.title_contains("cheese!"))
