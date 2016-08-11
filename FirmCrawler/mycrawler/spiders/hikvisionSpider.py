# -*- coding: UTF-8 -*-

from sets import Set
from urlparse import *
import urllib2
import re

from scrapy.spiders import Spider

import mycrawler.items as MI


header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}


class DlinkSpider(Spider):
    name = "hikvision"
    timeout = 8
    trytimes = 3
    start_urls = [
        "http://www.hikvisioneurope.com/portal/index.php?dir=Product%20Firmware/"
        # 'http://www.hikvisioneurope.com/portal/index.php?dir=Product%20Firmware/Cameras/DS-2CD2X22FWD%2C2X42FWD%2C2X52F/'
    ]
    suffix = ["zip", "obj", "exe", "drv", "com", "lan",
              "dlf", "tar", "tgz", "gz", "iso", "img", "dmg", "bin"]


    # 得到返回上一页的链接和进入下一页的链接
    def get_children_url(self, url):
        print url, '\n\n'
        t = 5
        while t > 0:
            try:
                res = urllib2.urlopen(urllib2.Request(
                    url, None, header), timeout=10)
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(res.read())
                tb = soup.find_all('table')[-2]

                return set([urljoin(self.domain, a.attrs.get('href'))
                            for a in tb.find_all('a')[1:]])
            except Exception, e:
                print e
                t -= 1

    def pparse(self, url, data):

        children_url = self.get_children_url(url)

        if not children_url:
            return

        print children_url, "children_url\n\n\n"
        for child_url in children_url:

            trytime = 5
            while trytime > 0:
                try:
                    res1 = urllib2.urlopen(urllib2.Request(child_url, None, header))
                    t = res1.headers.dict.get(
                        'content-type').split(r'/')[-1].split(r';')[0]

                    if t == 'html':
                        self.pparse(child_url, data)
                    elif t.lower() in self.suffix:

                        filename = child_url.split('file=')[-1]

                        item = MI.BasicItem()

                        item["ProductVersion"]=""
                        item["PackedTime"]=""
                        item["ProductClass"]=""
                        #item["Info"]["Size"]=""
                        item["ProductModel"]=""
                        item["Description"]=""



                        item["Manufacturer"] = "Hikvision"
                        item["URL"] = child_url
                        #item["Rawlink"] = child_url
                        item["FirmwareName"] = filename
                        # res1.headers.dict.get(
                        # "content-type").split('name=')[-1].strip('"')

                        #item["Title"] = item["Filename"]


                        reg = re.compile(r'[0-1][0-9][0-1][0-9][0-3][0-9]')
                        regs = reg.search(filename)
                        if regs !=None:
                            item["PackedTime"] = regs.group()
                        if regs ==None:
                            item["PackedTime"] = ""
                        #item["Info"]["Published"] = re.match(reg,filename).group()
                        #item["Release_time"] =
                        filename1 = filename.split('_')

                        if len(filename1) >= 2 and filename1[-1].isalnum():
                            #item["Info"]["Published"] = filename1[-1]
                            item["PublishTime"] = filename1[-1]  #################
                            item["ProductVersion"] = filename1[-2]
                            item["ProductModel"] = filename1[0]
                            print filename
                            print item["PackedTime"]

                        print item
                        data.add(item)
                    break
                except Exception, e:
                    print e
                    trytime -= 1

    def parse(self, response):

        r = urlparse(response.url)
        self.domain = response.url.split(r.path)[0]
        data = Set()
        self.pparse(response.url, data)
        return data
