import BigWorld
from CurrentVehicle import g_currentVehicle
from gui import InputHandler, SystemMessages
from gui.shared import event_dispatcher
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors import plugins
from gui.shared.utils.key_mapping import getBigworldNameFromKey
from helpers import isPlayerAccount
from items import vehicles

def onCacheRecieved(reqID, data):
    for k, v in data[GUI_ITEM_TYPE.VEHICLE]['compDescr'].items():
        veh = vehicles.VehicleDescr(compactDescr=v)
        if not plugins.VehicleSellsLeftValidator(g_currentVehicle.item).validate().success:
            SystemMessages.pushMessage('Limit', priority=True)
            return
        if veh.level in (2, 3, 4) and not veh.type.isPremium:
            event_dispatcher.showVehicleSellDialog(k)
            return

def onhandleKeyEvent(event):
    key = getBigworldNameFromKey(event.key)
    if key == 'KEY_S' and isPlayerAccount():
        BigWorld.player().inventory.getCache(onCacheRecieved)

InputHandler.g_instance.onKeyDown += onhandleKeyEvent