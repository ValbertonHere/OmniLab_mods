from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from CurrentVehicle import g_currentVehicle
from adisp import adisp_process
from debug_utils import LOG_CURRENT_EXCEPTION
from items import getTypeInfoByName
from realm import CURRENT_REALM

from helpers import dependency
from helpers.i18n import makeString

from gui.impl.gen import R
from gui.impl import backport

from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta

from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel import AmmunitionPanel
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.view.lobby.hangar.entry_points.event_entry_points_container import EventEntryPointsContainer
from gui.Scaleform.daapi.view.lobby.header.BattleTypeSelectPopover import BattleTypeSelectPopover
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SquadItem, _R_BATTLE_TYPES
from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel import AmmunitionPanel
from gui.Scaleform.daapi.view.lobby.hangar.daily_quest_widget import DailyQuestWidget
from gui.Scaleform.daapi.view.lobby.hangar.ResearchPanel import ResearchPanel
from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import ModuleFittingSelectPopover, _POPOVER_FIRST_TAB_IDX, _POPOVER_SECOND_TAB_IDX, CommonFittingSelectPopover, _HangarLogicProvider, PopoverLogicProvider, _extendByModuleData

from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.formatters import text_styles
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shared.utils.requesters import REQ_CRITERIA

from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS

from skeletons.gui.app_loader import IAppLoader

from .views.legacy_ammopanel import GameControllers, setOnlyBattleAbilities, upgradeModule, installModule, setAutoRearm, onManageBattleAbilitiesClicked, getListOverlayData
from .views.legacy_ammopanel import _extendByArtefactData, _extendByBattleAbilityData, _extendByBattleBoosterData, _extendByOptionalDeviceData
from .utils import override

__all__ = ()
initLoad = True

"""
LEGACY AMMOPANEL OVERRIDES
"""

_TAB_IDS = (0, 1)

_OPTDEV_TABS = [{'label': '#tank_setup:tabs/simple', 'id': 'simpleOptDevices'}, 
         {'label': '#tank_setup:tabs/deluxe', 'id': 'deluxeOptDevices'}]

_BOOST_TABS = [{'label': '#tank_setup:tabs/optDevice', 'id': 'boostersForAmmunition'}, 
  {'label': '#tank_setup:tabs/crew', 'id': 'boostersForCrew'}]

@override(AmmunitionPanel, '_populate')
def AmmunitionPanel_populate(base, self):
    base(self)
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    if setOnlyBattleAbilities not in app.containerManager.onViewAddedToContainer:
        app.containerManager.onViewAddedToContainer += setOnlyBattleAbilities

@override(ModuleFittingSelectPopover, '_dispose')
def ModuleFittingSelectPopover_dispose(base, self):
    global initLoad
    
    initLoad = True
    base(self)

@override(ModuleFittingSelectPopover, '__init__')
def ModuleFittingSelectPopover__init__(base, self, ctx=None, customProviderClass=None):
    base(self, ctx, customProviderClass)
    global initLoad

    try:
        initLoad = True
        self.__class__.upgradeVehicleModule = upgradeModule
        self.__class__.buyVehicleModule = installModule
        self.__class__.setAutoRearm = setAutoRearm
        self.__class__.onManageBattleAbilitiesClicked = onManageBattleAbilitiesClicked
    except:
        LOG_CURRENT_EXCEPTION()

@override(PopoverLogicProvider, '_PopoverLogicProvider__extendByTypeSpecificData')
def PopoverLogicProvider__extendByTypeSpecificData(base, self, moduleData, module):
    if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
        _extendByArtefactData(moduleData, module, self._slotIndex)
    elif module.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
        _extendByModuleData(moduleData, module, self._vehicle.descriptor, self._PopoverLogicProvider__moduleExtenders)
    if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
        _extendByOptionalDeviceData(moduleData, module)
    elif self._slotType == FITTING_TYPES.BOOSTER:
        _extendByBattleBoosterData(moduleData, module, self._vehicle)
    elif self._slotType == FITTING_TYPES.BATTLE_ABILITY:
        mayInstall, _ = module.mayInstall(self._vehicle)
        _extendByBattleAbilityData(moduleData, module, self._slotIndex, mayInstall)

