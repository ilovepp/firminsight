# -*- coding: UTF-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# 关于这个，请查看  --  爬虫说明文档.doc
class BasicItem(scrapy.Item):
    id = scrapy.Field()
    Manufacturer = scrapy.Field()
    Title = scrapy.Field()
    URL = scrapy.Field()
    Rawlink = scrapy.Field()
    FirmwareName = scrapy.Field()
    Description = scrapy.Field()
    Info = scrapy.Field()
    Status = scrapy.Field()
    need_login = scrapy.Field()
    Release_time = scrapy.Field() #后面加
    PackedTime = scrapy.Field()
    PublishTime = scrapy.Field()
    ProductModel = scrapy.Field()
    ProductVersion = scrapy.Field()
    ProductClass = scrapy.Field()
