# -*- coding: UTF-8 -*-

from sets import Set

from scrapy.spiders import Spider
import scrapy

from mycrawler.items import BasicItem
import re


class VipaSpider(Spider):
    name = "vipa"
    timeout = 20
    trytimes = 3
    start_urls = ["http://www.vipa.com/en/service-support/downloads/firmware"]
    # must be lower character
    typefilter = ["txt", "pdf"]
    allsuffix = Set()

    def parse(self, response):
        request = scrapy.Request(response.url, callback=self.parse_page)
        request.meta["prototype"] = BasicItem()
        #request.meta["prototype"]["Info"] = {}
        request.meta["prototype"]["Manufacturer"] = "Vipa"
        yield request

    def parse_page(self, response):
        lines = response.selector.xpath(
            "//div[@class='sbfolderdownload']/a")
        prototype = response.meta['prototype']
        dirs = response.selector.xpath(
            "//div[@id='sbfolderFolderWrap']/div[@class='sbfolderFolder']/a/@href").extract()

        for i in dirs:
            request = scrapy.Request(
                response.urljoin(i), callback=self.parse_page)
            request.meta["prototype"] = response.meta["prototype"]


            yield request
        for a in lines:

            filename = a.xpath("text()").extract().pop()
            filetype = filename.rsplit(".", 1).pop().strip().lower()
            VipaSpider.allsuffix.add(filetype)
            if not filetype in VipaSpider.typefilter:
                item = BasicItem()
                #item["Info"] = {}
                item["ProductVersion"]=""
                item["PackedTime"]=""
                item["ProductClass"]=""
                #item["Info"]["Size"]=""
                item["ProductModel"]=""
                item["Description"]=""


                item["Manufacturer"] = "Vipa"

                ttt = response.urljoin(
                    a.xpath("@href").extract().pop())
                item["URL"]=ttt.replace(" ","%20")
                #item["Rawlink"] = item["Link"].split("&", 1)[0]
                item["FirmwareName"] = filename
                #item["Title"] = item["Filename"]
                item["Description"] = str().join(
                    a.xpath("//div[@class='up']//text()").extract())


                reg = re.compile(r'[0-1][0-9]-[0-1][0-9]-[0-3][0-9]')
                regs = reg.search(filename)
                if regs !=None:
                    item["PackedTime"] = regs.group()
                if regs ==None:
                    item["PackedTime"] = ""

                try:
                    ss = ["DP","CPU","CP","image","a1","a2","a3"]
                    ss1 = ["FEE0","3Bxxx"]
                    ss2 = ["Bb000082","BB000088","BB000090","BB000021"]

                    m = filename.split("_")

                    xx = m[-1].replace(".zip","")
                    xx = xx.replace(".bin","")
                    xx = xx.replace(".BIN","")
                    xx = xx.replace(".os","")

                    if xx in ss:
                        xx = m[-2]
                    c = xx.split("-")
                    if c[-1] in ss1:
                        xx = "CE6.0"

                    if xx == "CXX":
                        xx = ""

                    cc = xx.split(".")
                    if cc[0] in ss2:
                        xx = ""

                    aa = str().join(
                    a.xpath("//div[@class='up']//text()").extract())

                    xxx = xx.split("-")[0]
                    xxx1 = xx.split(".")[0]
                    if xxx in ["CORE","PROF","DEMO"]:
                        xx = ""

                    elif xxx in ["M","MOV","ZENON"]:
                        xx = xx.split("-")[1]
                    if xxx1 == "Bb000125":
                        xx = ""
                    item["ProductVersion"] = xx

                    item["ProductModel"] = item["URL"].split("/")[6] .replace('%20', " ").strip()
                    Controlsystem = ["System 300S","System 100V","System 200V","System 300V","System 400V","System 500S","System 500V"]
                    Sliosystem = ["System Slio"]
                    Hmi = ["HMI"]
                    Netcomponents = ["Components"]
                    Zubehor=["Zubehör"]
                    if item["ProductModel"] in Netcomponents:
                        item["ProductClass"]= "Netcomponents"
                    elif item["ProductModel"] in Sliosystem:
                        item["ProductClass"]= "Sliosystem"
                    elif item["ProductModel"] in Hmi:
                        item["ProductClass"]= "Hmi"
                    elif item["ProductModel"] in Controlsystem:
                        item["ProductClass"]= "Controlsystem"
                    elif item["ProductModel"] in Zubehor:
                        item["ProductClass"] = "Zubehör"
                    else:
                        item["ProductClass"]= "Other"

                    # item["ProductModel"] = item["URL"].split("/")[6].replace('%20', " ")

                except:
                    pass



                yield item
