from gui.techtree.techtree_dp import TechTreeDataProvider, DisplaySettingsModel
from items import _xml

def TechTreeDataProvider__readNodeList(self, shared, nation, xmlPath, clearCache=False, orderPrefix=0):
    baseInfo = base(self, shared, nation, xmlPath, clearCache, orderPrefix)
    for i in baseInfo:
        baseInfoSec = baseInfo.get(i, None)
        if baseInfoSec is not None:
            baseRow = baseInfoSec['row']
            baseColumn = baseInfoSec['column']
            baseInfoSec['row'] = baseColumn
            baseInfoSec['column'] = baseRow/2
    return baseInfo

def TechTreeDataProvider__readShared(self, clearCache=False):
    baseInfo = base2(self, clearCache)
    baseRowsNumber = baseInfo['settings'].rowsNumber
    baseColumnsNumber = baseInfo['settings'].columnsNumber
    basePremiumRowsNumber = baseInfo['settings'].premiumRowsNumber
    
    baseInfo['settings'] = DisplaySettingsModel(baseRowsNumber, baseColumnsNumber, basePremiumRowsNumber)
    return baseInfo

def TechTreeDataProvider__readDefaultLine(self, shared, xmlCtx, section):
    shared['default'] = {'line': 'vertical'}
    return

base2 = TechTreeDataProvider._TechTreeDataProvider__readShared
base = TechTreeDataProvider._TechTreeDataProvider__readNodeList

TechTreeDataProvider._TechTreeDataProvider__readNodeList = TechTreeDataProvider__readNodeList
TechTreeDataProvider._TechTreeDataProvider__readShared = TechTreeDataProvider__readShared
#TechTreeDataProvider._TechTreeDataProvider__readDefaultLine = TechTreeDataProvider__readDefaultLine