import BigWorld
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items.items_actions import factory
from functools import partial

tList = []

def dissmisAction(tankmanList):
    factory.doAction(factory.DISMISS_TANKMAN, tankmanList)

for tankmanObj in g_currentVehicle.itemsCache.items.getTankmen().values():
    if not tankmanObj.isInTank and tankmanObj.earnedSkillsCount == 0:
        tList.append(tankmanObj)
    else: continue

dissmisAction(tList)