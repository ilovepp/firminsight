# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 13:51:49 2015

@author: byfeelus
"""

# print dict([bb.split(' ') for bb in "111 eee;222 rrrr;333 ffff".split(';')])
# print not 0

# print 'ewdf&&namenjhcbas**'.find('name11')
# print len('text/html'.split(';'))
#
# print
# "http://www.ad.siemens.com.cn/service/search/Default.aspx?kw=%u56FA%u4EF6&searchType=8&filter=1&ov=%u56FA%u4EF6&sort=&order=desc&searchInR=0&pageIndex=$$&dc_types=5".replace('$$',str(1))

import os
import urllib2


header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}

for x in os.walk('.'):
    pass
    # print x
# print os.walk('.').next()
print isinstance([1, 2], list)


def get_url_info(self, url):
    res = urllib2.urlopen(urllib2.Request(url, None, header))
    content_type = res.headers.get('content-type').split(r';')
    if len(content_type) == 1:
        return (content_type[0].split(r'/')[-1], None)
    else:
        c_n = [x.split("name=").pop().strip('"')
               for x in content_type[1:] if x.find('name=') != -1]
        if not len(c_n):
            return (content_type[0].split(r'/')[-1], None)
        return (content_type[0].split(r'/')[-1], c_n.pop())


        # # 使用多线程
        # import threadpool
        # while collection.find({'Status': 2}).count() > 0:
        # print "下载低优先级"
        # tpool = threadpool.ThreadPool(10)
        # requests = threadpool.makeRequests(
        # download_url, collection.find({'Status': 2}))
        # [tpool.putRequest(req) for req in requests]
        # tpool.wait()
        # print "优先级低的下载完毕"
        # print "所有下载完毕"
        # 是否filename这个绝对路径，没有的话新建，并打开
        # urllib.urlretrieve(mylink, filename, callbackfunc)
        # with open(filename, "ab+") as foo:
        # for f in response.readlines():
        # sys.stdout.write(".")
        # foo.write(f)  # 把str中的内容写进filename这个文件夹中


        # response = urllib2.urlopen(urllib2.Request(
        # mylink, None, header), timeout=30)  # 回复超过十秒超时
        # 根据response header中的“content-length"判断文件大小

        # if response.headers.has_key("content-length"):
        # # 判断文件是否大于100m，大于的话，舍弃不下载
        # size = int(response.headers["content-length"])
        # if size >= file_size:
        # collection.remove({"_id": ids})
        # return

        # print "开始下载", name

        # cur = collection.find({'Status': 1})
        # a = cur.count()
        # print a
        # i = 0
        # for i in range(0, a):
        #     print i
        #     if (cur[i].has_key('Link')):
        #         # print  "have link"

        #         # print mylink
        #         if (cur[i].has_key('Firm')):

        #             # print firmname
        #             if(cur[i].has_key('Filename')):
        #                 name = cur[i]['Filename']
        #                 print "all count is  %s" % a
        #                 print "now is %s" % i
        #                 print name
        #                 mylink = cur[i]['Link']
        #                 print mylink
        #                 firmname = cur[i]['Firm']
        #                 ids = cur[i]["_id"]

        #                 dirs = dirs_root + "%s" % firmname
        #                 if os.path.exists(dirs) == False:
        #                     os.makedirs(dirs)
        #                 # else:
        #                 #	print"have this folder "
        #                 filename = dirs + "/" + name
        #                 print filename

        #                 if os.path.exists(filename) == False:
        #                     #foo1 =open(filename,'w')
        #                     #threadpool foo1.close()
        #                     request = urllib2.Request(mylink, None, header)
        #                     # response=requests.get(mylink)
        #                     try:
        #                         response = urllib2.urlopen(request)
        #                         try:
        #                             # response=requests.get(mylink)
        #                             Size = response.headers["content-length"]
        #                             Size = int(Size)
        #                             print Size
        #                             if Size < 104857600:
        #                                 str = response.read()
        #                                 print "下载"
        #                                 print name
        #                                 print mylink
        #                                 foo = open(filename, "wb")
        #                                 foo.write(str)
        #                                 print "下载成功"
        #                                 print "\n"
        #                                 foo.close()
        #                                 if firmname in firmlist_fc:
        #                                     print "It  is   FactoryControl_firm"
        #                                     collection.update({'_id': ids}, {
        #                                                       "$set": {'Path': filename, 'Status': 0, 'Firmtype': 'FactoryControl'}})
        #                                 else:
        #                                     collection.update({'_id': ids}, {
        #                                                       "$set": {'Path': filename, 'Status': 0, 'Firmtype': 'Not_FactoryControl'}})

        #                             else:
        #                                 collection.remove({"_id": ids})
        #                                 print " remove  success!"
        #                         except:
        #                             print"no Size"
        #                             str = response.read()
        #                             print "下载"
        #                             print name
        #                             print mylink
        #                             foo = open(filename, "wb")
        #                             foo.write(str)
        #                             print "下载成功"
        #                             print "\n"
        #                             foo.close()
        #                             if firmname in firmlist_fc:
        #                                 print "It  is   FactoryControl_firm"
        #                                 collection.update({'_id': ids}, {
        #                                                   "$set": {'Path': filename, 'Status': 0, 'Firmtype': 'FactoryControl'}})
        #                             else:
        #                                 collection.update({'_id': ids}, {
        #                                                   "$set": {'Path': filename, 'Status': 0, 'Firmtype': 'Not_FactoryControl'}})

        #                     except Exception, e:
        #                         print e
        #                 else:
        #                     print "file path is" + filename
        #                     collection.update({'_id': ids}, {
        #                                       "$set": {'Path': filename, 'Status': 0, 'Firmtype': 'FactoryControl'}})
        #             else:
        #                 print "no Filename"
        #         else:
        #             print "no Firm"
        #     else:
        #         print "no link"

        # print "low status download over"


        # print "ALL FIRMWARE  DOWMLOAD OVER"


# print "Status:1"
# import threadpool
#
# tpool = threadpool.ThreadPool(5)
# requests = threadpool.makeRequests(
# download_url,
# list(collection.find({'Status': 1})), 5)
# [tpool.putRequest(req) for req in requests]
# tpool.wait()


# !/usr/bin/python
# -*- coding: utf-8 -*-
# filename: paxel.py
# FROM: http://jb51.net/code/view/58/full/
# Jay modified it a little and save for further potential usage.

'''It is a multi-thread downloading tool

    It was developed following axel.
        Author: volans
        E-mail: volansw [at] gmail.com
'''

import sys
import os
import time
import urllib
from threading import Thread

# in case you want to use http_proxy
local_proxies = {'http': 'http://131.139.58.200:8080'}


class AxelPython(Thread, urllib.FancyURLopener):
    '''Multi-thread downloading class.

        run() is a vitural method of Thread.
    '''

    def __init__(self, threadname, url, filename, ranges=0, proxies={}):
        Thread.__init__(self, name=threadname)
        urllib.FancyURLopener.__init__(self, proxies)
        self.name = threadname
        self.url = url
        self.filename = filename
        self.ranges = ranges
        self.downloaded = 0

    def run(self):
        '''vertual function in Thread'''
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            #print 'never downloaded'
            self.downloaded = 0

        # rebuild start poind
        self.startpoint = self.ranges[0] + self.downloaded

        # This part is completed
        if self.startpoint >= self.ranges[1]:
            print 'Part %s has been downloaded over.' % self.filename
            return

        self.oneTimeSize = 16384  # 16kByte/time
        print 'task %s will download from %d to %d' % (self.name, self.startpoint, self.ranges[1])

        self.addheader("Range", "bytes=%d-%d" % (self.startpoint, self.ranges[1]))
        self.urlhandle = self.open(self.url)

        data = self.urlhandle.read(self.oneTimeSize)
        while data:
            filehandle = open(self.filename, 'ab+')
            filehandle.write(data)
            filehandle.close()

            self.downloaded += len(data)
            #print "%s" % (self.name)
            #progress = u'\r...'

            data = self.urlhandle.read(self.oneTimeSize)


def GetUrlFileSize(url, proxies={}):
    urlHandler = urllib.urlopen(url, proxies=proxies)
    headers = urlHandler.info().headers
    length = 0
    for header in headers:
        if header.find('Length') != -1:
            length = header.split(':')[-1].strip()
            length = int(length)
    return length


def SpliteBlocks(totalsize, blocknumber):
    blocksize = totalsize / blocknumber
    ranges = []
    for i in range(0, blocknumber - 1):
        ranges.append((i * blocksize, i * blocksize + blocksize - 1))
    ranges.append((blocksize * (blocknumber - 1), totalsize - 1))

    return ranges


def islive(tasks):
    for task in tasks:
        if task.isAlive():
            return True
    return False


def paxel(url, output, blocks=6, proxies=local_proxies):
    ''' paxel
    '''
    size = GetUrlFileSize(url, proxies)
    ranges = SpliteBlocks(size, blocks)

    threadname = ["thread_%d" % i for i in range(0, blocks)]
    filename = ["tmpfile_%d" % i for i in range(0, blocks)]

    tasks = []
    for i in range(0, blocks):
        task = AxelPython(threadname[i], url, filename[i], ranges[i])
        task.setDaemon(True)
        task.start()
        tasks.append(task)

    time.sleep(2)
    while islive(tasks):
        downloaded = sum([task.downloaded for task in tasks])
        process = downloaded / float(size) * 100
        show = u'\rFilesize:%d Downloaded:%d Completed:%.2f%%' % (size, downloaded, process)
        sys.stdout.write(show)
        sys.stdout.flush()
        time.sleep(0.5)

    filehandle = open(output, 'wb+')
    for i in filename:
        f = open(i, 'rb')
        filehandle.write(f.read())
        f.close()
        try:
            os.remove(i)
            pass
        except:
            pass

    filehandle.close()


if __name__ == '__main__':
    # url = 'http://support1.toshiba-tro.de/tedd-files2/0/frmwre-20071005144441.zip'
    # output = 'frmwre-20071005144441.zip'
    # paxel(url, output, blocks=4, proxies={})
    a = "TL-AP300I-PoE V3.0_150804标准版"
    import re
    m = re.split(r'\w*', a)[-1]
    print a.replace(m,"")

    print {'1':1,"2":11}.viewkeys()

    # # global lock
    # lock = threading.Lock()
    #
    #
    # # default parameters
    # defaults = dict(
    #     thread_count=10,
    #     buffer_size=50 * 1024 * 1024,
    #     block_size=1000 * 1024)
    #
    #
    # def progress(percent, width=50):
    #     print "%s %d%%\r" % (('%%-%ds' % width) % (width * percent / 100 * '='), percent),
    #     if percent >= 100:
    #         print
    #         sys.stdout.flush()
    #
    #
    # def write_data(filepath, data):
    #     with open(filepath, 'wb') as output:
    #         cPickle.dump(data, output)
    #
    #
    # def read_data(filepath):
    #     with open(filepath, 'rb') as output:
    #         return cPickle.load(output)
    #
    #
    # FileInfo = namedtuple('FileInfo', 'url name size lastmodified')
    #
    #
    # def get_file_info(cur):
    #     trytimes = 3
    #     while trytimes > 0:
    #         try:
    #             res = urllib2.urlopen(urllib2.Request(
    #                 cur['Link'], None, header), timeout=10)
    #             size = int(res.headers.get('content-length', 0))
    #
    #             # 判断文件是否大于100m，大于的话，舍弃不下载
    #             if size >= file_size:
    #                 collection.update(
    #                     {{"_id": cur['_id']}, {"$set": {'Status': 3}}}, True)
    #                 # collection.remove({"_id": cur['_id']})
    #                 return
    #
    #             lastmodified = res.headers.get('last-modified', '')
    #             return FileInfo(cur['Link'],
    #                             os.path.join(dirs_root,
    #                                          cur['Firm'],
    #                                          cur['Filename']), size, lastmodified)
    #         except Exception, e:
    #             print e
    #             trytimes -= 1
    #     else:
    #         collection.update(
    #             {{"_id": cur['_id']}, {"$set": {'Status': 3}}}, True)
    #
    #
    # def download(cur,
    #              thread_count=defaults['thread_count'],
    #              buffer_size=defaults['buffer_size'],
    #              block_size=defaults['block_size']):
    #     # get latest file info
    #
    #     # print cur
    #     print "block_size", block_size
    #     trytime = 3
    #     while trytime > 0:
    #         try:
    #             rep = urllib2.urlopen(urllib2.Request(cur['Link'], None, header), timeout=10)  # 回复超过十秒超时
    #             print "code", rep.code
    #             break
    #         except Exception, e:
    #             print e
    #             trytime -= 1
    #             print "下载", cur['Filename']
    #             print "超时次数：%d" % (3 - trytime)
    #     else:
    #         collection.update(
    #             {{"_id": cur['_id']}, {"$set": {'Status': 3}}}, True)
    #         return
    #
    #     file_info = get_file_info(cur)
    #     print "file_info.size", file_info.size
    #     if not file_info:
    #         return
    #     # init path
    #     output = file_info.name
    #     workpath = '%s.ing' % output
    #     infopath = '%s.inf' % output
    #
    #     # split file to blocks. every block is a array [start, offset, end],
    #     # then each greenlet download filepart according to a block, and
    #     # update the block' offset.
    #     blocks = []
    #
    #     if os.path.exists(infopath):
    #         # load blocks
    #         print "ti qu wen jian:", infopath
    #         _x, blocks = read_data(infopath)
    #         print "blocks is ", blocks
    #         if (_x.url != file_info.url or
    #                     _x.name != file_info.name or
    #                     _x.lastmodified != file_info.lastmodified):
    #             print "blocks is 0"
    #             blocks = []
    #         print "ti qu wen jian wan bi"
    #
    #     if not len(blocks):
    #         # set blocks
    #         if block_size > file_info.size:
    #             blocks = [[0, 0, file_info.size]]
    #         else:
    #             block_count, remain = divmod(file_info.size, block_size)
    #             blocks = [[i * block_size, i * block_size,
    #                        (i + 1) * block_size - 1] for i in range(block_count)]
    #             blocks[-1][-1] += remain
    #         # create new blank workpath
    #         with open(workpath, 'wb') as fobj:
    #             fobj.write('')
    #
    #     # start monitor
    #     threading.Thread(target=_monitor, args=(
    #         infopath, file_info, blocks)).start()
    #
    #     print "开始下载", file_info.name
    #     with open(workpath, 'rb+') as fobj:
    #         args = [(file_info.url, blocks[i], fobj, buffer_size)
    #                 for i in range(len(blocks)) if blocks[i][1] < blocks[i][2]]
    #         print "fen pian", len(args)
    #
    #         if thread_count > len(args):
    #             thread_count = len(args)
    #
    #         pool = ThreadPool(thread_count)
    #         pool.map(_worker, args)
    #         pool.close()
    #         pool.join()
    #         print "完成下载", file_info.name
    #     print "完成下载", file_info.name
    #
    #     try:
    #         # rename workpath to output
    #         if os.path.exists(output):
    #             os.remove(output)
    #
    #         # delete infopath
    #         if os.path.exists(infopath):
    #             os.remove(infopath)
    #         os.rename(workpath, output)
    #
    #         if not all([block[1] >= block[2] for block in blocks]):
    #             return
    #     except Exception, e:
    #         print e
    #         return
    #
    #     return True
    #
    #
    # def _worker((url, block, fobj, buffer_size)):
    #     trytimes = 3
    #     while trytimes > 0:
    #         try:
    #             req = urllib2.Request(url, None, header)
    #             req.headers['Range'] = 'bytes=%s-%s' % (block[1], block[2])
    #             res = urllib2.urlopen(req)
    #
    #             chunk = res.read(buffer_size)
    #             if not chunk:
    #                 break
    #             with lock:
    #                 fobj.seek(block[1])
    #                 fobj.write(chunk)
    #                 block[1] += len(chunk)
    #         except Exception, e:
    #             print e
    #             trytimes -= 1
    #
    #
    # def _monitor(infopath, file_info, blocks):
    #     while 1:
    #         with lock:
    #             percent = sum([block[1] - block[0]
    #                            for block in blocks]) * 100 / file_info.size
    #             progress(percent)
    #             if percent >= 100:
    #                 break
    #             write_data(infopath, (file_info, blocks))
    #         time.sleep(5)