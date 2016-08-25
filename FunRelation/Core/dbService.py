__author__ = 'changqing'

import pymongo
import codecs
import ConfigParser

config = ConfigParser.ConfigParser()
globalconfigfile = r'../../GLOBAL_CONFIG'
config.readfp(codecs.open(globalconfigfile, "r", "utf-8"))
MONGO_URI = config.get('globalconfig',"MONGO_IP")
MONGO_PORT = int(config.get('globalconfig',"MONGO_PORT"))

config = ConfigParser.ConfigParser()
globalconfigfile = r'../CONFIG'
config.readfp(codecs.open(globalconfigfile, "r", "utf-8"))
dbName = config.get('funrelationconfig',"DB_NAME")
BugCollectionName = config.get('funrelationconfig',"BUG_COLLECTION_NAME")
TargetCollectionName = config.get('funrelationconfig','TARGET_COLLECTION_NAME')


print dbName
print BugCollectionName
print TargetCollectionName

def connectDB():
	#conn = pymongo.MongoClient(MONGO_URI, MONGO_PORT)
	#conn['test']['CQ'].insert({'name':'changqing'})
	return pymongo.MongoClient(MONGO_URI, MONGO_PORT)
