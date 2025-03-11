import BigWorld
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items.items_actions import factory
from functools import partial

def dissmisAction(tankman):
    factory.doAction(factory.DISMISS_TANKMAN, tankman)

for tankman in g_currentVehicle.itemsCache.items.getTankmen():
    tankmanObj = g_currentVehicle.itemsCache.items.getTankman(tankman)
    if not tankmanObj.isInTank and tankmanObj.earnedSkillsCount == 0:
        BigWorld.callback(2, partial(dissmisAction, tankman))
    else: continue