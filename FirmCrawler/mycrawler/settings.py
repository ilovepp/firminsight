# -*- coding: utf-8 -*-

# Scrapy settings for schneider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'mycrawler'

SPIDER_MODULES = ['mycrawler.spiders']
NEWSPIDER_MODULE = 'mycrawler.spiders'

# 数据库配置，firmware为数据库名字，iie_CERT为密码，MONGODB-CR为认证机制，注意mongodb默认认证机制
# 不是MONGODB-CR，具体情况请查看，mongodb总结.doc
#MONGO_URI = "mongodb://firmware:iie_CERT@10.10.13.154:27017/firmware?authMechanism=MONGODB-CR"
#MONGO_URI = "mongodb://10.10.12.82/firmware"
#MONGO_DATABASE = "firmware"
#MONGO_COLLECTION = "scrapy_items"

#>>> from pymongo import MongoClient
#>>> client = MongoClient('example.com')
#>>> client.the_database.authenticate('user', 'password', mechanism='SCRAM-SHA-1')
#>>> uri = "mongodb://user:password@example.com/the_database?authMechanism=SCRAM-SHA-1"
#>>> client = MongoClient(uri)


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'schneider (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN=16
# CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
# COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED=False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'schneider.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'schneider.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'mycrawler.pipelines.MongoPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
# AUTOTHROTTLE_ENABLED=True
# The initial download delay
# AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED=True
# HTTPCACHE_EXPIRATION_SECS=0
# HTTPCACHE_DIR='httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES=[]
# HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

# myconfig
firmlist_fc = ["Schneider", "Rockwell", "Abb","Siemens","Vipa"]  # 定义一个工控企业队列
priority = ["Rockwell"]  # 最高优先级2，把最高优先级的厂商配置到此处


###############################################################################################
import codecs
import ConfigParser
config = ConfigParser.ConfigParser()
globalconfigfile = r'../GLOBAL_CONFIG.config'
config.readfp(codecs.open(globalconfigfile, "r", "utf-8"))
MONGO_URI = config.get('globalinfo',"MONGO_IP")
MONGO_DATABASE = config.get('globalinfo',"MONGO_DATABASE")
MONGO_COLLECTION = config.get('globalinfo',"MONGO_SCRAPY_COLLECTION_NAME")
dirs_root = config.get('globalinfo',"FIRMWARE_STORE_PATH")
#file_size = config.get('globalinfo',"")

configfile = r'./CONFIG.cfg'
config.readfp(codecs.open(configfile, "r", "utf-8"))

file_size = config.get('info',"FIRMWARES_SIZE_LIMIT")
rockwelluser = config.get('info',"ROCKWELL_CRAWL_ACCOUNT")
rockwellpwd = config.get('info',"ROCKWELL_CRAWL_PASSWORD")
