__author__ = 'qingqing'

from Similarty_Function import *
from attr_info import attrInfo,attrListInfo,attrValueInfo,attrSetInfo

class CountSim():


    def __init__(self,d1,d2):
        self.sim = {}
        self.countSimAttr(d1,d2)


    def countSimAttr(self,d1,d2):
        for i in attrInfo:
            self.sim[i+'_bug'] = d1[i]  #bug and target
            self.sim[i+'_target'] = d2[i]
        for i in attrValueInfo:
            self.sim['sim_'+i] = numSim(d1[i],d2[i])
        for i in attrListInfo:
            self.sim['sim_'+i] = longSim(d1[i],d2[i])
        for i in attrSetInfo:
            self.sim['sim_'+i] = jaccardSim(d1[i],d2[i])


    def countLabel(self):
        if self.sim['Func_Name_bug'] == self.sim['Func_Name_target']:
            self.label = 1
        else: self.label = 0
        self.sim['Label'] = self.label