@override(CommonFittingSelectPopover, '_getCommonData')
def CommonFittingSelectPopover_getCommonData(base, self):
    if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
        rendererName = 'OptDeviceFittingItemRendererUI'
        rendererDataClass = 'omnilab.wotclassic.legacyAmmoPanel.data.LegacyOptDeviceVO'
        width = FITTING_TYPES.LARGE_POPOVER_WIDTH
        title = '#wek:optDeviceFittingSelect/title'
    elif self._slotType == FITTING_TYPES.BOOSTER:
        rendererName = 'BoosterFittingItemRendererUI'
        rendererDataClass = 'omnilab.wotclassic.legacyAmmoPanel.data.LegacyBoosterVO'
        width = FITTING_TYPES.LARGE_POPOVER_WIDTH
        title = '#wek:boosterFittingSelect/title'
    elif self._slotType == FITTING_TYPES.BATTLE_ABILITY:
        rendererName = 'BattleAbilityItemRendererUI'
        rendererDataClass = 'omnilab.wotclassic.legacyAmmoPanel.data.LegacyBattleAbilityVO'
        width = FITTING_TYPES.SHORT_POPOVER_WIDTH
        title = '#menu:battleAbility/title'
    else:
        if self._slotType == FITTING_TYPES.VEHICLE_WHEELED_CHASSIS:
            self._slotType = 'vehicleChassis'
        title = makeString(MENU.MODULEFITS_TITLE, moduleName=getTypeInfoByName(self._slotType)['userString'], vehicleName=self._getVehicle().userName if self._getVehicle() is not None else '')
        rendererDataClass = 'omnilab.wotclassic.legacyAmmoPanel.data.LegacyModuleVO'
        if self._slotType == FITTING_TYPES.VEHICLE_ENGINE:
            if self._getVehicle().descriptor.hasTurboshaftEngine or self._getVehicle().descriptor.hasRocketAcceleration:
                rendererName = FITTING_TYPES.ENGINE_FITTING_BIG_ITEM_RENDERER
            else:
                rendererName = FITTING_TYPES.ENGINE_FITTING_ITEM_RENDERER
            width = FITTING_TYPES.MEDUIM_POPOVER_WIDTH
        elif self._slotType == FITTING_TYPES.VEHICLE_CHASSIS_OVERRIDE:
            rendererName = FITTING_TYPES.CHASSIS_FITTING_ITEM_RENDERER
            width = FITTING_TYPES.MEDUIM_POPOVER_WIDTH
        elif self._slotType == FITTING_TYPES.VEHICLE_RADIO:
            rendererName = FITTING_TYPES.RADIO_FITTING_ITEM_RENDERER
            width = FITTING_TYPES.SHORT_POPOVER_WIDTH
        else:
            rendererName = FITTING_TYPES.GUN_TURRET_FITTING_ITEM_RENDERER
            width = FITTING_TYPES.LARGE_POPOVER_WIDTH

    return (rendererName, rendererDataClass, width, title)

@override(CommonFittingSelectPopover, '_prepareInitialData')
def CommonFittingSelectPopover_prepareInitialData(base, self):
    rendererName, rendererDataClass, width, title = self._getCommonData()
    result = {'title': text_styles.highTitle(title), 
        'rendererName': rendererName, 
        'rendererDataClass': rendererDataClass,
        'scrollToIndex': self._logicProvider.getSelectedIdx(), 
        'selectedIndex': self._logicProvider.getSelectedIdx(), 
        'availableDevices': self._logicProvider.getDevices(),
        'rearmCheckboxVisible': self._slotType == FITTING_TYPES.BOOSTER,
        'rearmCheckboxValue': self._getVehicle().isAutoBattleBoosterEquip() if self._slotType == FITTING_TYPES.BOOSTER else False,
        'battleAbilitiesButtonVisible': self._slotType == FITTING_TYPES.BATTLE_ABILITY,
        'width': width}
    if getListOverlayData() is not None:
        result.update(getListOverlayData())
    result.update(self._getTabsData())
    return result

@override(CommonFittingSelectPopover, 'setCurrentTab')
def CommonFittingSelectPopover_setCurrentTab(base, self, tabIndex):
    if tabIndex not in _TAB_IDS:
        return
    self._logicProvider.setTab(tabIndex)
    if tabIndex != self._getInitialTabIndex():
        self._saveTabIndex(tabIndex)
    self.as_updateS(self._prepareInitialData())

@override(CommonFittingSelectPopover, '_getTabsData')
def CommonFittingSelectPopover_getTabsData(base, self):
    if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
        return {'tabData': _OPTDEV_TABS, 'selectedTab': self._getInitialTabIndex()}
    elif self._slotType == FITTING_TYPES.BOOSTER:
        return {'tabData': _BOOST_TABS, 'selectedTab': self._getInitialTabIndex()}
    else: return {}

