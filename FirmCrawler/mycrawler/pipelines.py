# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from settings import priority


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    # classmethod注解是让from_crawler变成一个类函数，第一个参数cls为该类本身（不是对象哦）
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # db[settings['MONGODB_COLLECTION']]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        '''
        这个才是对数据操作的重要函数
        :param item:
        :param spider:
        :return:
        '''
        print "\nadd\n", item, "\ndata\n"

        # 第一步，检查优先级
        if item["Manufacturer"] in priority:
            item["Status"] = 2
        else:
            item["Status"] = 1
        # mymd5 = md5.new(item["Rawlink"].encode("utf8"))
        # item["id"] = mymd5.hexdigest()

        # 检查该连接是否已经存在于数据库
        if item["Status"] == 1:
            exist = self.db[self.mongo_collection].find_one(
                {"Manufacturer": item.get('Manufacturer'), 'URL': item.get('URL')})

            if not exist:

            # 那就更新吧，update有四个参数，很诡异
                self.db[self.mongo_collection].update(
                    {"Manufacturer": item.get('Manufacturer'), 'URL': item.get('URL')}, {"$set": item}, True)




        if item["Status"] == 2:
            exist = self.db[self.mongo_collection].find_one(
            {"Manufacturer": item.get('Manufacturer'), 'FirmwareName': item.get('FirmwareName')})
            if exist:
                if item["URL"] != exist["URL"]:
                    self.db[self.mongo_collection].update(
                    {"Manufacturer": item.get('Manufacturer'), 'FirmwareName': item.get('FirmwareName')}, {"$set": {"URL":item.get("URL")}}, True)

            if not exist:

            # 那就更新吧，update有四个参数，很诡异
                self.db[self.mongo_collection].update(
                    {"Manufacturer": item.get('Manufacturer'), 'FirmwareName': item.get('FirmwareName')}, {"$set": item}, True)

        return item
