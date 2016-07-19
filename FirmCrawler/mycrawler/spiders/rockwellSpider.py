# -*- coding: UTF-8 -*-

from sets import Set
import re
import logging

from scrapy.spiders import Spider
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import mycrawler.items as MI


class RockwellSpider(Spider):
    name = "rockwell"
    def __init__(self,user = None,pwd = None,*args,**kwargs):
        """

        :param category:
        :param ar:
        :param ars:
        """
        super(RockwellSpider,self).__init__(*args,**kwargs)
        self.user = user
        self.pwd = pwd
        #self.start_urls = [URL]
        #self.timeout = 7
        #self.trytimes = 3
        #self.typefilter = ["pdf"]

    start_urls = [
        "http://compatibility.rockwellautomation.com/Pages/MultiProductDownload.aspx?keyword=Controller"
    ]



    timeout = 7
    trytimes = 3
    #user = "wangmt915940157@gmail.com"
    #pwd = "wmt199111400WMT"
    typefilter = ["pdf"]

    def noTimeoutClick(self, e):
        try:
            e.click()
        except TimeoutException:
            pass

    def login(self):
        try:
            reg = WebDriverWait(self.browser, RockwellSpider.timeout) \
                .until(EC.presence_of_element_located((By.ID, "regname"))).text.strip()
        except TimeoutException:
            reg = ""
        if reg == "":
            self.browser.find_element_by_id(
                "reglinks").find_element_by_xpath("a").click()
            usrtext = WebDriverWait(self.browser, RockwellSpider.timeout * 2).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='userName']")))

            #usrtext.send_keys(RockwellSpider.user)
            usrtext.send_keys(self.user)
            #self.browser.find_element_by_xpath(
             #   "//input[@name='password']").send_keys(RockwellSpider.pwd)

            self.browser.find_element_by_xpath(
                "//input[@name='password']").send_keys(self.pwd)
            self.noTimeoutClick(self.browser.find_element_by_xpath(
                "//input[@name='rememberMe']"))
            self.browser.execute_script("javascript:document.User.submit()")
        return True

    def loadpage(self, url):
        t = RockwellSpider.trytimes * 2
        while 1:
            try:
                self.browser.get(url)
            except TimeoutException:
                pass
            try:
                logged = self.login()
            except Exception, e:
                t -= 1
                if t == 0:
                    logging.exception(e)
                    return False
                else:
                    continue
            if not logged:
                continue
            try:
                WebDriverWait(self.browser, RockwellSpider.timeout * 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "button1")))
            except TimeoutException:
                pass
            try:
                self.browser.execute_script(
                    "javascript:ctl00_ContentPlaceHolder1_MultiProductSelector1.Search()")
            except Exception, e:
                t -= 1
                if t == 0:
                    logging.exception(e)
                    return False
                else:
                    continue
            try:
                table = WebDriverWait(self.browser, RockwellSpider.timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='multiResults']/table")))
            except TimeoutException:
                pass
            try:
                self.lines = table.find_elements_by_xpath("tbody/tr")
            except Exception, e:
                t -= 1
                if t == 0:
                    logging.exception(e)
                    return False
                else:
                    continue
            else:
                break
        return True

    def newbrowser(self):
        # firefox_profile="/home/iie/.mozilla/firefox/zsihlnkt.default"
        # browser=webdriver.Firefox(webdriver.FirefoxProfile(firefox_profile),None,15)
        browser = webdriver.Firefox(None, None, 15)
        browser.set_page_load_timeout(RockwellSpider.timeout)
        browser.implicitly_wait(5)
        return browser

    def parse(self, response):
        self.pattern = re.compile(".*\(.*,\'(\d*)\'")
        self.prodset = Set()
        self.errmsg = ""
        lst = []
        self.browser = self.newbrowser()
        self.url = response.url
        self.result = Set()
        if not self.loadpage(response.url):
            return

            # self.split_group() #debug
        # return self.result #debug

        lst = []
        name = []
        cnt = {}

        for i in self.lines:
            lst.append(i.get_attribute("v"))
            name.append(i.find_element_by_xpath("td").text)

        i = 0
        t = RockwellSpider.trytimes
        while i < len(lst):
            try:
                cnt[i] = (name[i], self.parse_all_products(lst[i]))
            except Exception, e:
                t -= 1
                if t == 0:
                    i = i + 1
                    t = RockwellSpider.trytimes
                    logging.log(logging.ERROR, "%d-th fetch no data", i)
                    logging.exception(e)
            else:
                i = i + 1
                t = RockwellSpider.trytimes
        logging.log(logging.INFO, "Parse %d unique products",
                    len(self.prodset))
        logging.log(logging.DEBUG, "product set %s", str(self.prodset))
        self.split_group()

        return self.result

    def group_download(self, browser):
        # WebDriverWait(self.browser,RockwellSpider.timeout).\
        # until(lambda x: \
        # x.find_element_by_id("ctl00_ContentPlaceHolder1_MultiProductSelector1DownloadsCmd")\
        #					.get_attribute("class")=="raCmd")
        #		self.browser.execute_script("javascript:MPS.FindDownloads('ctl00_ContentPlaceHolder1_MultiProductSelector1')")
        table = WebDriverWait(browser, RockwellSpider.timeout).until(EC.presence_of_element_located(
            (By.ID, "ctl00_ContentPlaceHolder1_FindDownloads1MatrixTable")))
        chkbox = table.find_elements_by_xpath(
            "tbody/tr[position()>2]/td[position()=2]/span[position()=3]")
        unfinished = ""
        for c in chkbox:
            try:
                logging.log(logging.INFO, "click:%s",
                            c.get_attribute("onclick"))
                self.noTimeoutClick(c)
            except UnexpectedAlertPresentException, e:
                for u in chkbox:
                    if u.get_attribute("state") == "0" and u.get_attribute("onclick"):
                        r = self.pattern.match(u.get_attribute("onclick"))
                        unfinished += r.expand(r"\1") + ","
                logging.log(
                    logging.INFO, "Cart is full, %s is not included", unfinished)
                print "***********************************************************"
                break

        t = RockwellSpider.trytimes
        try:
            cart = WebDriverWait(browser, RockwellSpider.timeout). \
                until(EC.presence_of_element_located((By.ID, "BreadcrumbDownloadCart")))

            ca = browser.find_element_by_xpath('//span[@id="BreadcrumbDownloadCart"]/button')
            self.noTimeoutClick(ca)
            print "************************ dian ji ***************************************"
        except WebDriverException:
            logging.log(logging.WARNING, "cart not found")
        #browser.execute_script(
         #   "javascript:Tools.ShowPopUp(null, null, null);DownloadCartSummary1.Show(this);")
        #print "************************ dian ji ***************************************"
        try:
            print "************************  try  ***************************************"
            WebDriverWait(browser, RockwellSpider.timeout). \
                until(EC.presence_of_element_located(
                (By.ID, "ctl00_DownloadCartSummary1Listing")))
            print "************************** end try ***********************************"
        except WebDriverException:
            logging.log(logging.WARNING, "cart listing not found")
            ca = browser.find_element_by_xpath('//span[@id="BreadcrumbDownloadCart"]/button')
            self.noTimeoutClick(ca)
            #browser.execute_script(
             #   "javascript:ctl00_DownloadCart1.Init();ctl00_DownloadCart1.Show()")
            WebDriverWait(browser, RockwellSpider.timeout). \
                until(EC.presence_of_element_located(
                (By.ID, "c")))
        while 1:
            try:
                print "#################### while ####################################"
                browser.execute_script(
                    "javascript:DownloadCartSummary.DownloadNow('ctl00_DownloadCartSummary1');")
                print "##################### end  while  ################################"
                #browser.find_element_by_xpath('//*[@id="ctl00_DownloadCartSummary1DownloadNowCmd"]/a')
            except WebDriverException, e:
                logging.log(logging.ERROR, "Downloadnow execute failure")
                logging.exception(e)
                raise e
            WebDriverWait(browser, RockwellSpider.timeout). \
                until(lambda x: len(x.window_handles) == 2)
            current_window = browser.current_window_handle
            for w in browser.window_handles:
                if w != browser.current_window_handle:
                    browser.switch_to.window(w)
                    break
            try:
                self.validate_page(browser)
            except WebDriverException, e:
                t -= 1
                browser.close()
                browser.switch_to.window(current_window)
                logging.log(logging.WARNING, "Validate Failure(%d)",
                            RockwellSpider.trytimes - t)
                if t == 0:
                    browser.execute_script(
                        "javascript:DownloadCartSummary.Clear('ctl00_DownloadCartSummary1');")
                    logging.exception(e)
                    raise e
            else:
                browser.close()
                browser.switch_to.window(current_window)
                WebDriverWait(browser, RockwellSpider.timeout). \
                    until(EC.presence_of_element_located(
                    (By.ID, "ctl00_DownloadCartSummary1Listing")))
                browser.execute_script(
                    "javascript:DownloadCartSummary.Clear('ctl00_DownloadCartSummary1');")
                break
        return unfinished

    def validate_page(self, browser):
        browser.set_page_load_timeout(RockwellSpider.timeout)
        try:
            acceptbtn = WebDriverWait(browser, RockwellSpider.timeout). \
                until(EC.presence_of_element_located(
                (By.ID, "ctl00_MainContent_btnAgree")))
        except TimeoutException:
            acceptbtn = browser.find_element_by_id(
                "ctl00_MainContent_btnAgree")

        self.noTimeoutClick(acceptbtn)
        try:
            directdownload = WebDriverWait(browser, RockwellSpider.timeout). \
                until(EC.presence_of_element_located(
                (By.ID, "ctl00_MainContent_btndirectdownload")))
        except TimeoutException:
            directdownload = browser.find_element_by_id(
                "ctl00_MainContent_btndirectdownload")
        self.noTimeoutClick(directdownload)
        self.getlink(browser)

    def getlink(self, browser):
        try:
            table = WebDriverWait(browser, RockwellSpider.timeout). \
                until(EC.presence_of_element_located(
                (By.ID, "IndividualItemTable")))
        except TimeoutException:
            table = browser.find_element_by_id("IndividualItemTable")
        lines = table.find_elements_by_xpath("tbody/tr/td")

        proto = MI.BasicItem()
        proto["Manufacturer"] = "Rockwell"
        #proto["Info"] = {}


        for l in lines:
            item = MI.BasicItem(proto)
            inner = l.find_element_by_xpath("table/tbody/tr/td")
            item["URL"] = inner.find_element_by_xpath(
                "a/input").get_attribute("value").strip()
            #item["Rawlink"] = item["Link"].split("?")[0].strip()
            #if item["Rawlink"].rsplit(".", 1).pop().lower() in RockwellSpider.typefilter:
             #   continue
            #item["Title"] = l.find_element_by_xpath(
             #   "span[position()=1]").text.split(":", 1).pop().strip()

            item["ProducVersion"] = l.find_element_by_xpath(
                "span[position()=2]").text.split(":", 1).pop().strip()
            item["Description"] = inner.find_element_by_xpath(
                "span[position()=1]").text.split(":", 1).pop().strip()
            item["ProducModel"] = item["URL"].split("/")[-2]

            #item["Info"]["Model"] = item["Title"].split("for")[-1].split("V")[0]
            item["FirmwareName"] = inner.find_element_by_xpath(
                "a/span").text.strip()
            item["PackedTime"] = ""
            print item
            self.result.add(item)

    def split_group(self):
        i = 0
        j = 0
        maxpage = 20
        lst = list(self.prodset)
        pagelink = "http://compatibility.rockwellautomation.com/Pages/MultiProductFindDownloads.aspx?crumb=112&refSoft=1&toggleState=&versions="

        # lst=[51223,51224,51225,51226,51227,51228,410,53253,51235,51236,51237,51238,51239,51240,51241,51242,51243,51244,51245,51246,51247,51248,51249,298,299,301,309,51220,51221,51222,51250,54490,51894,54285,53820,53329,53330,53331,51284,54491,51287,698,51897,699,51597,53359,53360,53361,53362,51219,53364,702,53366,52585,53368,52244,53370,53371,53372,52586,53374,52245,51328,51329,51330,51331,51332,51333,51334,51335,51336,50540,51338,52247,53388,706,53390,53391,53392,52248,54493,53396,52590,53398,53400,53234,53402,50543,53404,53406,53408,52592,53410,53412,51366,50545,53416,53418,711,181,182,183,184,185]
        # #debug
        browser = self.browser
        group = ""
        while i < len(lst):
            group += str(lst[i])
            i += 1
            j += 1
            if j >= maxpage or i == len(lst):
                t = RockwellSpider.trytimes
                while 1:
                    try:
                        browser.get(pagelink + group)
                    except TimeoutException:
                        pass
                    try:
                        # while not self.login():
                        # continue
                        remain = self.group_download(browser)
                    except Exception, e:
                        # raise e #debug
                        t -= 1
                        logging.log(logging.WARNING, "GroupDownloadFailure(%d):%s",
                                    RockwellSpider.trytimes - t, e.message)
                        if t == 0:
                            logging.exception(e)
                            break
                        else:
                            self.browser.quit()  # !debug
                            self.browser = self.newbrowser()
                            browser = self.browser
                            self.loadpage(self.url)
                    else:
                        self.browser.quit()
                        self.browser = self.newbrowser()
                        browser = self.browser
                        self.loadpage(self.url)
                        break
                j = remain.count(",")
                logging.log(
                    logging.INFO, "[Progress] Finished(%d/%d)", i - j, len(lst))
                # print "\n\tFINISHED(%d/%d):"%(i-j,len(lst)),group
                group = remain
            else:
                group += ","


                # while i<len(lst):
                # self.browser.execute_script("javascript:MPS.SelectVersion('ctl00_ContentPlaceHolder1_MultiProductSelector1','"+str(lst[i])+"')")
                # j+=1
                #			i+=1
                #			if j==maxpage or i==len(lst):
                #				self.group_download()
                #				if i==len(lst):
                #					break
                #				else:
                #					self.loadpage()

    def parse_all_products(self, no):
        tr = self.browser.find_element_by_xpath(
            "//div[@class='multiResults']/table/tbody/tr[@v='" + no + "']")
        key = tr.find_element_by_xpath("td").text
        cnt = 0
        self.noTimeoutClick(tr)
        col1 = self.browser.find_element_by_class_name('multiSeriesResults')
        col2 = self.browser.find_element_by_class_name(
            'multiSeriesVersionResults')
        tableTimeWait = 3
        try:
            WebDriverWait(self.browser, tableTimeWait).until(
                lambda x: col1.is_displayed() or col2.is_displayed())
        except TimeoutException:
            try:
                cont = WebDriverWait(self.browser, RockwellSpider.timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='container']/table/tbody/tr/td/img")))
            except TimeoutException:
                cont = self.browser.find_element_by_xpath(
                    "//div[@class='container']/table/tbody/tr/td/img")
            cnt += self.match(cont.get_attribute("onclick"))
            self.noTimeoutClick(cont)
            logging.log(logging.INFO, "column[0]")

        else:
            if col1.is_displayed():
                lst1 = col1.find_elements_by_xpath("table/tbody/tr")
                i = 0
                last = ""
                t = RockwellSpider.trytimes
                while i < len(lst1):
                    l = lst1[i]
                    self.noTimeoutClick(l)
                    try:
                        WebDriverWait(self.browser, tableTimeWait, 0.5, NoSuchElementException).until(
                            lambda x: not col1.is_displayed() or col2.find_element_by_xpath(
                                "table/tbody/tr").is_displayed() and col2.find_element_by_xpath(
                                "table/tbody/tr").get_attribute("onclick") != last)
                        if not col1.is_displayed():
                            cont = WebDriverWait(self.browser, RockwellSpider.timeout).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//div[@class='container']/table/tbody/tr/td/img")))
                            cnt += self.match(cont.get_attribute("onclick"))
                            self.noTimeoutClick(cont)
                            WebDriverWait(self.browser, tableTimeWait).until(EC.invisibility_of_element_located(
                                (By.XPATH, "//div[@class='container']/table/tbody/tr/td/img")))
                            if i + 1 == len(lst1):
                                break
                            self.noTimeoutClick(tr)
                            WebDriverWait(self.browser, tableTimeWait, 0.5, NoSuchElementException).until(
                                lambda x: col1.find_element_by_xpath("table/tbody/tr").is_displayed())
                            lst1 = col1.find_elements_by_xpath(
                                "//div[@class='multiSeriesResults']/table/tbody/tr")
                        else:
                            last = col2.find_element_by_xpath(
                                "table/tbody/tr").get_attribute("onclick")
                            cnt += self.product_version(
                                self.browser.find_element_by_class_name('multiSeriesVersionResults'))
                    except Exception, e:
                        t -= 1
                        if t == 0:
                            logging.exception(e)
                        continue
                    else:
                        t = RockwellSpider.trytimes
                    i += 1
                    logging.log(
                        logging.INFO, "column[1]:%d %d", len(lst1), cnt)

            elif col2.is_displayed():
                cnt += self.product_version(col2)
                logging.log(logging.INFO, "column[2]:%d", cnt)
        self.noTimeoutClick(
            self.browser.find_element_by_class_name("subheader"))
        WebDriverWait(self.browser, tableTimeWait).until_not(
            lambda x: col1.is_displayed() or col2.is_displayed())
        return cnt

    def match(self, s):
        r = self.pattern.match(s)
        if r:
            self.prodset.add(int(r.expand(r"\1")))
            logging.log(logging.INFO, "match-id:%s", r.expand(r"\1"))
            return 1
        return 0

    def product_version(self, col2):
        lines = col2.find_elements_by_xpath("table/tbody/tr")
        cnt = 0
        for tr in lines:
            cnt += self.match(tr.get_attribute("onclick"))
        return cnt