@override(CommonFittingSelectPopover, '_getInitialTabIndex')
def CommonFittingSelectPopover_getInitialTabIndex(base, self):
    global initLoad
    
    if not initLoad:
        return self._TAB_IDX
    else:
        initLoad = False
        if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
            vehicle = self._getVehicle()
            if vehicle is None:
                return self._TAB_IDX
            installedDevice = vehicle.optDevices.installed[self._getSlotIndex()]
            if installedDevice is not None:
                self._saveTabIndex(_POPOVER_FIRST_TAB_IDX)
                if installedDevice.isDeluxe:
                    self._saveTabIndex(_POPOVER_SECOND_TAB_IDX)
        elif self._slotType == FITTING_TYPES.BOOSTER:
            vehicle = self._getVehicle()
            if vehicle is None:
                return self._TAB_IDX
            battleBooster = vehicle.battleBoosters.installed[self._getSlotIndex()]
            if battleBooster is not None:
                self._saveTabIndex(_POPOVER_FIRST_TAB_IDX)
                if battleBooster.isCrewBooster():
                    self._saveTabIndex(_POPOVER_SECOND_TAB_IDX)
        return self._TAB_IDX

@override(_HangarLogicProvider, '_getSpecificCriteria')
def HangarLogicProvider_getSpecificCriteria(base, self, typeID):
    if typeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
        criteria = REQ_CRITERIA.BATTLE_BOOSTER.OPTIONAL_DEVICE_EFFECT if self._tabIndex == _POPOVER_FIRST_TAB_IDX else REQ_CRITERIA.BATTLE_BOOSTER.CREW_EFFECT
    elif typeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        criteria = REQ_CRITERIA.CUSTOM(lambda item: not item.isDeluxe and not ((item.isTrophy or item.isModernized) and item.inventoryCount == 0 and not item.isInstalled(self._vehicle))) if self._tabIndex == _POPOVER_FIRST_TAB_IDX else REQ_CRITERIA.OPTIONAL_DEVICE.DELUXE
    elif typeID == GUI_ITEM_TYPE.BATTLE_ABILITY:
        skillItemIDs = []
        allSkills = GameControllers.epicMetaGameCtrl.getAllSkillsInformation().values()
        for skillInfo in allSkills:
            if skillInfo.category in self._vehicle.battleAbilities.slots[self._slotIndex].tags:
                skillExample = skillInfo.levels[1]
                skillItemIDs.append(skillExample.eqID)

        criteria = REQ_CRITERIA.CUSTOM(lambda item: item.innationID in skillItemIDs)
    else:
        criteria = REQ_CRITERIA.EMPTY
    return criteria

@override(_HangarLogicProvider, '_buildModuleData')
def HangarLogicProvider_buildModuleData(base, self, vehicleModule, isInstalledInSlot, stats):
    if self._slotType != FITTING_TYPES.BATTLE_ABILITY:
        baseData = base(self, vehicleModule, isInstalledInSlot, stats)
        isFit, reason = vehicleModule.mayInstall(self._vehicle, self._slotIndex)
        if reason == 'already installed':
            isFit = True
        baseData['disabled'] = not isFit
        return baseData
    else:
        baseData = base(self, vehicleModule, isInstalledInSlot, stats)
        baseData['disabled'] = not vehicleModule.isUnlocked
        baseData['showPrice'] = False
        return baseData


