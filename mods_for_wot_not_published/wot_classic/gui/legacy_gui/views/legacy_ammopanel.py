import BigWorld, Keys

from gui.Scaleform.locale.MENU import MENU
from helpers import dependency
from helpers.i18n import makeString
from functools import partial
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_CURRENT_EXCEPTION

from items import getTypeInfoByName
from items import ITEM_TYPES as MODULE_ITEM_TYPES

from account_helpers.AccountSettings import SHOW_OPT_DEVICE_HINT, AccountSettings


from gui import InputHandler, SystemMessages, g_htmlTemplates, shop
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.processors.vehicle import VehicleAutoBattleBoosterEquipProcessor
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.ClientUpdateManager import g_clientUpdateManager

from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel import AmmunitionPanel
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO
from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import ModuleFittingSelectPopover, _POPOVER_FIRST_TAB_IDX, _POPOVER_SECOND_TAB_IDX, CommonFittingSelectPopover, _HangarLogicProvider, PopoverLogicProvider, _extendByModuleData
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import OptDeviceBonusesDescriptionBuilder
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

from frameworks.wulf import Array
from frameworks.wulf.gui_constants import WindowLayer

from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IEpicBattleMetaGameController

from ..utils import override

_MODULE_SLOTS = (GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleGun],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleTurret],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleChassis],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleEngine],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleRadio],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.optionalDevice],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.shell],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.equipment],
 'battleBooster', 'battleAbility')

class EmptySlotVO(dict):
    
    def __init__(self, moduleType='', isDisabled=False):
        super(EmptySlotVO, self).__init__()

        self['name'] = ''
        self['slotType'] = moduleType
        self['removable'] = True
        self['slotLocked'] = g_currentVehicle.item.isLocked
        if isDisabled:
            self['id'] = -999
            self['tooltip'] = ''
            self['tooltipType'] = ''
            self['moduleLabel'] = 'disabledSlot'
            self['overlayType'] = ''
            self['bgHighlightType'] = ''
            self['slotLocked'] = True
        else:
            self['id'] = -1
            self['tooltip'] = '#wek:legacy_ammo_panel/' + moduleType + '/empty'
            self['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
            self['moduleLabel'] = 'empty' if moduleType != 'battleBooster' else 'emptyBooster'

class HangarFittingSlotVO(FittingSlotVO):

    def _prepareModule(self, modulesData, vehicle):
        module = modulesData[0]
        self['slotLocked'] = vehicle.isLocked or not vehicle.isAlive
        if module.itemTypeName == FITTING_TYPES.OPTIONAL_DEVICE:
            battleBooster = vehicle.battleBoosters.installed[0]
            if battleBooster is not None and battleBooster.isOptionalDeviceCompatible(module):
                self['highlight'] = True

            self['bgHighlightType'] = module.getHighlightType()
            self['overlayType'] = module.getOverlayType()
        elif module.itemTypeName == FITTING_TYPES.EQUIPMENT:
            self['bgHighlightType'] = module.getHighlightType()
            self['overlayType'] = module.getOverlayType()
        elif module.itemTypeName == FITTING_TYPES.BOOSTER:
            affectsAtTTC = module.isAffectsOnVehicle(vehicle)
            self['affectsAtTTC'] = affectsAtTTC
            if affectsAtTTC:
                self['bgHighlightType'] = module.getHighlightType(vehicle=vehicle)
                self['overlayType'] = module.getOverlayType(vehicle=vehicle)
                if module.isCrewBooster():
                    isPerkReplace = not module.isAffectedSkillLearnt(vehicle) and module.getGUIEmblemID() != 'commander_sixthSense'
                    bgType = 'battleBoosterReplace' if isPerkReplace else 'battleBooster'
                    self['overlayType'] = bgType
                    self['bgHighlightType'] = bgType
                else:
                    self['highlight'] = affectsAtTTC
                    self['bgHighlightType'] = 'battleBooster'
        else:
            self['level'] = module.level
            if module.itemTypeName == GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleTurret] and vehicle.isAlive:
                self['slotLocked'] = vehicle.isLocked or not vehicle.hasTurrets
        return module
    
