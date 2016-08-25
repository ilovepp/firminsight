# coding: UTF-8
__author__ = 'changqing'


import time
import random
from Similarity_CountSim import CountSim
from Train_MLP import *
from attr_info import attrListName,attrValueName
from dbService import connectDB


def save_data(prob,name):

    fid = open(name,'wb')
    pickle.dump(prob,fid)
    fid.close()


def get_data(name):

    f = open(name,'rb')
    result = pickle.load(f)
    f.close()
    return result


def list2dic(Feature):
    flst = {}
    for item in Feature:
        flst[item['Func_Name']] = item
    return flst


def shared_dataset(data_xy, borrow=True):

    data_x, data_y = data_xy
    shared_x = theano.shared(numpy.asarray(data_x, dtype=theano.config.floatX), borrow=borrow)
    shared_y = theano.shared(numpy.asarray(data_y, dtype=theano.config.floatX), borrow=borrow)
    return (shared_x, T.cast(shared_y, 'int32'))


def turnType(DataList,type = 0): #0 is the train type

    featureList = []
    labelList = []
    for item in DataList:
        featureList.append([item['sim_'+key] for key in attrListName + attrValueName]) # order
        labelList.append(item['Label'])

    if type:
        train_set_x, train_set_y = shared_dataset((featureList,labelList))
    # print train_set_x.type
    # print train_set_y.type
    return (train_set_x,train_set_y)


def count_sim(proFeatures1,proFeatures2,n,m,p):

    proFeaturesDic1 = list2dic(proFeatures1)
    proFeaturesDic2 = list2dic(proFeatures2)

    functionName1 = set(proFeaturesDic1)
    functionName2 = set(proFeaturesDic2)
    functionCommonName2 = functionName1 & functionName2
    # sampleNum = len(functionCommonName)//1000*1000
    # functionCommonName2 = set(random.sample(list(functionCommonName),sampleNum))
    functionName12 = set(random.sample(list(functionCommonName2),m))
    functionName13 = set(random.sample(list(functionCommonName2-functionName12),p))
    functionName11 = functionCommonName2 - functionName12 - functionName13

    flstTrain = []
    posTrainNum = 0
    for item in functionName11:

        if 1:
            d2 = proFeaturesDic2[item]
            d1 = proFeaturesDic1[item]
            dList = random.sample(list(set(functionName2)-set([item])),n)

            eachSim = CountSim(d1,d2)
            eachSim.countLabel()
            flstTrain.append(eachSim.sim)

            for name in dList:
                d3 = proFeaturesDic2[name]
                eachSim = CountSim(d1,d3)
                eachSim.countLabel()
                flstTrain.append(eachSim.sim)

            posTrainNum += 1

        #except:
         #   continue

    negTrainNum = len(flstTrain)-posTrainNum


    flstValid = []
    posValidNum = 0
    for item in functionName12:
        try:
            d2 = proFeaturesDic2[item]
            d1 = proFeaturesDic1[item]
            dList = random.sample(list(set(functionName2)-set([item])),n)

            eachSim = CountSim(d1,d2)
            eachSim.countLabel()
            flstValid.append(eachSim.sim)

            for name in dList:
                d3 = proFeaturesDic2[name]
                eachSim = CountSim(d1,d3)
                eachSim.countLabel()
                flstValid.append(eachSim.sim)

            posValidNum += 1
        except:
            continue

    negValidNum = len(flstValid)-posValidNum


    flstTest = []
    posTestNum = 0
    for item in functionName13:
        try:
            d2 = proFeaturesDic2[item]
            d1 = proFeaturesDic1[item]
            dList = random.sample(list(set(functionName2)-set([item])),n)

            eachSim = CountSim(d1,d2)
            eachSim.countLabel()
            flstTest.append(eachSim.sim)

            for name in dList:
                d3 = proFeaturesDic2[name]
                eachSim = CountSim(d1,d3)
                eachSim.countLabel()
                flstTest.append(eachSim.sim)

            posTestNum += 1
        except:
            continue

    negTestNum = len(flstTest)-posTestNum

    # print 'The Train Set,p,n and all: ', posTrainNum, negTrainNum, len(flstTrain)
    # print 'The Valid Set,p,n and all: ', posValidNum, negValidNum, len(flstValid)
    # print 'The Test Set,p,n and all: ', posTestNum, negTestNum, len(flstTest)

    return flstTrain,flstValid,flstTest


