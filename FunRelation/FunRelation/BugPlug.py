# -*- coding: UTF-8 -*-
#! /usr/bin/env python


import time
import math
from sets import Set
import sys
#while '/home/changqing/miniconda2/lib/python2.7/site-packages/myHashlib' in sys.path:
#    sys.path.remove('/home/changqing/miniconda2/lib/python2.7/site-packages/myHashlib')
#while '/home/changqing/miniconda2/lib/python2.7/site-packages' in sys.path:
#    sys.path.remove('/home/changqing/miniconda2/lib/python2.7/site-packages')
#sys.path.append('/home/changqing/miniconda2/lib/python2.7/site-packages/myHashlib')
#sys.path.append('/home/changqing/miniconda2/lib/python2.7/site-packages')
#import pymongo
# import idc
# from idaapi import *
# import idascript
from bson.objectid import ObjectId
from collections import Counter
#from dbService import connectDB
from attr_info import attrName,attrListName,attrValueName,attrValueNameJmp
#from dbService import dbName,BugCollectionName,TargetCollectionName
import json

class funAnalyzer(object):
    #	Analyze a specific function. func_ea must be the start addr.

    def __init__(self, fun):
        self.__func = fun
        self.__cfgNodes = {}
        self.cfgEdges = Set()
        self.strRef = Set()
        self.allInst = {}
        self.callTo = Set()
        self.callFrom = Set()
        self.block = []
        self.oriCfg = Set()
        self.attr = {}

        for i in attrValueName + attrValueNameJmp:
            self.attr[i] = 0.0
        for i in attrListName:
            self.attr[i] = []

        inf = get_inf_structure()
        self.attr["Compiler"] = get_compiler_name(inf.cc.id)
        self.attr["Processor"] = get_idp_name()


    def startAnalyze(self):
        self.attr["Func_Addr"] = self.__func.startEA
        self.attr["Func_Name"] = str(GetFunctionName(self.__func.startEA))
        self.attr["Func_CodeSize"] = self.__func.size()
        self.attr["Func_FrameSize"] = GetFrameSize(self.__func.startEA)
        self.cfgIn = Set([self.__func.startEA])
        self.cfgOut = Set([])
        self.alzInst()
        self.secAnalyze()
        self.findCaller()
        self.attr["Func_CallToNums"] = len(self.callTo)
        return self.attr


    def findCaller(self):
        for r in CodeRefsTo(self.__func.startEA, 0):
            if not func_contains(self.__func, r):
                self.attr["Func_CallToTimes"] += 1
                f = get_func(r) # the api has a bug for error-2
                if f:
                    self.callTo.add(f.startEA)

    def alzInst(self):
        func = self.__func
        it = func_item_iterator_t(func)
        t = True
        while (t):
            ea = it.current()
            hasInternal = False
            blk = xrefblk_t()
            i = blk.first_from(ea, XREF_ALL)
            while (i):
                ref = blk.to
                if blk.type == dr_O:
                    seg = getseg(blk.to)
                    if seg and seg.type == SEG_DATA and seg.perm == SEGPERM_READ:
                        # stype=GetStringType(blk.to)
                        dstr = GetString(blk.to)
                        if dstr and len(dstr) > 4:  # at least 4 chars
                            try:
                                self.strRef.add(dstr.decode('utf8'))
                            except UnicodeDecodeError:
                                #print "%x" % blk.to, dstr
                                pass
                elif blk.type in [fl_CN, fl_CF]:
                    self.attr["Func_CallFromTimes"] += 1
                    self.callFrom.add(ref)
                if blk.type in [fl_JN, fl_JF]:
                    self.attr["Func_Jmp"] += 1
                    #	Build CFG
                    if func_contains(func, ref):
                        hasInternal = True
                        if isFlow(GetFlags(ref)):
                            self.__makecfg(PrevHead(ref, get_fchunk(ref).startEA), ref)
                        # print "Lin1:%x %x" % (PrevHead(ref,get_fchunk(ref).startEA),ref)
                        if ph.id == PLFM_MIPS:
                            self.__makecfg(NextHead(ea), ref)
                        # print "Lin2:%x %x"%(NextHead(ea),ref)
                        else:
                            self.__makecfg(ea, ref)
                            #							print "Lin2:%x %x"%(ea,ref)
                i = blk.next_from()
            self.attr["Func_InstSize"] += 1
            # Entropy
            inst = ua_mnem(ea)
            if self.allInst.has_key(inst):
                self.allInst[inst] += 1
            else:
                self.allInst[inst] = 1

            t = it.next_code()
            if hasInternal and t:
                next_ea = it.current()
                if ph.id == PLFM_MIPS:
                    t2 = it.next_code()
                    if t2 and isFlow(GetFlags(it.current())):
                        self.__makecfg(next_ea, it.current())
                    # print "Lin3:%x %x"%(next_ea,it.current())
                    it.set(func, next_ea)
                else:
                    if isFlow(GetFlags(next_ea)):
                        self.__makecfg(ea, next_ea)
                        #						print "Lin3:%x %x"%(ea,next_ea)
        per = 0.0
        for key in self.allInst:
            per = self.allInst[key] / self.attr["Func_InstSize"]
            self.attr["Func_AllEtp"] -= per * math.log(per)
        per = 0.0
        for key in attrValueNameJmp:
            if self.attr[key]:
                per = self.attr[key] / self.attr["Func_InstSize"]
                self.attr["Func_Entropy"] -= per * math.log(per)


        #rebuild
    def edgeMap(self,a):
        m = len(self.block)
        for i in range(0,m-1):
            if self.block[i]<=a and a<self.block[i+1]:
                return self.block[i]
        return self.block[m-1]


    def rebuildEdge(self):
        self.reOriCfg = []#edge for first change based on block
        self.toPoint = {} #outDegree
        self.fromPoint = {}# inDegree
        for i in self.block:
            self.toPoint[i] = []
            self.fromPoint[i] = []
        for edge in self.oriCfg:
            start = self.edgeMap(edge[0])
            end = self.edgeMap(edge[1])
            self.reOriCfg.append([start,end])
            self.toPoint[start].append(end)
            self.fromPoint[end].append(start)

    def rebuildCfg(self):
        self.rebuildEdge()
        i = 0
        while(i != len(self.block)-1):
            p1 = self.block[i]
            p2 = self.block[i+1]
            if self.toPoint[p1] == []:
                if self.fromPoint[p2] == []:
                    #merge
                    self.toPoint[p1].extend(self.toPoint[p2])
                    for k in self.toPoint[p2]:
                        self.fromPoint[k] = [p1 if x == p2 else x for x in self.fromPoint[k]]
                    del self.toPoint[p2]
                    del self.fromPoint[p2]
                    self.block.remove(p2)
                    i -= 1
                else:
                    #connect
                    self.toPoint[p1].append(p2)
                    self.fromPoint[p2].append(p1)
            i += 1

        self.reCfg = Set()
        for i in self.toPoint.keys():
            try:
                for j in self.toPoint[i]:
                    self.reCfg.add((i,j))
            except:
                continue
        self.reCfg = list(self.reCfg)


    def secAnalyze(self):
        self.attr["Func_CallFromNums"] = len(self.callFrom)
        self.attr["Func_StrList"] = list(self.strRef)
        self.attr["Func_StrSize"] = len(self.attr["Func_StrList"])
        for i in attrValueNameJmp:
            self.attr[i + "p"] = self.attr[i] / self.attr["Func_InstSize"]
        self.oriCfg = list(self.cfgEdges)
        self.block = self.count_bbList()
        self.rebuildCfg()
        self.attr['Func_Node'] = len(self.block)
        self.attr['Func_Edge'] = len(self.reCfg)
        if self.attr['Func_Edge'] != 0.0:
            self.attr['Func_Density'] = self.countDensity()
            self.countMatrix()
            self.attr['Func_InDegree'] = self.count_numpy_row_sum(self.dA)
            self.attr['Func_InDegree'].sort()
            self.attr['Func_OutDegree'] = self.count_numpy_line_sum(self.dA)
            self.attr['Func_OutDegree'].sort()
            self.attr['Func_AllDegree'] = self.count_numpy_row_sum(self.undA)
            self.attr['Func_AllDegree'].sort()
            self.attr['Func_AveInDegree'] = sum(self.attr['Func_InDegree'])/len(self.attr['Func_InDegree'])
            self.attr['Func_AveOutDegree'] = sum(self.attr['Func_OutDegree'])/len(self.attr['Func_OutDegree'])
            self.attr['Func_AveAllDegree'] = sum(self.attr['Func_AllDegree'])/len(self.attr['Func_AllDegree'])
            self.attr['Func_MaxInDegree'] = max(self.attr['Func_InDegree'])
            self.attr['Func_MaxOutDegree'] = max(self.attr['Func_OutDegree'])
            self.attr['Func_MaxAllDegree'] = max(self.attr['Func_AllDegree'])
            self.attr['Func_CfgEntropy'] = self.countCfgEntropy()
            self.attr['Func_PathList'] = self.count_pathList(self.dijkstra())
            self.attr['Func_AvePath'] = sum(self.attr['Func_PathList'])/len(self.attr['Func_PathList'])
            self.attr['Func_E'] = float(self.attr['Func_Edge'] - self.attr['Func_AvePath'])/self.attr['Func_Edge']
            self.attr['Func_Diameter'] = max(self.attr['Func_PathList'])
            self.attr['Func_Cc'] = self.countCc()


    #count Features
    def countDensity(self):
        if self.attr['Func_Node'] == 1:
            return 0.0
        else:
            return 2.0 * self.attr['Func_Edge'] / (self.attr['Func_Node'] * (self.attr['Func_Node'] - 1))


    def countCfgEntropy(self):
        nodeNum = len(self.attr['Func_AllDegree'])
        df = Counter(self.attr['Func_AllDegree'])  # 计算频率
        entr = 0
        for k in df:
            p = float(df[k]) / nodeNum
            entr = entr + p * math.log(p) / math.log(2)
        return -entr


    # 计算路径序列
    # 输入D是路径矩阵
    # 输出pathList是升序路径序列
    def count_pathList(self,disDic):
        dis = []
        for i in disDic.keys():
            dis.append(disDic[i])
        while float('inf') in dis: #为了避免两个入口节点= = 真有这种该死的情况！
            dis.remove(float('inf'))
        dis.sort()
        return dis


    def dijkstra(self):
        G= self.Matrix2Dic(self.dA)
        source = self.first
        unprocessed = set(G.keys()) # vertices whose shortest paths from source have not yet been calculated
        unprocessed.remove(source)
        shortest_distances = {source: 0}
        for i in xrange(len(G) - 1):
            m, closest_head = float('inf'), -1
            for tail in shortest_distances:
                for head in G[tail]:
                    if head in unprocessed:
                        d = shortest_distances[tail] + G[tail][head]
                        if d < m:
                            m, closest_head = d, head
            if closest_head != -1:
                unprocessed.remove(closest_head)
                shortest_distances[closest_head] = m
            else:
                for vertex in unprocessed:
                    shortest_distances[vertex] = float('inf')
        return shortest_distances


    # 计算聚类系数
    # 输入A是无向CFG图邻接矩阵
    def countCc(self):
        A = self.undA
        entryAddr = self.attr['Func_Addr']
        nodeNum = len(A)
        dList = self.count_numpy_row_sum(A)
        #dList = sum(A)
        for i in range(0, nodeNum):
            s = [j for j in range(0, nodeNum) if A[i][j] == 1]  # i的所有邻居节点
            sum0 = 0.0
            sum1 = 0.0
            for j in s:
                for g in s:
                    sum0 = sum0 + A[j][g]  # 计算三角形数量
            if dList[i] != 1 and dList[i] !=0:
                sum1 = sum1 + float(sum0) / (dList[i] * (dList[i] - 1))
        return sum1 / nodeNum


    def countMatrix(self):
        n = len(self.block)
        d = {}
        k = 0
        for i in self.block:
            d[i] = k
            k = k + 1

        self.dA = []
        self.undA  =[]
        for i in range(n):
            self.dA.append([])
            self.undA.append([])
            for j in range(n):
                self.dA[i].append(0.0)
                self.undA[i].append(0.0)
        #print self.dA
        #print self.undA
        # self.dA = nu.zeros((n, n))  #directed A
        # self.undA = nu.zeros((n, n))  #undirected A


        for edge in self.reCfg:
            self.dA[d[edge[0]]][d[edge[1]]] = 1.0
            self.undA[d[edge[0]]][d[edge[1]]] = 1.0
            self.undA[d[edge[1]]][d[edge[0]]] = 1.0

        # if self.addr not in self.block:
            # print 'start not in block'
            # print self.name
            # print hex(self.addr)
            # print display1(self.block)
        try:
            self.first = d[self.attr['Func_Name']]
        except:
            self.first = d[self.block[0]]


    def __makecfg(self, x, y):
        if x != BADADDR and y != BADADDR:
            self.cfgEdges.add((x, y))
            self.cfgOut.add(x)
            self.cfgIn.add(y)


    def count_bbList(self):#FlowChart is a class of block analyse
        bb_list = []
        name = GetFunctionName(self.__func.startEA)
        fc = FlowChart(self.__func)
        for j in range(0,fc.size):
            bb = fc.__getitem__(j)
            if bb.startEA == bb.endEA:
                break
            bb_list.append(bb.startEA)#-4 will cause problems
        bb_list.sort()
        # if name != self.attr['Func_Name']:
        #     global mycount
        #     mycount += 1
        return bb_list


    def count_numpy_row_sum(self,a):
        result = []
        if len(a) == 0:
            return result
        n = len(a[0])
        for i in range(n):
            count = 0
            for j in range(n):
                count += a[j][i]
            result.append(count)
        return result


    def count_numpy_line_sum(self,a):
        result = []
        if len(a) == 0:
            return result
        n = len(a[0])
        for i in range(n):
            count = 0
            for j in range(n):
                count += a[i][j]
            result.append(count)
        return result


    def Matrix2Dic(self,A):
        G = {}
        for i in range(0,len(A)):
            G[i] = {}
            for j in range(0,len(A)):
                if A[i][j]!= 0:
                    G[i][j] = 1.0
        return G

