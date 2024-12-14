from functools import partial
from BigWorld import callback

from CurrentVehicle import g_currentVehicle
from gui import DialogsInterface, SystemMessages

from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import events, event_dispatcher as shared_events
from gui.shared.utils import decorators
from gui.shared.money import Currency, Money
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.formatters import getItemPricesVOWithReason
from gui.shared.utils.requesters import REQ_CRITERIA as _RC
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.processors.vehicle import VehicleRepairer, VehicleAutoRepairProcessor, VehicleAutoLoadProcessor, VehicleAutoEquipProcessor

from helpers import i18n, dependency

from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta, DIALOG_BUTTON_ID, ConfirmDialogButtons
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

from skeletons.gui.shared import IItemsCache

class TechMainConfirmButtons(ConfirmDialogButtons):

    def getLabels(self):
        return ({'id': DIALOG_BUTTON_ID.SUBMIT, 'label': self._submit, 'focused': True},
                {'id': DIALOG_BUTTON_ID.CLOSE, 'label': self._close, 'focused': False})

class TechnicalMaintenanceMeta(AbstractWindowView):

    def getEquipment(self, id1, currency1, id2, currency2, id3, currency3):
        self._printOverrideError('getEquipment')

    def repair(self):
        self._printOverrideError('repair')

    def setRefillSettings(self, vehicleCompact, repair, shells, equipment):
        self._printOverrideError('setRefillSettings')

    def showModuleInfo(self, moduleId):
        self._printOverrideError('showModuleInfo')

    def fillVehicle(self, needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment):
        self._printOverrideError('fillVehicle')

    def updateEquipmentCurrency(self, equipmentIndex, currency):
        self._printOverrideError('updateEquipmentCurrency')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setEquipmentS(self, installed, setup, modules, capacity):
        return self.flashObject.as_setEquipment(installed, setup, modules, capacity) if self._isDAAPIInited() else None

    def as_setCreditsS(self, credits):
        return self.flashObject.as_setCredits(credits) if self._isDAAPIInited() else None

    def as_setGoldS(self, gold):
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_resetEquipmentS(self, equipmentCD):
        return self.flashObject.as_resetEquipment(equipmentCD) if self._isDAAPIInited() else None

    def as_setEquipmentVisibleS(self, boolArray):
        return self.flashObject.as_setEquipmentVisible(boolArray) if self._isDAAPIInited() else None