def prepareData(FeatureTuple=(),flag = 0):

    # print '... count the similar'
    time1= time.time()
    simFeaturesTrain = []
    simFeaturesValid = []
    simFeaturesTest = []
    for i,j in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]:
        # print
        # print 'The Train ID: ',i,j
        simFeaturesTrain1, simFeaturesValid1, simFeaturesTest1 = count_sim(FeatureTuple[i],FeatureTuple[j],10,200,200)
        simFeaturesTrain.extend(simFeaturesTrain1)
        simFeaturesValid.extend(simFeaturesValid1)
        simFeaturesTest.extend(simFeaturesTest1)
    time2 = time.time()
    # print 'Time: ',time2-time1
    # print

    #print len(simFeaturesTrain),len(simFeaturesValid),len(simFeaturesTest)

    trainData = turnType(simFeaturesTrain,type = 1)
    validData = turnType(simFeaturesValid,type = 1)
    testData = turnType(simFeaturesTest,type = 1)

    if flag:
        save_data(trainData, name = 'trainData.data')
        save_data(validData, name = 'validData.data')
        save_data(testData, name = 'testData.data')
        #save_data(testData[0],name = '/home/changqing/Desktop/code/data/preData.data')
        #save_data(testData[1],name = '/home/changqing/Desktop/code/data/preLabel.data')
    return trainData,validData,testData


def main(Train_collectionName = 'train', Train_dbName = 'Analyse',pathfile = ',,/TrainBinary',idaengine = '../../IDAPro/idal64',\
         plugpath = '../Plug_Train.py'):
    # pathfile = '/home/changqing/Desktop/BugSearch/TrainBinary'
    # idaengine = '/home/changqing/IDAPro/idal64'
    # plugpath = '/home/changqing/Desktop/BugSearch/Plug_Train.py'
    #
    # for parent,dirnames,filenames in os.walk(pathfile):
    #     for filename in filenames:
    #         print filename
    #         binaryPath = os.path.join(parent,filename)
    #         os.system("%s -B %s"%(idaengine,binaryPath))
    #         binaryI64Path = binaryPath+'.i64'
    #         if os.path.exists(binaryI64Path):
    #             os.system("%s -A -S'%s %s' %s"%(idaengine,plugpath, Train_dbName, binaryI64Path))
    #         try:
    #             os.system("rm %s"%(binaryPath+'.id0'))
    #             os.system("rm %s"%(binaryPath+'.id1'))
    #             os.system("rm %s"%(binaryPath+'.asm'))
    #             os.system("rm %s"%(binaryPath+'.nam'))
    #             os.system("rm %s"%(binaryPath+'.til'))
    #             os.system("rm %s"%(binaryPath+'.i64'))
    #         except:
    #             pass


    conn = connectDB()

    collection0 = "busybox-mips-O0"
    collection1 = "busybox-mips-O1"
    collection2 = "busybox-mips-O2"
    collection3 = "busybox-mips-O3"
    Feature0 = list(conn[Train_dbName][Train_collectionName].find({'Firmware_ID':collection0}))
    Feature1 = list(conn[Train_dbName][Train_collectionName].find({'Firmware_ID':collection1}))
    Feature2 = list(conn[Train_dbName][Train_collectionName].find({'Firmware_ID':collection2}))
    Feature3 = list(conn[Train_dbName][Train_collectionName].find({'Firmware_ID':collection3}))

    if len(Feature0)*len(Feature1)*len(Feature2)*len(Feature3):
        trainData,validData,testData = prepareData((Feature0,Feature1,Feature2,Feature3))

        print
        print '... MLP'
        test_mlp((trainData,validData,testData))




if __name__ == "__main__":
    time1 = time.time()
    main()
    time2 = time.time()
    print 'Time: ', time2 - time1