class LegacyAmmoPanel(View, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    appLoader = dependency.instance(IAppLoader)
    
    _TAB_IDS = (0, 1)
    _OPTDEV_TABS = [{'label': '#tank_setup:tabs/simple', 'id': 'simpleOptDevices'}, 
            {'label': '#tank_setup:tabs/deluxe', 'id': 'deluxeOptDevices'}]
    _BOOST_TABS = [{'label': '#tank_setup:tabs/optDevice', 'id': 'boostersForAmmunition'}, 
    {'label': '#tank_setup:tabs/crew', 'id': 'boostersForCrew'}]
    
    def __init__(self):
        super(LegacyAmmoPanel, self).__init__()
        self._initLoad = True

        override(AmmunitionPanel, '_populate', self._AmmunitionPanel_populate)
        override(ModuleFittingSelectPopover, '__init__', self._ModuleFittingSelectPopover__init__)
        override(ModuleFittingSelectPopover, '_dispose', self._ModuleFittingSelectPopover_dispose)
        override(PopoverLogicProvider, '_PopoverLogicProvider__extendByTypeSpecificData', self._PopoverLogicProvider__extendByTypeSpecificData)
        override(CommonFittingSelectPopover, '_getCommonData', self._CommonFittingSelectPopover_getCommonData)
        override(CommonFittingSelectPopover, '_prepareInitialData', self._CommonFittingSelectPopover_prepareInitialData)
        override(CommonFittingSelectPopover, 'setCurrentTab', self._CommonFittingSelectPopover_setCurrentTab)
        override(CommonFittingSelectPopover, '_getTabsData', self._CommonFittingSelectPopover_getTabsData)
        override(CommonFittingSelectPopover, '_getInitialTabIndex', self._CommonFittingSelectPopover_getInitialTabIndex)
        override(_HangarLogicProvider, '_getSpecificCriteria', self._HangarLogicProvider_getSpecificCriteria)
        override(_HangarLogicProvider, '_buildModuleData', self._HangarLogicProvider_buildModuleData)
        override(_HangarLogicProvider, '_buildList', self._HangarLogicProvider_buildList)
        override(_HangarLogicProvider, 'setModule', self._HangarLogicProvider_setModule)

    def _populate(self):
        super(LegacyAmmoPanel, self)._populate()
        self._addListeners()
        self.as_setupSlots()

    def _addListeners(self):
        self.startGlobalListening()
        InputHandler.g_instance.onKeyDown += self.switchOptDevLayoutTrigger
        InputHandler.g_instance.onKeyDown += self.switchEquipmentLayoutTrigger
        self.itemsCache.onSyncCompleted += self._update
        g_currentVehicle.onChanged += self.as_setupSlots
        g_clientUpdateManager.addCallbacks({'inventory': self._update})
    
    def _dispose(self):
        self.stopGlobalListening()
        InputHandler.g_instance.onKeyDown -= self.switchOptDevLayoutTrigger
        InputHandler.g_instance.onKeyDown -= self.switchEquipmentLayoutTrigger
        self.itemsCache.onSyncCompleted -= self._update
        g_currentVehicle.onChanged -= self.as_setupSlots
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(LegacyAmmoPanel, self)._dispose()

    
    def _AmmunitionPanel_populate(self, base, baseSelf):
        base(baseSelf)
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        if setOnlyBattleAbilities not in app.containerManager.onViewAddedToContainer:
            app.containerManager.onViewAddedToContainer += setOnlyBattleAbilities
    
    def _ModuleFittingSelectPopover__init__(self, base, baseSelf, ctx=None, customProviderClass=None):
        base(baseSelf, ctx, customProviderClass)

        try:
            self._initLoad = True
            baseSelf.__class__.upgradeVehicleModule = upgradeModule
            baseSelf.__class__.buyVehicleModule = installModule
            baseSelf.__class__.setAutoRearm = setAutoRearm
            baseSelf.__class__.onManageBattleAbilitiesClicked = onManageBattleAbilitiesClicked
        except:
            LOG_CURRENT_EXCEPTION()
    
    def _ModuleFittingSelectPopover_dispose(self, base, baseSelf):

        self._initLoad = True
        base(baseSelf)


    def _PopoverLogicProvider__extendByTypeSpecificData(self, base, baseSelf, moduleData, module):
        if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            _extendByArtefactData(moduleData, module, baseSelf._slotIndex)
        elif module.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
            _extendByModuleData(moduleData, module, baseSelf._vehicle.descriptor, baseSelf._PopoverLogicProvider__moduleExtenders)
        if baseSelf._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
            _extendByOptionalDeviceData(moduleData, module)
        elif baseSelf._slotType == FITTING_TYPES.BOOSTER:
            _extendByBattleBoosterData(moduleData, module, baseSelf._vehicle)
        elif baseSelf._slotType == FITTING_TYPES.BATTLE_ABILITY:
            mayInstall, _ = module.mayInstall(baseSelf._vehicle)
            _extendByBattleAbilityData(moduleData, module, baseSelf._slotIndex, mayInstall)

    
    def _CommonFittingSelectPopover_getCommonData(self, base, baseSelf):
        if baseSelf._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
            rendererName = 'OptDeviceFittingItemRendererUI'
            rendererDataClass = 'omnilab.wotclassic.legacyAmmoPanel.data.LegacyOptDeviceVO'
            width = FITTING_TYPES.LARGE_POPOVER_WIDTH
            title = '#wek:optDeviceFittingSelect/title'
        elif baseSelf._slotType == FITTING_TYPES.BOOSTER:
            rendererName = 'BoosterFittingItemRendererUI'
            rendererDataClass = 'omnilab.wotclassic.legacyAmmoPanel.data.LegacyBoosterVO'
            width = FITTING_TYPES.LARGE_POPOVER_WIDTH
            title = '#wek:boosterFittingSelect/title'
        elif baseSelf._slotType == FITTING_TYPES.BATTLE_ABILITY:
            rendererName = 'BattleAbilityItemRendererUI'
            rendererDataClass = 'omnilab.wotclassic.legacyAmmoPanel.data.LegacyBattleAbilityVO'
            width = FITTING_TYPES.SHORT_POPOVER_WIDTH
            title = '#menu:battleAbility/title'
        else:
            if baseSelf._slotType == FITTING_TYPES.VEHICLE_WHEELED_CHASSIS:
                baseSelf._slotType = 'vehicleChassis'
            title = makeString(MENU.MODULEFITS_TITLE, moduleName=getTypeInfoByName(baseSelf._slotType)['userString'], vehicleName=baseSelf._getVehicle().userName if baseSelf._getVehicle() is not None else '')
            rendererDataClass = 'omnilab.wotclassic.legacyAmmoPanel.data.LegacyModuleVO'
            if baseSelf._slotType == FITTING_TYPES.VEHICLE_ENGINE:
                if baseSelf._getVehicle().descriptor.hasTurboshaftEngine or baseSelf._getVehicle().descriptor.hasRocketAcceleration:
                    rendererName = FITTING_TYPES.ENGINE_FITTING_BIG_ITEM_RENDERER
                else:
                    rendererName = FITTING_TYPES.ENGINE_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.MEDUIM_POPOVER_WIDTH
            elif baseSelf._slotType == FITTING_TYPES.VEHICLE_CHASSIS_OVERRIDE:
                rendererName = FITTING_TYPES.CHASSIS_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.MEDUIM_POPOVER_WIDTH
            elif baseSelf._slotType == FITTING_TYPES.VEHICLE_RADIO:
                rendererName = FITTING_TYPES.RADIO_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.SHORT_POPOVER_WIDTH
            else:
                rendererName = FITTING_TYPES.GUN_TURRET_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.LARGE_POPOVER_WIDTH

        return (rendererName, rendererDataClass, width, title)

    
    def _CommonFittingSelectPopover_prepareInitialData(self, base, baseSelf):
        rendererName, rendererDataClass, width, title = baseSelf._getCommonData()
        result = {'title': text_styles.highTitle(title), 
            'rendererName': rendererName, 
            'rendererDataClass': rendererDataClass,
            'scrollToIndex': baseSelf._logicProvider.getSelectedIdx(), 
            'selectedIndex': baseSelf._logicProvider.getSelectedIdx(), 
            'availableDevices': baseSelf._logicProvider.getDevices(),
            'rearmCheckboxVisible': baseSelf._slotType == FITTING_TYPES.BOOSTER,
            'rearmCheckboxValue': baseSelf._getVehicle().isAutoBattleBoosterEquip() if baseSelf._slotType == FITTING_TYPES.BOOSTER else False,
            'battleAbilitiesButtonVisible': baseSelf._slotType == FITTING_TYPES.BATTLE_ABILITY,
            'width': width}
        if getListOverlayData() is not None:
            result.update(getListOverlayData())
        result.update(baseSelf._getTabsData())
        return result

    
    def _CommonFittingSelectPopover_setCurrentTab(self, base, baseSelf, tabIndex):
        if tabIndex not in self._TAB_IDS:
            return
        baseSelf._logicProvider.setTab(tabIndex)
        if tabIndex != baseSelf._getInitialTabIndex():
            baseSelf._saveTabIndex(tabIndex)
        baseSelf.as_updateS(baseSelf._prepareInitialData())

   
    def _CommonFittingSelectPopover_getTabsData(self, base, baseSelf):
        if baseSelf._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
            return {'tabData': self._OPTDEV_TABS, 'selectedTab': baseSelf._getInitialTabIndex()}
        elif baseSelf._slotType == FITTING_TYPES.BOOSTER:
            return {'tabData': self._BOOST_TABS, 'selectedTab': baseSelf._getInitialTabIndex()}
        else: return {}

    
    def _CommonFittingSelectPopover_getInitialTabIndex(self, base, baseSelf):
        if not self._initLoad:
            return baseSelf._TAB_IDX
        else:
            self._initLoad = False
            if baseSelf._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
                vehicle = baseSelf._getVehicle()
                if vehicle is None:
                    return baseSelf._TAB_IDX
                installedDevice = vehicle.optDevices.installed[baseSelf._getSlotIndex()]
                if installedDevice is not None:
                    baseSelf._saveTabIndex(_POPOVER_FIRST_TAB_IDX)
                    if installedDevice.isDeluxe:
                        baseSelf._saveTabIndex(_POPOVER_SECOND_TAB_IDX)
            elif baseSelf._slotType == FITTING_TYPES.BOOSTER:
                vehicle = baseSelf._getVehicle()
                if vehicle is None:
                    return baseSelf._TAB_IDX
                battleBooster = vehicle.battleBoosters.installed[baseSelf._getSlotIndex()]
                if battleBooster is not None:
                    baseSelf._saveTabIndex(_POPOVER_FIRST_TAB_IDX)
                    if battleBooster.isCrewBooster():
                        baseSelf._saveTabIndex(_POPOVER_SECOND_TAB_IDX)
            return baseSelf._TAB_IDX

    
    def _HangarLogicProvider_getSpecificCriteria(self, base, baseSelf, typeID):
        if typeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            criteria = REQ_CRITERIA.BATTLE_BOOSTER.OPTIONAL_DEVICE_EFFECT if baseSelf._tabIndex == _POPOVER_FIRST_TAB_IDX else REQ_CRITERIA.BATTLE_BOOSTER.CREW_EFFECT
        elif typeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            criteria = REQ_CRITERIA.CUSTOM(lambda item: not item.isDeluxe and not ((item.isTrophy or item.isModernized) and item.inventoryCount == 0 and not item.isInstalled(baseSelf._vehicle))) if baseSelf._tabIndex == _POPOVER_FIRST_TAB_IDX else REQ_CRITERIA.OPTIONAL_DEVICE.DELUXE
        elif typeID == GUI_ITEM_TYPE.BATTLE_ABILITY:
            skillItemIDs = []
            allSkills = self.epicMetaGameCtrl.getAllSkillsInformation().values()
            for skillInfo in allSkills:
                if skillInfo.category in baseSelf._vehicle.battleAbilities.slots[baseSelf._slotIndex].tags:
                    skillExample = skillInfo.levels[1]
                    skillItemIDs.append(skillExample.eqID)

            criteria = REQ_CRITERIA.CUSTOM(lambda item: item.innationID in skillItemIDs)
        else:
            criteria = REQ_CRITERIA.EMPTY
        return criteria

    
    def _HangarLogicProvider_buildModuleData(self, base, baseSelf, vehicleModule, isInstalledInSlot, stats):
        if baseSelf._slotType != FITTING_TYPES.BATTLE_ABILITY:
            baseData = base(baseSelf, vehicleModule, isInstalledInSlot, stats)
            isFit, reason = vehicleModule.mayInstall(baseSelf._vehicle, baseSelf._slotIndex)
            if reason == 'already installed':
                isFit = True
            baseData['disabled'] = not isFit
            return baseData
        else:
            baseData = base(baseSelf, vehicleModule, isInstalledInSlot, stats)
            baseData['disabled'] = not vehicleModule.isUnlocked
            baseData['showPrice'] = False
            return baseData


    
    def _HangarLogicProvider_buildList(self, base, baseSelf):
        modulesList = []
        baseSelf._tooltipType = TOOLTIPS_CONSTANTS.HANGAR_MODULE
        if baseSelf._slotType == FITTING_TYPES.VEHICLE_WHEELED_CHASSIS:
            baseSelf._slotType = 'vehicleChassis'
        elif baseSelf._slotType == FITTING_TYPES.BOOSTER:
            baseSelf._tooltipType = TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK
        elif baseSelf._slotType == FITTING_TYPES.BATTLE_ABILITY:
            baseSelf._tooltipType = TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO
        if baseSelf._vehicle is not None:
            typeId = GUI_ITEM_TYPE_INDICES[baseSelf._slotType]
            data = baseSelf._getSuitableItems(typeId)
            currXp = baseSelf._itemsCache.items.stats.vehiclesXPs.get(baseSelf._vehicle.intCD, 0)
            stats = {'money': baseSelf._itemsCache.items.stats.money,
            'exchangeRate': baseSelf._itemsCache.items.shop.exchangeRate, 
            'currXP': currXp, 
            'totalXP': currXp + baseSelf._itemsCache.items.stats.freeXP}
            for idx, vehicleModule in enumerate(data):
                if baseSelf._slotType != FITTING_TYPES.BATTLE_ABILITY:
                    isInstalled = vehicleModule.isInstalled(baseSelf._vehicle, baseSelf._slotIndex)
                    if isInstalled:
                        baseSelf._selectedIdx = idx
                else:
                    isInstalled = vehicleModule.isInstalled(baseSelf._vehicle)
                if typeId == GUI_ITEM_TYPE_INDICES['optionalDevice']:
                    inventoryVehicles = baseSelf._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
                    isInOtherVehicles = len(vehicleModule.getInstalledVehicles(inventoryVehicles.itervalues())) > 0 and not vehicleModule.isInInventory
                    isAvailable = vehicleModule.isInInventory or isInstalled
                    isTrophyOrModern = vehicleModule.isTrophy or vehicleModule.isModernized
                    if ((isTrophyOrModern and not isInOtherVehicles) or (vehicleModule.isHidden and vehicleModule.isDeluxe)) and not isAvailable:
                        continue
                moduleData = baseSelf._buildModuleData(vehicleModule, isInstalled, stats)
                if typeId == GUI_ITEM_TYPE_INDICES['optionalDevice'] and isInOtherVehicles and isTrophyOrModern:
                    moduleData.update({'target': 'vehicle', 'targetVisible': True})
                baseSelf._PopoverLogicProvider__extendByTypeSpecificData(moduleData, vehicleModule)
                modulesList.append(moduleData)
        return modulesList

    
    def _HangarLogicProvider_setModule(self, base, baseSelf, newId, oldId, isRemove, isUpgrade=False):
        newItem = baseSelf._itemsCache.items.getItemByCD(int(newId))
        if baseSelf._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
            isRemoving = newId == oldId and isRemove
            isDestroy = oldId < 0 and isRemove
            isTrophyOrModern = newItem.isTrophy or newItem.isModernized
            installedOptDevice = g_currentVehicle.item.optDevices.installed[baseSelf._slotIndex]
            if isRemoving:
                ItemsActionsFactory.doAction(ItemsActionsFactory.REMOVE_OPT_DEVICE, baseSelf._vehicle, installedOptDevice, baseSelf._slotIndex)
                return
            elif isDestroy and isTrophyOrModern:
                ItemsActionsFactory.doAction(ItemsActionsFactory.DECONSTRUCT_OPT_DEVICE, newItem, baseSelf._vehicle, baseSelf._slotIndex, None)
                return
            elif isDestroy and not isTrophyOrModern:
                ItemsActionsFactory.doAction(ItemsActionsFactory.REMOVE_OPT_DEVICE, baseSelf._vehicle, installedOptDevice, baseSelf._slotIndex, True)
                return
            elif isUpgrade:
                ItemsActionsFactory.doAction(ItemsActionsFactory.UPGRADE_OPT_DEVICE, newItem, None, None, None)
                return
            elif isTrophyOrModern:
                return
            elif newItem.isInstalled(baseSelf._vehicle):
                copyVehicle = baseSelf._vehicle
                for idx, optDevice in enumerate(baseSelf._vehicle.optDevices.installed):
                    if optDevice is None:
                        continue
                    elif optDevice.intCD == newItem.intCD:
                        copyVehicle.optDevices.swap(baseSelf._slotIndex, idx)
                ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, copyVehicle, True)
            else:
                copyVehicle = baseSelf._vehicle
                copyVehicle.optDevices.layout[baseSelf._slotIndex] = newItem
                onlyExchange = newItem.isInInventory
                if oldId > 0:
                    ItemsActionsFactory.doAction(ItemsActionsFactory.REMOVE_OPT_DEVICE, baseSelf._vehicle, installedOptDevice, baseSelf._slotIndex, forFitting=True)
                    return
                ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, copyVehicle, onlyExchange)
                return
        elif baseSelf._slotType == FITTING_TYPES.BOOSTER:
            copyVehicle = baseSelf._vehicle
            onlyExchange = newItem.isInInventory
            if isRemove:
                copyVehicle.battleBoosters.layout[baseSelf._slotIndex] = None
                ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_BATTLE_BOOSTERS, copyVehicle, onlyExchange)
                return
            
            copyVehicle.battleBoosters.layout[self._slotIndex] = newItem
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_BATTLE_BOOSTERS, copyVehicle, oldId < 0)
            return
        elif baseSelf._slotType == FITTING_TYPES.BATTLE_ABILITY:
            copyVehicle = baseSelf._vehicle
            copyVehicle.battleAbilities.layout[baseSelf._slotIndex] = newItem
            ItemsActionsFactory.doAction(ItemsActionsFactory.INSTALL_BATTLE_ABILITIES, copyVehicle, skipConfirm=True)
            return

        if newItem.isInInventory:
            ItemsActionsFactory.doAction(ItemsActionsFactory.INSTALL_ITEM, int(newId), baseSelf._vehicle.intCD)
        elif newItem.isUnlocked:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_AND_SELL_ITEM, int(newId), baseSelf._vehicle.intCD)

        return

    def showModuleInfo(self, itemCD):
        vehicle = g_currentVehicle.item
        if vehicle is not None and itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, vehicle.descriptor)
        return

    def pyLog(self, msg):
        print msg

    def onPrbEntitySwitched(self):
        self._update()

    def _update(self, *args, **kwargs):
        self.as_setupSlots()

    def onCloseBtnClicked(self):
        self.destroy()
    
    def callTechnicalMaintenance(self):
        app = self.appLoader.getApp()
        app.loadView(SFViewLoadParams('TechnicalMaintenance'))

    def as_setBattleAbilitiesVisible(self):
        isVisible = self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC)
        self.flashObject.as_setBattleAbilitiesVisibleS(isVisible)

    def switchPostProgressionLayout(self, isOptDev):
        if g_currentVehicle.item.isLocked:
            return

        localeKey = '#wek:legacy_ammo_panel/postProgression/'

        if isOptDev:
            layouts = g_currentVehicle.item.optDevices.setupLayouts
            layout_text = 'opt_dev_boosters'
        else:
            layouts = g_currentVehicle.item.consumables.setupLayouts
            layout_text = 'shells_consumables'

        if layouts.capacity > 1:
            for i in range(0, 2):
                if layouts.layoutIndex == i:
                    continue
                else:
                    ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_SETUP_EQUIPMENTS_INDEX, g_currentVehicle.item, layouts.groupID, i)
                    SystemMessages.pushMessage(localeKey + layout_text, priority=True)
        else:
            SystemMessages.pushMessage(localeKey + 'switch_error', SystemMessages.SM_TYPE.Error, priority=True)

    def switchOptDevLayoutTrigger(self, event):
        if event.isKeyDown() and (BigWorld.isKeyDown(Keys.KEY_LCONTROL) or BigWorld.isKeyDown(Keys.KEY_RCONTROL)) and BigWorld.isKeyDown(Keys.KEY_1):
            self.switchPostProgressionLayout(True)

    def switchEquipmentLayoutTrigger(self, event):
        if event.isKeyDown() and (BigWorld.isKeyDown(Keys.KEY_LCONTROL) or BigWorld.isKeyDown(Keys.KEY_RCONTROL)) and BigWorld.isKeyDown(Keys.KEY_2):
            self.switchPostProgressionLayout(False)

    def as_setupSlots(self):
        ammunitionData = {}
        modules = []
        optionalDevices = []
        shells = []
        consumables = []
        battleAbilities = []

        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            
            for slotType in _MODULE_SLOTS:
                if slotType == GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.optionalDevice]:
                    for idx, optDevice in enumerate(vehicle.optDevices.installed):
                        if optDevice is None:
                            oDSlot = EmptySlotVO(slotType)
                        else:
                            oDSlot = HangarFittingSlotVO([optDevice], vehicle, slotType, tooltipType=TOOLTIPS_CONSTANTS.HANGAR_MODULE)
                            oDSlot['slotIndex'] = idx
                        optionalDevices.append(oDSlot)
                elif slotType == GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.shell]:
                    for shell in vehicle.shells.installed:
                        shells.append({'id': str(shell.intCD),
                        'type': shell.type,
                        'label': ITEM_TYPES.shell_kindsabbreviation(shell.type),
                        'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor.icon[0],
                        'count': shell.count,
                        'tooltip': '',
                        'tooltipType': TOOLTIPS_CONSTANTS.HANGAR_SHELL,
                        'slotLocked': vehicle.isLocked or not vehicle.isAlive})
                elif slotType == GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.equipment]:
                    for idx, equipment in enumerate(vehicle.consumables.installed):
                        if equipment is None:
                            equipSlot = EmptySlotVO(slotType)
                        else:
                            equipSlot = HangarFittingSlotVO([equipment], vehicle, slotType, tooltipType=TOOLTIPS_CONSTANTS.HANGAR_MODULE)
                            equipSlot['slotIndex'] = idx
                        consumables.append(equipSlot)
                elif slotType == 'battleBooster':
                    booster = vehicle.battleBoosters.installed[0]
                    if vehicle.battleBoosters.layoutCapacity == 0:
                        boosterSlot = EmptySlotVO(isDisabled=True)
                    elif booster is None:
                        boosterSlot = EmptySlotVO(slotType)
                    else:
                        boosterSlot = HangarFittingSlotVO([booster], vehicle, slotType, tooltipType=TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK)
                elif slotType == 'battleAbility':
                    for battleAbility in vehicle.battleAbilities.installed:
                        if battleAbility is None:
                            bASlot = EmptySlotVO('battleAbility')
                        else:
                            bASlot = HangarFittingSlotVO([battleAbility], vehicle, 'battleAbility', tooltipType=TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO)
                        battleAbilities.append(bASlot)
                else:
                    data = self.itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[slotType], REQ_CRITERIA.CUSTOM(lambda item: item.isInstalled(vehicle))).values()
                    moduleSlot = HangarFittingSlotVO(data, vehicle, slotType, tooltipType=TOOLTIPS_CONSTANTS.HANGAR_MODULE)
                    modules.append(moduleSlot)

            if len(shells) != 3:
                emptySlots = 3 - len(shells)
                for _ in range(0, emptySlots):
                    shells.append(EmptySlotVO(isDisabled=True))

            if vehicle.optDevices.layoutCapacity != 3:
                emptySlots = 3 - vehicle.optDevices.layoutCapacity
                for _ in range(0, emptySlots):
                    optionalDevices.append(EmptySlotVO(isDisabled=True))

            if vehicle.consumables.layoutCapacity != 3:
                emptySlots = 3 - vehicle.consumables.layoutCapacity
                for _ in range(0, emptySlots):
                    consumables.append(EmptySlotVO(isDisabled=True))

            ammunitionData['modules'] = modules
            ammunitionData['optionalDevice'] = optionalDevices
            ammunitionData['shells'] = shells
            ammunitionData['equipment'] = consumables
            ammunitionData['booster'] = boosterSlot
            ammunitionData['battleAbilities'] = battleAbilities

            self.as_setBattleAbilitiesVisible()
            self.flashObject.setupSlots(ammunitionData)

