# # encoding=utf-8
import commands

import pymongo

import settings


class DbUtil(object):
    '''
    数据库操作模块，有点乱，以后重构
    '''

    def conn(self):
        '''
        链接数据库
        :return:
        '''
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DATABASE]
        return self

    def collection(self, colName=None):
        if not colName:
            return self.db[settings.MONGO_COLLECTION]
        elif isinstance(colName, str):
            return self.db[colName]
        else:
            print "集合名字必须是字符串"
            return

    def close(self):
        self.client.close()


def url_items(name):
    db = DbUtil().conn()
    cols = db.collection('url_items').find({'name': name})
    return [str(c.get('start_urls')) for c in cols]


def all_firm():
    '''
    返回所有下载链接，下载成功链接，下载失败链接
    :return:
    '''
    col = DbUtil().conn().collection('scrapy_items')
    return (col.find({"Status": {"$gte": 0}}).count(),
            col.find({"Status": 0}).count(),
            col.find({"Status": 3}).count())


def download_process():
    '''
    返回每个厂商的爬取链接，下载链接，下载失败连接
    :return:
    '''
    all_spiders = commands.getoutput("scrapy list").split('\n')
    col = DbUtil().conn().collection('scrapy_items')
    for spider_name in all_spiders:
        spider_name = spider_name.capitalize()
        yield [spider_name,
               col.find({'Firm': spider_name, "Status": {"$gte": 0}}).count(),
               col.find({'Firm': spider_name, "Status": 0}).count(),
               col.find({'Firm': spider_name, "Status": 3}).count()]


if __name__ == '__main__':
    pass
