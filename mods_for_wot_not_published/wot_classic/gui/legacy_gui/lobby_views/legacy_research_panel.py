from helpers import dependency
from CurrentVehicle import g_currentVehicle

from gui.ClientUpdateManager import g_clientUpdateManager

from gui.Scaleform.framework.entities.View import View

from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IVehicleComparisonBasket

class LegacyResearchPanel(View):
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    SWF = None

    def __init__(self):
        super(LegacyResearchPanel, self).__init__()
        LegacyResearchPanel.SWF = self

    def _populate(self):
        super(LegacyResearchPanel, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.vehTypeXP': self._update, 
           'stats.eliteVehicles': self._update})
        self._update()
        self.comparisonBasket.onChange += self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange += self._update
        g_currentVehicle.onChanged += self._update

    def _dispose(self):
        super(LegacyResearchPanel, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.comparisonBasket.onChange -= self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange -= self._update
        g_currentVehicle.onChanged -= self._update

    def __onCompareBasketChanged(self, changedData):
        if changedData.isFullChanged:
            self._update()

    def _update(self, *args, **kwargs):
        if g_currentVehicle.isPresent():
            xps = self.itemsCache.items.stats.vehiclesXPs
            vehicle = g_currentVehicle.item
            xp = xps.get(vehicle.intCD, 0)
            self.flashObject.as_setVehInfo(vehicle.isElite, xp)

print '[OMNILAB R&D: views.LegacyResearchPanel] INITIALIZED!'