def _extendByArtefactData(targetData, module, slotIndex):
    assert module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS
    targetData['slotIndex'] = slotIndex
    targetData['removable'] = module.isRemovable
    targetData['name'] = text_styles.stats(module.userName)

def _extendByOptionalDeviceData(targetData, module):
    assert module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE
    targetData['desc'] = OptDeviceBonusesDescriptionBuilder().getDescription(module).replace("\n", "", 1) if OptDeviceBonusesDescriptionBuilder().getDescription(module).startswith("\n") else OptDeviceBonusesDescriptionBuilder().getDescription(module)
    overlay = module.getOverlayType()
    highlight = module.getHighlightType()
    _extendHighlightData(targetData, highlight, overlay)
    if module.isTrophy or module.isModernized:
        targetData['showPrice'] = False
        targetData['isTrophyOrModern'] = True
        targetData['isAvailable'] = module.isInInventory or module.isInstalled
        targetData['isUpgradable'] = module.isUpgradable

def _extendHighlightData(targetData, highlight, overlay):
    targetData['overlayType'] = overlay
    targetData['highlightType'] = highlight
    targetData['bgHighlightType'] = highlight

def _extendByBattleBoosterData(targetData, module, vehicle):
    assert module.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER
    overlay = module.getOverlayType()
    if module.isCrewBooster():
        skillLearnt = module.isAffectedSkillLearnt(vehicle)
        template = g_htmlTemplates['html_templates:lobby/popovers']['crewBattleBooster']
        desc = module.getCrewBoosterDescription(not skillLearnt, template.source)
        targetData['desc'] = text_styles.main(desc)
        highlight = SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER if skillLearnt else SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE
        _extendHighlightData(targetData, highlight, overlay)
    else:
        if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            targetData['notAffectedTTC'] = False
        else:
            targetData['notAffectedTTC'] = not module.isAffectsOnVehicle(vehicle)
        targetData['desc'] = text_styles.main(module.getOptDeviceBoosterDescription(vehicle, text_styles.bonusAppliedText))
        _extendHighlightData(targetData, SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER, overlay)
    targetData['count'] = module.inventoryCount
    targetData['removeButtonLabel'] = '#wek:boosterFittingSelect/removeButton'
    targetData['buyButtonLabel'] = '#wek:boosterFittingSelect/buyButton'
    targetData['buyButtonTooltip'] = ''
    targetData['buyButtonVisible'] = targetData['isSelected']