def main():  # response for executing

    #BugName = 'alpha_auth_check'
    #dbName = idc.ARGV[2]
    #BugCollectionName = idc.ARGV[3]
    #ugFlag = idc.ARGV[2]

	#BugName = idc.ARGV[1]
    fout2 = open('out.txt','w')
    fout2.write('test')
    fout2.close()

    fout = open('/home/cy/Desktop/firminsight/FunRelation/FunRelation/bug.json','w')

    for i in range(0, get_func_qty()):
        fun = getn_func(i)
        segname = get_segm_name(fun.startEA)
        # only analyze the function which segname is .text or LOAD
        if segname[1:4] not in ["tex","OAD"]:
            continue
        # Analyse the each function

        if str(GetFunctionName(fun.startEA)) not in  [BugName]:
            continue
        f = funAnalyzer(fun)
        f.startAnalyze()

        # Linux ida bug, we delete the problem functions
        sAddr = fun.startEA
        if(sAddr!=fun.startEA):
            #print "ERROR-1: ", sAddr, fun.startEA
            continue
        if f.attr["Func_Addr"] != fun.startEA:
            #print "ERROR-2: ", fun.startEA, flst[fun.startEA].dump()
	    continue

        func_info = f.attr
        outStr = json.dumps(func_info,ensure_ascii = False)+','
        fout.write(outStr.strip().encode('utf-8')+'\n')

	fout.close()




        #func_info["Time"] = time.strftime("%Y-%m-%d %H:%m:%S", time.localtime())
        #func_info["BugFlag"] = BugFlag
        #if dbFlag:
        #    conn = connectDB()
            #[WARNING] prior database with the same name will be replaced!
            #db[collectionName].remove()#Note! there are so many binaries
	#    conn['test']['CQ'].insert({'name':'changqing'})
        #    try:
        #        conn[dbName][BugCollectionName].insert_one(func_info)
        #    except Exception, e:
        #        raise e



Time1 = time.time()
main()
Time2 = time.clock()
#print 'The time: ', allMyTime2 - allMyTime1
idc.Exit(0)
