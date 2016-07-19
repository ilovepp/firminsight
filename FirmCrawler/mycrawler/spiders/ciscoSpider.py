# -*- coding: UTF-8 -*-

from sets import Set
from scrapy.spiders import Spider
import scrapy
import urllib2
import urlparse
import mycrawler.items as MI
import re
import time
from lxml import etree

header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}
a = "http://www.linksys.com/us/"

class OpenwrtSpider(Spider):
    name = "cisco"
    timeout = 8
    trytimes = 3
    start_urls = [
       'http://www.linksys.com/us/search?text=firmware&type=support_downloads'
    ]



    # must be lower character
    #suffix = ["bin", "bix", "trx", "img", "dlf", "tfp", "rar", "zip"]
    ahref = []
    #allsuffix = Set()


    def parse(self, response):




        try:
            print response
            ahref = response.xpath('//ul[@class="support-list"]/li/a/@href').extract()
            #print "##########################"

            print ahref
           # print "*************************"

            index = 0

            #s = 1
            for x in ahref:

                index+=1
                print "==================",index,"============="


                #if index < 100:
                 #   continue



                x = urlparse.urljoin(a,x)
                #print x
                t = 4
                while t > 0:
                    try:
                        res = urllib2.urlopen(urllib2.Request(x,None,header),timeout=10)
                        html = res.read()
                        #print s
                        #s = s + 1
                        #from bs4 import BeautifulSoup
                        #soup = BeautifulSoup(res.read())
                        html = etree.HTML(html)
                        zzs = html.xpath('//div[@id="support-article-downloads"]')
                        print "zhaodaop"
                        print zzs

                        for x in zzs:
                            #print "mashangzhaoa"
                            z1 = x.xpath('.//a[@target="_blank"]')
                            #print "zhaodaoa"
                            #print z1
                            #z2 = x.xpath('//a/@href')
                            #print "zhaodaolianjie"

                            #print z2
                            for y in z1:
                                print "mashangdaozzz"

                                zz1 = y.xpath('./text()')[0]
                                zz2 = y.xpath('./@href')[0]
                                print zz2
                                print zz1





                                if zz1 == 'Download':

                                        print "$$$$$$$$$$$$$$$$$$$$$"


                                        print zz1
                                        print "11111111111111111111111"
                                        link = zz2
                                        print link

                                        name = link.split("/")[-1]
                                        name1 = name.replace('.' + name.split('.')[-1],"")
                                        print name1



                                        item = MI.BasicItem()
                                        #item = BasicItem()

                                        #item["Info"]["Version"]=""
                                        item["PackedTime"]=""
                                        item["ProductVersion"] = ""
                                        item["ProductClass"]=""

                                        item["ProductModel"]=""
                                        item["Description"]= ""
                                        item["FirmwareName"] = name
                                        item["Manufacture"] = "Cisco"



                                        item["ProductModel"]= name1.split("-")[0]
                                        try:
                                            if name1.split("_")[1]:
                                                item["ProductModel"]= name1.split("_")[0] + name1.split("_")[1]
                                        except:
                                            print ""
                                        #item["Info"]["Model"]= name1.split("-")[0]


                                        name2 =  name1.split(".")[0]
                                        if name2 in ["LinksysConnect","Setup","ExtenderSetups","CiscoConnect","ExtenderSetup"]:

                                            item["ProductModel"]= name1.split(".")[1]

                                        elif name2 == "Downloadable":
                                            item["ProductModel"]= name1.split(".")[2]
                                        elif name2 in ["EA2700","EA3500","PLW"]:
                                            item["ProductModel"]= name1.split(".")[0]
                                        elif name1.split("_")[0] in ["WRT160N","WRT320N"]:
                                            item["ProductModel"]= name1.split("_")[0]





                                        a1 = re.compile(r'[1-9]\.[0-9]+\.[0-9]+(\.[0-9]+)*')

                                        a2 = a1.search(name1)
                                        #print "***********************a2a2a2a2****************************"
                                        #print a2
                                        if a2:
                                            item["ProductVersion"]= a2.group()
                                        reg = re.compile(r'20[0-1][0-9][0-1][0-9][0-3][0-9]')
                                        regs = reg.search(item["Name"])
                                        if regs !=None:
                                            item["PackedTime"] = regs.group()







                                        item["URL"] = link




                                        yield item

                    except Exception,e:
                        print e
                        t -= 1
        except Exception,e:
            print e






