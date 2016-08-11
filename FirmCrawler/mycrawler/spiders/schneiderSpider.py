# -*- coding: UTF-8 -*-

from sets import Set


from scrapy.spiders import Spider
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import mycrawler.items as MI

import re
import time

class SchneiderSpider(Spider):
    name = "schneider"
    start_urls = [
        "http://www.schneider-electric.com/download/ww/en/results/3541958-SoftwareFirmware/1555893-Firmware--Released/?showAsIframe=false",
        "http://www.schneider-electric.com/download/ww/en/results/3541958-SoftwareFirmware/1555902-Firmware--Updates/?showAsIframe=false",
    ]
    timeout = 15
    trytimes = 3

    # must be lower character
    suffix = ["zip", "bin", "exe", "rar", "upg", "7z", "tar", "gz", "tgz"]
    allsuffix = Set()

    def parse(self, response):

        browser = webdriver.Firefox()
        browser.implicitly_wait(SchneiderSpider.timeout)
        browser.set_page_load_timeout(SchneiderSpider.timeout)
        # return

        # self.parse_page("http://www.schneider-electric.com/download/ww/en/details/987961741-ComX-510-v1144-Firmware-EBX510/?showAsIframe=false&reference=ComX510v1-1-44_Firmware_EBX510",browser)

        t = SchneiderSpider.trytimes
        while True:
            try:
                browser.get(response.url)
            except TimeoutException:
                pass
            try:
                table = browser.find_element_by_id("gridResults")
            except Exception, e:
                t -= 1
                if t == 0:
                    browser.quit()
                    raise e
            else:
                break

                # sel=Selector(table)
                # print table.get_attribute("innerHTML")
        page = u"0"
        t = SchneiderSpider.trytimes
        links = Set()
        while True:
            try:
                WebDriverWait(browser, SchneiderSpider.timeout).until(
                    lambda d: page != (d.find_element_by_id(
                        "gridPager_right").find_element_by_class_name("sel").text))
            except WebDriverException, e:
                if t == 0:
                    browser.quit()
                    raise e
                t -= 1
                continue
            page = browser.find_element_by_id(
                "gridPager_right").find_element_by_class_name("sel").text
            rows = table.find_elements_by_xpath("//tr[position()>1]")
            for tr in rows:
                links.add(tr.find_element_by_xpath(
                    'td[5]/a[1]').get_attribute("href"))
            if browser.find_element_by_id("gridPager_right").find_element_by_xpath("a[last()-1]").get_attribute(
                    "class") == "sel":
                break
            try:
                browser.find_element_by_id(
                    "gridPager_right").find_element_by_xpath("a[last()]").click()
            except TimeoutException:
                pass
            t = SchneiderSpider.trytimes

        files = Set()
        for link in links:
            t = SchneiderSpider.trytimes


            while True:
                nbrowser = webdriver.Firefox()
                try:
                    if not nbrowser:
                        nbrowser = webdriver.Firefox()
                    yield self.parse_page(link, nbrowser)

                except WebDriverException, e:
                    t -= 1
                    nbrowser.quit()
                    if t == 0:
                        break
                else:
                    nbrowser.quit()
                    break




        browser.quit()
        # return files

        # def parse_page(self,response):

    # link=response.url
    def parse_page(self, link, browser):
        browser.implicitly_wait(SchneiderSpider.timeout)
        browser.set_page_load_timeout(SchneiderSpider.timeout)
        try:
            browser.get(link)
            WebDriverWait(browser, SchneiderSpider.timeout, 500).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jqgfirstrow")))
        except TimeoutException:
            pass

        scope = browser.find_element_by_class_name("mainPadding")
        item = MI.BasicItem()
        #item["Title"] = scope.find_element_by_xpath("//h1").text
        item["Manufacturer"] = "Schneider"
        #item["Info"] = {}
        item["ProductVersion"]=""
        item["PackedTime"]=""
        item["ProductClass"]=""
        #item["Info"]["Size"]=""
        item["ProductModel"]=""
        item["Description"]=""


        Energy = ["ION","730","733",'735','755','765','800','860','865','Dev','CM3','CM4','PM2','PM5','PM8','SC2','LAN','BCP','Com']
        Plc_Pac = ['140','Cpu','ETC','ETG','ETH','M1e','Mli','M22','M23','M24','M25','NOC','NOE','TSX','BME','eg0']
        In_ethernet = ['tcs']
        Motor = ['MLD','LXM','LMC','Tes']
        Scada = ['Sca','TRS']
        item["ProductClass"] = "Other"



        labels = scope.find_elements_by_xpath("div/div/div[@class='label']/p")
        label_contents = scope.find_elements_by_xpath(
            "div/div/div[@class='labelContent']/p")
        for i in range(len(labels)):
            lable = labels[i]
            lst = lable.text.rstrip().rstrip(":").split(" ")
            if len(lst) == 0:
                continue

            key = lst[-1]  # .lower()
            if key == "Description":
                item["Description"] = label_contents[i].text
            elif key == "Date":
                item["PackedTime"] =""          #label_contents[i].text
                item["PublishTime"] = label_contents[i].text

                a = item["PublishTime"]
                try:
                    array = time.strptime(a,"%d-%b-%Y")
                    item["PublishTime"] = time.strftime("%Y-%m-%d",array)
                except:
                    print"format error"

        datas = Set()
        links = scope.find_elements_by_xpath(
            "//table[@id='gridResults']/tbody/tr/td/a[@class='open-popup']")
        for l in links:
            filetype = l.text.split(".").pop()
            SchneiderSpider.allsuffix.add(filetype)
            if filetype in SchneiderSpider.suffix:
                item["URL"] = l.get_attribute("href")
                #item["Rawlink"] = item["Link"].split("/?")[0]
                item["FirmwareName"] = l.text

                try:
                    item["ProductModel"] = l.text.split("_")[0]
                    item["ProductVersion"] = ""#l.text.split("_")[-1]
                    a = l.text
                    a2 = a.split(".")
                    a3 = a.replace("." + a2[-1],"")
                    a4 = a3.split("_")[0]
                    a5 = a4.split("-")[0]
                    item["ProductModel"] = a5

                    if a5 == "S":
                        item["ProductModel"] = a5 + a3.split("_")[1]
                    elif a5 == "FW":
                        item["ProductModel"] =  a3.split("_")[1]
                    elif a5 == "Text":
                        item["ProductModel"] = a4.split("-")[1]
                    elif a5 == "Firmware":
                        item["ProductModel"] =  a4.split("-")[1]
                    elif a5 == "upgrade":
                        item["ProductModel"] = a4.split("-")[1]

                    s1 = re.compile(r"(V|v)[1-9]\.")
                    s2 = s1.match(a5)
                    if s2:
                        item["ProductModel"] = ""




                    patt = re.compile(r'((v|V)([0-9]+\.*(lie[0-9]+)*\.*([0-9]+)*)\.*([0-9]+)*\.*([0-9]+)*)|([0-9]+\.([0-9]+)\.*([0-9]+)*\.*([0-9]+)*\.*([0-9]+)*)')
                    ma = patt.search(a3)
                    if ma:
                        item["ProductVersion"] = ma.group()


                    try:
                        a = item["ProductModel"][0] + item["ProductModel"][1] + item["ProductModel"][2]
                        if a == 'Con' and item["ProductModel"][3] == 'n':
                            item["ProducClass"]= "In_ethernet"
                        elif a in Energy:
                            item["ProducClass"]= "Energy"
                        elif a in Plc_Pac:
                            item["ProducClass"]= "Plc_Pac"
                        elif a in Motor:
                            item["ProducClass"]= "Motor"
                        elif a in In_ethernet:
                            item["ProducClass"]= "In_ethernet"
                        elif a in Scada:
                            item["ProducClass"]= "Scada"
                        else:
                            item["ProducClass"] = "Other"
                    except:
                        item["ProducClass"] = "Other"





                    #a1 = l.text.split("_")[-1]
                    #b = a1.split(".")
                    #item["Info"]["Version"] = a1.replace("." + b[-1],"")



                except:
                    pass




                # result.add(tmp)
                print "\n\n\n\nsucess"
                datas.update(item)
                return item
        return datas

        # print "\n\n\n",tmp,"\n\n\n"
        # print "\t\n",len(result),"\t\n"

        # logging.log(logging.INFO,"Page:%s,fetch %d links,get %d items",link,len(links),len(result))
        # return result