@override(_HangarLogicProvider, '_buildList')
def HangarLogicProvider_buildList(base, self):
    modulesList = []
    self._tooltipType = TOOLTIPS_CONSTANTS.HANGAR_MODULE
    if self._slotType == FITTING_TYPES.VEHICLE_WHEELED_CHASSIS:
        self._slotType = 'vehicleChassis'
    elif self._slotType == FITTING_TYPES.BOOSTER:
        self._tooltipType = TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK
    elif self._slotType == FITTING_TYPES.BATTLE_ABILITY:
        self._tooltipType = TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO
    if self._vehicle is not None:
        typeId = GUI_ITEM_TYPE_INDICES[self._slotType]
        data = self._getSuitableItems(typeId)
        currXp = self._itemsCache.items.stats.vehiclesXPs.get(self._vehicle.intCD, 0)
        stats = {'money': self._itemsCache.items.stats.money,
        'exchangeRate': self._itemsCache.items.shop.exchangeRate, 
        'currXP': currXp, 
        'totalXP': currXp + self._itemsCache.items.stats.freeXP}
        for idx, vehicleModule in enumerate(data):
            if self._slotType != FITTING_TYPES.BATTLE_ABILITY:
                isInstalled = vehicleModule.isInstalled(self._vehicle, self._slotIndex)
                if isInstalled:
                    self._selectedIdx = idx
            else:
                isInstalled = vehicleModule.isInstalled(self._vehicle)
            if typeId == GUI_ITEM_TYPE_INDICES['optionalDevice']:
                inventoryVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
                isInOtherVehicles = len(vehicleModule.getInstalledVehicles(inventoryVehicles.itervalues())) > 0 and not vehicleModule.isInInventory
                isAvailable = vehicleModule.isInInventory or isInstalled
                isTrophyOrModern = vehicleModule.isTrophy or vehicleModule.isModernized
                if ((isTrophyOrModern and not isInOtherVehicles) or (vehicleModule.isHidden and vehicleModule.isDeluxe)) and not isAvailable:
                    continue
            moduleData = self._buildModuleData(vehicleModule, isInstalled, stats)
            if typeId == GUI_ITEM_TYPE_INDICES['optionalDevice'] and isInOtherVehicles and isTrophyOrModern:
                moduleData.update({'target': 'vehicle', 'targetVisible': True})
            self._PopoverLogicProvider__extendByTypeSpecificData(moduleData, vehicleModule)
            modulesList.append(moduleData)
    return modulesList

@override(_HangarLogicProvider, 'setModule')
def HangarLogicProvider_setModule(base, self, newId, oldId, isRemove, isUpgrade=False):
    newItem = self._itemsCache.items.getItemByCD(int(newId))
    if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
        isRemoving = newId == oldId and isRemove
        isDestroy = oldId < 0 and isRemove
        isTrophyOrModern = newItem.isTrophy or newItem.isModernized
        installedOptDevice = g_currentVehicle.item.optDevices.installed[self._slotIndex]
        print newId, oldId
        if isRemoving:
            ItemsActionsFactory.doAction(ItemsActionsFactory.REMOVE_OPT_DEVICE, self._vehicle, installedOptDevice, self._slotIndex)
            return
        elif isDestroy and isTrophyOrModern:
            ItemsActionsFactory.doAction(ItemsActionsFactory.DECONSTRUCT_OPT_DEVICE, newItem, self._vehicle, self._slotIndex, None)
            return
        elif isDestroy and not isTrophyOrModern:
            ItemsActionsFactory.doAction(ItemsActionsFactory.REMOVE_OPT_DEVICE, self._vehicle, installedOptDevice, self._slotIndex, True)
            return
        elif isUpgrade:
            ItemsActionsFactory.doAction(ItemsActionsFactory.UPGRADE_OPT_DEVICE, newItem, None, None, None)
            return
        elif isTrophyOrModern:
            return
        elif newItem.isInstalled(self._vehicle):
            copyVehicle = self._vehicle
            for idx, optDevice in enumerate(self._vehicle.optDevices.installed):
                if optDevice is None:
                    continue
                elif optDevice.intCD == newItem.intCD:
                    copyVehicle.optDevices.swap(self._slotIndex, idx)
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, copyVehicle, True)
        else:
            copyVehicle = self._vehicle
            copyVehicle.optDevices.layout[self._slotIndex] = newItem
            onlyExchange = newItem.isInInventory
            if oldId > 0:
                ItemsActionsFactory.doAction(ItemsActionsFactory.REMOVE_OPT_DEVICE, self._vehicle, installedOptDevice, self._slotIndex, forFitting=True)
                return
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, copyVehicle, onlyExchange)
            return
    elif self._slotType == FITTING_TYPES.BOOSTER:
        copyVehicle = self._vehicle
        onlyExchange = newItem.isInInventory
        if isRemove:
            copyVehicle.battleBoosters.layout[self._slotIndex] = None
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_BATTLE_BOOSTERS, copyVehicle, onlyExchange)
            return
        
        copyVehicle.battleBoosters.layout[self._slotIndex] = newItem
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_BATTLE_BOOSTERS, copyVehicle, oldId < 0)
        return
    elif self._slotType == FITTING_TYPES.BATTLE_ABILITY:
        copyVehicle = self._vehicle
        copyVehicle.battleAbilities.layout[self._slotIndex] = newItem
        ItemsActionsFactory.doAction(ItemsActionsFactory.INSTALL_BATTLE_ABILITIES, copyVehicle, skipConfirm=True)
        return

    if newItem.isInInventory:
        ItemsActionsFactory.doAction(ItemsActionsFactory.INSTALL_ITEM, int(newId), self._vehicle.intCD)
    elif newItem.isUnlocked:
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_AND_SELL_ITEM, int(newId), self._vehicle.intCD)

    return

