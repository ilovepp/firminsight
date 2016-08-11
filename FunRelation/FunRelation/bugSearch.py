# -*- coding: UTF-8 -*-
import sys
import time
import os
from Similarity_CountSim import CountSim
from Predict_Net import prediction
from attr_info import attrListName,attrValueName
import codecs
import ConfigParser
import json

config = ConfigParser.ConfigParser()
globalconfigfile = r'../CONFIG'
config.readfp(codecs.open(globalconfigfile, "r", "utf-8"))
idaenginePath = config.get('funrelationconfig',"IDA_PATH")
thre = float(config.get('funrelationconfig',"THRESHOLD"))
BugPlugPath = config.get('funrelationconfig',"BUG_PLUG_PATH")
TargetPlugPath = config.get('funrelationconfig',"TARGET_PLUG_PATH")


def count_predSim(BugFunctionList,FirmFunctionList):
	flst = []
	for  BugItem in BugFunctionList:
		for FirmItem in FirmFunctionList:
			eachSim = CountSim(BugItem,FirmItem) # order is import
			eachSim.countLabel()
			flst.append(eachSim.sim)
	return flst


#generate the form data
def count_formData(predSim):
	featureList =[]
	labelList = []
	try:
		for item2 in predSim:
			featureList.append([item2['sim_' + key] for key in attrListName + attrValueName])
			labelList.append(item2['Label'])
	except:
		for item2 in predSim:
			featureList.append([item2['sim_' + key] for key in attrListName + attrValueName])
		labelList = [0.0] * len(predSim)
	return featureList, labelList


def readJson(addr):
	info = []
	fin = open(addr,'r')
	for eachLine in fin:
		line = eachLine.strip().decode('utf-8')
		line = line.strip(',')
		js = None
		js = json.loads(line)
		info.append(js)
	fin.close()
	return info


def main():

	TargetBinaryPath = sys.argv[1]
	BugBinaryPath = sys.argv[2]
	BugName = sys.argv[3]

	analyseFlag = BugBinaryPath[-4:]=='.i64' and TargetBinaryPath[-4:]=='.i64'


	if analyseFlag:
		BugId0Path = BugBinaryPath[:-4]+'.id0'
		BugId1Path = BugBinaryPath[:-4]+'.id1'
		BugNamPath = BugBinaryPath[:-4]+'.nam'
		BugTilPath = BugBinaryPath[:-4]+'.til'

		if os.path.exists(BugId0Path):
			os.system("rm %s"%(BugId0Path))
		if os.path.exists(BugId1Path):
			os.system("rm %s"%(BugId1Path))
		if os.path.exists(BugNamPath):
			os.system("rm %s"%(BugNamPath))
		if os.path.exists(BugTilPath):
			os.system("rm %s"%(BugTilPath))

		#
		# if os.path.exists(idaenginePath):
		# 	print "idaenginePath"
		# 	print idaenginePath
		# if os.path.exists(BugPlugPath):
		# 	print "BugPlugPath"
		# 	print BugPlugPath
		# if os.path.exists(BugBinaryPath):
		# 	print "BugBinaryPath"
		# 	print BugBinaryPath
		# if os.path.exists(TargetBinaryPath):
		# 	print "TargetBinaryPath"
		# 	print TargetBinaryPath
		# if os.path.exists(TargetPlugPath):
		# 	print "TargetPlugPath"
		# 	print TargetPlugPath
		# print BugName


		os.system("%s -A -S'%s %s ' %s"%( idaenginePath, BugPlugPath, BugName, BugBinaryPath))

		if os.path.exists(BugId0Path):
			os.system("rm %s"%(BugId0Path))
		if os.path.exists(BugId1Path):
			os.system("rm %s"%(BugId1Path))
		if os.path.exists(BugNamPath):
			os.system("rm %s"%(BugNamPath))
		if os.path.exists(BugTilPath):
			os.system("rm %s"%(BugTilPath))

		TargetId0Path = TargetBinaryPath[:-4]+'.id0'
		TargetId1Path = TargetBinaryPath[:-4]+'.id1'
		TargetNamPath = TargetBinaryPath[:-4]+'.nam'
		TargetTilPath = TargetBinaryPath[:-4]+'.til'

		if os.path.exists(TargetId0Path):
			os.system("rm %s"%(TargetId0Path))
		if os.path.exists(TargetId1Path):
			os.system("rm %s"%(TargetId1Path))
		if os.path.exists(TargetNamPath):
			os.system("rm %s"%(TargetNamPath))
		if os.path.exists(TargetTilPath):
			os.system("rm %s"%(TargetTilPath))

		os.system("%s -A -S'%s' %s"%( idaenginePath, TargetPlugPath,TargetBinaryPath))

		if os.path.exists(TargetId0Path):
			os.system("rm %s"%(TargetId0Path))
		if os.path.exists(TargetId1Path):
			os.system("rm %s"%(TargetId1Path))
		if os.path.exists(TargetNamPath):
			os.system("rm %s"%(TargetNamPath))
		if os.path.exists(TargetTilPath):
			os.system("rm %s"%(TargetTilPath))
		
		BugFunctionList = []
		TargetFunctionList = []

		if os.path.exists('bug.json'):
			BugFunctionList = readJson('bug.json')

		if os.path.exists('target.json'):
			TargetFunctionList = readJson('target.json')

		predSimList = []
		probList = []

		if len(BugFunctionList) != 0 and len(TargetFunctionList) != 0:
			predSimList = count_predSim(BugFunctionList, TargetFunctionList)# order is import
			featureList,labelList = count_formData(predSimList)
			probList = prediction(featureList,labelList)



		result = {}
		for i in range(len(probList)):
			if probList[i] >= thre:
				result[predSimList[i]['Func_Name_target']] = probList[i]

		os.system("rm bug.json")
		os.system("rm target.json")

		fout = open('result.json', 'w')
		outStr = json.dumps(result, ensure_ascii=False)
		fout.write(outStr.strip().encode('utf-8') + '\n')


def main2():
	fin = open('result.json','r')
	for eachLine in fin:
		resultDic = json.loads(eachLine)
		print resultDic
	fin.close()

if __name__ == "__main__":
	main2()