class TechnicalMaintenance(TechnicalMaintenanceMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, _=None, skipConfirm=False):
        super(TechnicalMaintenance, self).__init__()
        self.__isConfirmDialogShown = False
        self.__layout = {}
        self._skipConfirm = skipConfirm
        return

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(TechnicalMaintenance, self)._populate()
        self.itemsCache.onSyncCompleted += self._onShopResync
        self.addListener(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, self.__resetEquipment, scope=EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.onCreditsChange)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.onGoldChange)
        g_clientUpdateManager.addCallbacks({'cache.mayConsumeWalletResources': self.onGoldChange,
         'cache.vehsLock': self.__onCurrentVehicleChanged})
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.populateTechnicalMaintenance()
        self.populateTechnicalMaintenanceEquipmentDefaults()
        # self.setupContextHints(TUTORIAL.TECHNICAL_MAINTENANCE)

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self._onShopResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.removeListener(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, self.__resetEquipment, scope=EVENT_BUS_SCOPE.LOBBY)
        super(TechnicalMaintenance, self)._dispose()

    def onCreditsChange(self, value):
        value = self.itemsCache.items.stats.credits
        self.as_setCreditsS(value)

    def onGoldChange(self, value):
        value = self.itemsCache.items.stats.gold
        self.as_setGoldS(value)

    def _onShopResync(self, reason, diff):
        if not g_currentVehicle.isPresent():
            self.destroy()
            return
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.populateTechnicalMaintenance()
            self.populateTechnicalMaintenanceEquipment(**self.__layout)

    def getEquipment(self, eId1, currency1, eId2, currency2, eId3, currency3):
        eIdsCD = []
        for item in (eId1, eId2, eId3):
            if item is None:
                eIdsCD.append(0)
            else:
                eIdsCD.append(int(item))

        self.populateTechnicalMaintenanceEquipment(eIdsCD[0], currency1, eIdsCD[1], currency2, eIdsCD[2], currency3)
        return

    def updateEquipmentCurrency(self, equipmentIndex, currency):
        key = 'currency%d' % (int(equipmentIndex) + 1)
        params = {key: currency}
        self.__saveCurrentLayout(**params)

    @decorators.adisp_process('loadStats')
    def setRefillSettings(self, intCD, repair, load, equip):
        vehicle = self.itemsCache.items.getItemByCD(int(intCD))
        if vehicle.isAutoRepair != repair:
            yield VehicleAutoRepairProcessor(vehicle, repair).request()
        if vehicle.isAutoLoad != load:
            yield VehicleAutoLoadProcessor(vehicle, load).request()
        if vehicle.isAutoEquip != equip:
            yield VehicleAutoEquipProcessor(vehicle, equip).request()

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentVehicle.item.descriptor)
        return

    def populateTechnicalMaintenance(self):
        money = self.itemsCache.items.stats.money
        data = {Currency.CREDITS: money.getSignValue(Currency.CREDITS),
         Currency.GOLD: money.getSignValue(Currency.GOLD)}
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            casseteCount = vehicle.descriptor.gun.clip[0]
            casseteText = i18n.makeString('#wek:technicalMaintenance/ammoTitleEx') % casseteCount
            data.update({'vehicleId': str(vehicle.intCD),
             'repairCost': vehicle.repairCost,
             'maxRepairCost': vehicle.descriptor.getMaxRepairCost(),
             'autoRepair': vehicle.isAutoRepair,
             'autoShells': vehicle.isAutoLoad,
             'autoEqip': vehicle.isAutoEquip,
             'maxAmmo': vehicle.gun.maxAmmo,
             'gunIntCD': vehicle.gun.intCD,
             'casseteFieldText': '' if casseteCount == 1 else casseteText,
             'shells': [],
             'infoAfterShellBlock': ''})
            for shell in vehicle.shells.installed:
                if shell.isHidden:
                    continue
                buyPrice = shell.getBuyPrice()
                prices = shell.buyPrices.getSum().price
                action = None
                if buyPrice.isActionPrice():
                    action = packItemActionTooltipData(shell)
                data['shells'].append({'id': str(shell.intCD),
                 'type': shell.type,
                 'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor.icon[0],
                 'count': shell.count,
                 'userCount': shell.count,
                 'step': casseteCount,
                 'inventoryCount': shell.inventoryCount,
                 'prices': prices.toMoneyTuple(),
                 'currency': buyPrice.getCurrency(byWeight=True),
                 'ammoName': shell.longUserNameAbbr,
                 'tableName': shell.getShortInfo(vehicle, True),
                 'maxAmmo': vehicle.gun.maxAmmo,
                 'userCredits': money.toDict(),
                 'actionPriceData': action,
                 'desc': '#wek:shellListItemRenderer/replace'})

        self.as_setDataS(data)
        return

    def populateTechnicalMaintenanceEquipmentDefaults(self):
        """
        Loads layout and sets equipment according to it as a default
        """
        vehicle = g_currentVehicle.item

        layoutVisible = [False, False, False]
        for i in range(0, vehicle.consumables.layoutCapacity):
            layoutVisible[i] = True

        self._setEquipment([], [], [], vehicle.consumables.layoutCapacity)
        self.as_setEquipmentVisibleS(layoutVisible)

        params = {}
        for i, e in enumerate(g_currentVehicle.item.consumables.installed):
            params['eId%s' % (i + 1)] = e.intCD if e else None
            params['currency%s' % (i + 1)] = e.getBuyPrice(preferred=True).getCurrency(byWeight=True) if e else None
            self.populateTechnicalMaintenanceEquipment(**params)
        return

    def populateTechnicalMaintenanceEquipment(self, eId1=None, currency1=None, eId2=None, currency2=None, eId3=None, currency3=None, slotIndex=None):
        items = self.itemsCache.items
        vehicle = g_currentVehicle.item
        money = self.itemsCache.items.stats.money
        installedItems = vehicle.consumables.installed
        currencies = [None, None, None]
        selectedItems = [None, None, None]
        if eId1 is not None or eId2 is not None or eId3 is not None or slotIndex is not None:
            selectedItems = map(lambda id: items.getItemByCD(id) if id is not None else None, (eId1, eId2, eId3))
            currencies = [currency1, currency2, currency3]
        inventoryVehicles = items.getVehicles(_RC.INVENTORY).values()
        itemsCriteria = ~_RC.HIDDEN | _RC.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.EQUIPMENT])
        data = sorted(self.itemsCache.items.getItems(GUI_ITEM_TYPE.EQUIPMENT, itemsCriteria).values(), reverse=True)
        modules = []

        for module in data:
            fits = []
            for i in xrange(3):
                fits.append(self.__getStatus(module.mayInstall(vehicle, i)[1]))
            
            buyPrice = module.getBuyPrice()
            prices = module.buyPrices.getSum().price
            inventoryCount = module.inventoryCount
            index = -1
            if module in selectedItems:
                index = selectedItems.index(module)
                _, reason = module.mayInstall(vehicle, index)
                priceCurrency = currencies[index] or Currency.CREDITS
                if inventoryCount and module not in installedItems:
                    inventoryCount -= 1
            else:
                _, reason = module.mayInstall(vehicle)
                priceCurrency = buyPrice.getCurrency(byWeight=True)
            highlightType = module.getHighlightType()
            disabledOption = self.__isSlotDisabled(module, selectedItems)
            itemPrice = module.buyPrices.itemPrice
            modules.append({'id': str(module.intCD),
             'name': module.userName,
             'desc': module.fullDescription,
             'target': module.getTarget(vehicle),
             'compactDescr': module.intCD,
             'prices': prices.toMoneyTuple(),
             'currency': priceCurrency,
             'icon': module.icon,
             'index': index,
             'inventoryCount': module.inventoryCount,
             'vehicleCount': len(module.getInstalledVehicles(inventoryVehicles)),
             'count': inventoryCount,
             'fits': fits,
             'userCredits': money.toDict(),
             'moduleLabel': module.getGUIEmblemID(),
             'builtIn': module.isBuiltIn,
             'highlightType': highlightType,
             'disabledOption': disabledOption,
             'isActionPrice': itemPrice.isActionPrice(),
             'itemPrices': getItemPricesVOWithReason(reason, itemPrice),
             'nullItemPrices': getItemPricesVOWithReason(reason, ItemPrice(Money(0), Money(0))),
             'inSetup': module in selectedItems})


        installed = []
        installed = map(lambda e: e.intCD if e is not None else None, installedItems)
        setup = map(lambda e: e.intCD if e is not None else None, selectedItems)
        

        self.__saveCurrentLayout(eId1=eId1, currency1=currency1, eId2=eId2, currency2=currency2, eId3=eId3, currency3=currency3)
        self._setEquipment(installed, setup, modules, vehicle.consumables.layoutCapacity)
        return

    @decorators.adisp_process('updateMyVehicles')
    def repair(self):
        vehicle = g_currentVehicle.item
        if vehicle.isBroken:
            result = yield VehicleRepairer(vehicle).request()
            if result and result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def fillVehicle(self, needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment):
        shellsLayout = []
        eqsLayout = []
        for shell in shells:
            buyGoldShellForCredits = shell.prices[1] > 0 and shell.currency == Currency.CREDITS
            shellsLayout.append({'id': int(shell.id) if not buyGoldShellForCredits else -int(shell.id), 'count': int(shell.userCount)})

        for ei in equipment:
            if ei is not None:
                intCD = int(ei.id)
                buyGoldEqForCredits = ei.prices[1] > 0 and ei.currency == Currency.CREDITS
                eqsLayout.append({'id': intCD if not buyGoldEqForCredits else -intCD, 'count': 1})
            else:
                eqsLayout.append({'id': 0, 'count': 0})

        if not needRepair and not needAmmo and not needEquipment:
            self.__setVehicleLayouts(g_currentVehicle.item, shellsLayout, eqsLayout)
        else:
            msgPrefix = '{0}'
            if needRepair:
                msgPrefix = msgPrefix.format('_repair{0}')
            if needAmmo or needEquipment:
                msgPrefix = msgPrefix.format('_populate')
            elif isUnload:
                msgPrefix = msgPrefix.format('_unload')
            elif isOrderChanged:
                msgPrefix = msgPrefix.format('_order_change')
            else:
                msgPrefix = msgPrefix.format('')
            msg = i18n.makeString(''.join(['#wek:technicalMaintenanceConfirm/msg', msgPrefix]))
            if not self.__isConfirmDialogShown:

                def fillConfirmationCallback(isConfirmed):
                    if isConfirmed:
                        if needRepair:
                            self.repair()
                        self.__setVehicleLayouts(g_currentVehicle.item, shellsLayout, eqsLayout)
                    self.__isConfirmDialogShown = False
                    
                DialogsInterface.showDialog(SimpleDialogMeta('#wek:technicalMaintenanceConfirm/title', 
                                                             msg, 
                                                             TechMainConfirmButtons('#wek:technicalMaintenanceConfirm/submit', '#wek:technicalMaintenanceConfirm/cancel')),
                                                             fillConfirmationCallback)
                self.__isConfirmDialogShown = True
        return

    @staticmethod
    def __isSlotDisabled(module, slots):
        if module.isBuiltIn:
            installedModules = filter(None, slots)
            if len(installedModules) == 1:
                return True
        return False

    def _setEquipment(self, installed, setup, modules, capacity):
        self.as_setEquipmentS(installed, setup, modules, capacity)

    def __onCurrentVehicleChanged(self, *args):
        if g_currentVehicle.isLocked() or not g_currentVehicle.isPresent() or g_currentVehicle.isEvent():
            self.destroy()
        else:
            self.populateTechnicalMaintenance()
            if g_currentVehicle.isPresent():
                self.populateTechnicalMaintenanceEquipmentDefaults()

    def __setVehicleLayouts(self, vehicle, shellsLayout=list(), eqsLayout=list()):
        for _ in range(0, 3 - vehicle.consumables.layoutCapacity):
            eqsLayout.pop()

        copyVehicle = vehicle
        for i, e in enumerate(shellsLayout):
            shell = self.itemsCache.items.getItemByCD(int(e['id']))
            shell.count = int(e['count'])
            copyVehicle.shells.layout[i] = shell
        for i, e in enumerate(eqsLayout):
            equip = self.itemsCache.items.getItemByCD(int(e['id']))
            copyVehicle.consumables.layout[i] = equip
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_SHELLS, copyVehicle, False, skipConfirm=True)
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_CONSUMABLES, copyVehicle, False, skipConfirm=True)
        self.destroy()

    def __saveCurrentLayout(self, **kwargs):
        self.__layout.update(kwargs)

    def __resetEquipment(self, event):
        equipmentCD = event.ctx.get('eqCD', None)
        if equipmentCD is not None:
            self.as_resetEquipmentS(equipmentCD)
        return

    def __getStatus(self, reason):
        return '#menu:moduleFits/' + reason.replace(' ', '_') if reason is not None else ''

print '[OMNILAB R&D: views.TechnicalMaintenance] INITIALIZED!'