def _extendByBattleAbilityData(targetData, ability, slotIndex, mayInstall=False):
    filterText = ability.shortFilterAlert if targetData['disabled'] and not mayInstall else ''
    targetData['slotIndex'] = slotIndex
    targetData['desc'] = text_styles.main(ability.shortDescription)
    targetData['name'] = text_styles.stats(ability.userName)
    targetData['level'] = ability.level if ability.isUnlocked else 0
    targetData['removeButtonLabel'] = '#menu:buttonLabel/remove'
    targetData['changeOrderButtonLabel'] = 'NIGGER'
    targetData['filterText'] = filterText

def __isHintVisible(self):
    prefSetting = AccountSettings.getSettings(SHOW_OPT_DEVICE_HINT)
    return prefSetting and self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY_OR_UNLOCKED | REQ_CRITERIA.VEHICLE.LEVELS(range(4, 10)))

def getListOverlayData():
    icon = RES_ICONS.MAPS_ICONS_MODULES_MODERNIZEDOVERLAY
    data = {'listOverlay': {'iconBig': icon,
     'titleText': text_styles.highTitle('O CHOLERA'),
     'descText': 'CZY TO FREDDY FAZBEAR?',
     'okBtnLabel': 'UR UR UR UR UR UR UR'}}
    return None
    