"""
LEGACY HANGAR OVERRIDES
"""

@override(Hangar, '_populate')
def Hangar__populate(base, self):
    base(self)
    
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()

    app.loadView(SFViewLoadParams('LegacyHangarUI'))

@override(Hangar, '_Hangar__onTeaserReceived')
def Hangar__onTeaserReceived(base, self, teaserData, showCallback, closeCallback):
    self._Hangar__teaser = None
    return 

@override(Hangar, 'hideTeaser')
def Hangar_hideTeaser(base, self):
    self._Hangar__teaser = None
    return 

@override(EventEntryPointsContainer, 'as_updateEntriesS')
def EventEntryPointsContainer_as_updateEntriesS(base, self, data):
    base(self, [])

@override(ResearchPanel, 'as_updateCurrentVehicleS')
def ResearchPanel_as_updateCurrentVehicleS(base, self, _):
    if g_currentVehicle.isPresent():
        base(self, {'earnedXP': 0, 
                'isElite': False, 
                'vehCompareData': {'modeAvailable': False, 'btnEnabled': False, 'btnTooltip': ''}, 
                'vehPostProgressionData': {'showCounter': False, 'btnEnabled': False, 'btnVisible': False}, 
                'intCD': g_currentVehicle.item.intCD})
    else:
        base(self, {'earnedXP': 0})

@override(AmmunitionPanelMeta, 'as_updateVehicleStatusS')
def AmmunitionPanelMeta_as_updateVehicleStatusS(base, self, data):
    message = '<font face="$TitleFont" size="20" color="#497212">%s</font>' % g_currentVehicle.getHangarMessage()[1]

    if g_currentVehicle.getHangarMessage()[0] != 'undamaged':
        message = '<font face="$TitleFont" size="20" color="#9b0202">%s</font>' % g_currentVehicle.getHangarMessage()[1]

    data = {'message': message,
                'rentAvailable': '',
                'isElite': False,
                'tankType': '',
                'vehicleLevel': '',
                'vehicleName': '',
                'roleId': '',
                'roleMessage': '', 
                'vehicleCD': ''}
    base(self, data)

@override(AmmunitionPanel, 'showRepairDialog')
def AmmunitionPanel_showRepairDialog(base, self):
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    app.loadView(SFViewLoadParams('TechnicalMaintenance'))

def Hangar_as_setPrestigeWidgetVisibleS(self, visible):
    base(self, False)

if CURRENT_REALM != 'RU':
    base = Hangar.as_setPrestigeWidgetVisibleS
    Hangar.as_setPrestigeWidgetVisibleS = Hangar_as_setPrestigeWidgetVisibleS

"""
LEGACY LOBBYHEADER OVERRIDES
"""

LEGACY_HEADER_TABS = (LobbyHeader.TABS.HANGAR, LobbyHeader.TABS.STORE, LobbyHeader.TABS.PROFILE, LobbyHeader.TABS.TECHTREE, LobbyHeader.TABS.BARRACKS, LobbyHeader.TABS.BROWSER, 
                      LobbyHeader.TABS.RESEARCH, LobbyHeader.TABS.PERSONAL_MISSIONS, LobbyHeader.TABS.PERSONAL_MISSIONS_PAGE)

@override(LobbyHeader, '_populate')
def LobbyHeader_populate(base, self):
    base(self)
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    app.graphicsOptimizationManager.switchOptimizationEnabled(False)
    app.loadView(SFViewLoadParams('LegacyLobbyHeaderUI'))

@override(BattleTypeSelectPopover, 'as_updateS')
def BattleTypeSelectPopover_as_updateS(base, self, items, extraItems, isShowDemonstrator, demonstratorEnabled):
    squad = _SquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.simpleSquad())), PREBATTLE_ACTION_NAME.SQUAD, 0)
    items.insert(1, squad.getVO())
    base(self, items, extraItems, isShowDemonstrator, demonstratorEnabled)

@override(BattleTypeSelectPopover, '_BattleTypeSelectPopover__selectFight')
@adisp_process
def BattleTypeSelectPopover__selectFight(base, self, actionName):
    if actionName == 'squad':
        prbDispatcher = g_prbLoader.getDispatcher()
        yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.SQUAD))
    else:
        base(self, actionName)

