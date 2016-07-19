# -*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from mycrawler.dbUtil import download_process, all_firm
import time


def process_download():
    '''
    显示下载过程中，下载链接和未下载链接的实时变化
    :return:
    '''
    while 1:
        print '%-12s %-12s %-12s %-12s' % ("厂商", "已爬取", "已下载", "下载失败")
        pp = list(download_process())
        for p in pp[0:]:
            print '%-10s %-12s %-10s %-10s' % (p[0], p[1], p[2], p[3])

        a = all_firm()
        print '%-10s   %-12s %-10s %-10s' % ("总计:", a[0], a[1], a[2])
        sys.stdout.flush()
        time.sleep(5)
        os.system('clear')

        if a[0] == a[1]:
            print "已经下载完毕"
            break

process_download()