def upgradeModule(self, moduleId):
    if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
        self._logicProvider.setModule(moduleId, -483, False, True)
        
def installModule(self, moduleId):
    if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
        installOptDevice(self, moduleId)
    elif self._slotType == FITTING_TYPES.BOOSTER:
        buyMoreBoosters(self, moduleId)

def buyMoreBoosters(self, moduleId):
    shop.showBattleBoosterOverlay(itemId=int(moduleId), source=shop.Source.EXTERNAL, origin=shop.Origin.BATTLE_BOOSTERS, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)
    return

def onManageBattleAbilitiesClicked(self):
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    hangar = app.containerManager.getContainer(WindowLayer.VIEW).getChildContainer(5).getView()
    hangar.as_showSwitchToAmmunitionS()
    shared_events.showAmmunitionSetupView(**{'selectedSlot': 0, 'selectedSection': 'battleAbilities'})
    self.destroy()
    
def setOnlyBattleAbilities(container, view):
    if view.alias == VIEW_ALIAS.AMMUNITION_SETUP_VIEW:
        BigWorld.callback(0.1, partial(setOnlyBattleAbilities_worker, view))
    
def setOnlyBattleAbilities_worker(view):
    tankSetupAmmoPanel = view.getComponent('ammunitionSetupViewInject').getInjectView().viewModel.ammunitionPanel
    slots = tankSetupAmmoPanel.getSectionGroups().getValue(2)
    tankSetupAmmoPanel.setSectionGroups(Array())
    tankSetupAmmoPanel.getSectionGroups().addViewModel(slots)

@decorators.adisp_process('loadStats')
def setAutoRearm(self, autoRearm):
    vehicle = self._getVehicle()
    if vehicle is not None and autoRearm != vehicle.isAutoBattleBoosterEquip():
        yield VehicleAutoBattleBoosterEquipProcessor(vehicle, autoRearm).request()
    return

def installOptDevice(self, moduleId):
    copyVehicle = g_currentVehicle.item
    module = copyVehicle.itemsCache.items.getItemByCD(int(moduleId))
    devSlot = self._getSlotIndex()
    installedOptDevice = g_currentVehicle.item.optDevices.installed[devSlot]
    installedOptDeviceID = installedOptDevice.intCD if installedOptDevice is not None else -1
    copyVehicle.optDevices.layout[devSlot] = module
    onlyExchange = module.isInInventory
    if installedOptDeviceID > 0:
        ItemsActionsFactory.doAction(ItemsActionsFactory.REMOVE_OPT_DEVICE, g_currentVehicle.item, installedOptDevice, devSlot, forFitting=True)
        return
    ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, copyVehicle, onlyExchange)
    return

print '[OMNILAB R&D: views.LegacyAmmoPanel] INITIALIZED!'