@override(LobbyHeader, '_LobbyHeader__setCounter')
def LobbyHeader__setCounter(base, self, alias, counter=None):
    if alias in LEGACY_HEADER_TABS:
        base(self, alias, counter)
    else: pass

@override(LobbyHeader, '_LobbyHeader__hideCounter')
def LobbyHeader__hideCounter(base, self, alias):
    if alias in LEGACY_HEADER_TABS:
        base(self, alias)
    else: pass

@override(LobbyHeader, '_getHangarMenuItemDataProvider')
def LobbyHeader_getHangarMenuItemDataProvider(base, self):
    tabDataProvider = [
     {'label': MENU.HEADERBUTTONS_HANGAR, 
        'value': self.TABS.HANGAR, 
        'textColor': 16764006,
        'textColorOver': 16768409, 
        'tooltip': TOOLTIPS.HEADER_BUTTONS_HANGAR},
     {'label': MENU.HEADERBUTTONS_STORAGE, 
        'value': self.TABS.STORAGE, 
        'tooltip': TOOLTIPS.HEADER_BUTTONS_STORAGE},
     {'label': MENU.HEADERBUTTONS_SHOP, 
        'value': self.TABS.STORE, 
        'tooltip': TOOLTIPS.HEADER_BUTTONS_SHOP},
     self._getPersonalMissionSelectorTabData()]
    tabDataProvider.append({'label': MENU.HEADERBUTTONS_PROFILE, 
       'value': self.TABS.PROFILE, 
       'tooltip': TOOLTIPS.HEADER_BUTTONS_PROFILE})
    techTreeData = {'label': MENU.HEADERBUTTONS_TECHTREE, 
       'value': self.TABS.TECHTREE, 
       'tooltip': TOOLTIPS.HEADER_BUTTONS_TECHTREE, 
       'isTooltipSpecial': False, 
       'subValues': [
                   self.TABS.RESEARCH]}
    if self.techTreeEventsListener.actions:
        techTreeData['tooltip'] = TOOLTIPS_CONSTANTS.TECHTREE_DISCOUNT_INFO
        techTreeData['isTooltipSpecial'] = True
        if self.techTreeEventsListener.getNations(unviewed=True):
            techTreeData['actionIcon'] = backport.image(R.images.gui.maps.icons.library.discountIndicator())
    tabDataProvider.extend([techTreeData])
    tabDataProvider.extend([
     {'label': MENU.HEADERBUTTONS_BARRACKS, 
        'value': self.TABS.BARRACKS, 
        'tooltip': TOOLTIPS.HEADER_BUTTONS_BARRACKS}])
    tournamentsData = self._getTournamentsSelectorData()
    tournamentsData = None
    if tournamentsData is not None:
        tabDataProvider.append(tournamentsData)
    if CURRENT_REALM == 'RU':
        override = self._tutorialLoader.gui.lastHangarMenuButtonsOverride
        if override is not None:
            tabDataProvider[:] = filter(lambda item: item['value'] in override, tabDataProvider)
    return tabDataProvider

@override(DailyQuestWidget, '_DailyQuestWidget__show')
def DailyQuestWidget__show(base, self):
    base(self)
    self._DailyQuestWidget__hide()

@override(CachedBlur, 'enable')
def CachedBlur_enable(base, self):
    self._switchEnabled(False)

@override(LobbyHeader, 'as_updateOnlineCounterS')
def LobbyHeader_as_updateOnlineCounterS(base, self, clusterStats, regionStats, tooltip, isAvailable):
    clusterUsers, regionUsers, _ = self.serverStats.getStats()
    clusterUsers = '%s / %s' % (clusterUsers, regionUsers)
    base(self, clusterUsers, '', None, isAvailable)

@override(LobbyHeader, '_populateButtons')
def LobbyHeader_populateButtons(base, self):
    if CURRENT_REALM == 'RU' and hasattr(self, '_tutorialLoader'):
        if self._tutorialLoader.gui.lastHeaderMenuButtonsOverride is not None:
            self._LobbyHeader__onOverrideHeaderMenuButtons()
            return
    else:
        buttonsToExclude = []
        for i in self.BUTTONS.ALL():
            buttonsToExclude.append(i)
        self.as_setHeaderButtonsS(self._getAvailableButtons(buttonsToExclude))
        return