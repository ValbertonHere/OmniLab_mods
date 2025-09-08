from adisp import adisp_process
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_CURRENT_EXCEPTION
from items import getTypeInfoByName
# from realm import CURRENT_REALM

from helpers import dependency
from helpers.i18n import makeString

from gui.impl.gen import R
from gui.impl import backport
from gui.impl.lobby.platoon.platoon_config import QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME

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

from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.managers.optimization_manager import GraphicsOptimizationManager

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
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IPlatoonController

from lobby_views.legacy_ammopanel import setOnlyBattleAbilities, upgradeModule, installModule, setAutoRearm, onManageBattleAbilitiesClicked, getListOverlayData
from lobby_views.legacy_ammopanel import _extendByArtefactData, _extendByBattleAbilityData, _extendByBattleBoosterData, _extendByOptionalDeviceData
from lobby_views import getGUIConfig
from utils import override

__all__ = ()

"""
LEGACY AMMOPANEL OVERRIDES
"""

class LegacyAmmoPanelHooks():
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    itemsCache = dependency.instance(IItemsCache)
    appLoader = dependency.instance(IAppLoader)

    _TAB_IDS = (0, 1)
    _OPTDEV_TABS = [{'label': '#tank_setup:tabs/simple', 'id': 'simpleOptDevices'}, 
            {'label': '#tank_setup:tabs/deluxe', 'id': 'deluxeOptDevices'}]
    _BOOST_TABS = [{'label': '#tank_setup:tabs/optDevice', 'id': 'boostersForAmmunition'}, 
    {'label': '#tank_setup:tabs/crew', 'id': 'boostersForCrew'}]

    def __init__(self):
        self._initload = True

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

    def _AmmunitionPanel_populate(self, base, baseSelf):
        base(baseSelf)
        app = self.appLoader.getApp()
        if setOnlyBattleAbilities not in app.containerManager.onViewAddedToContainer:
            app.containerManager.onViewAddedToContainer += setOnlyBattleAbilities

    def _ModuleFittingSelectPopover_dispose(self, base, baseSelf):
        self._initload = True
        base(baseSelf)

    def _ModuleFittingSelectPopover__init__(self, base, baseSelf, ctx=None, customProviderClass=None):
        base(baseSelf, ctx, customProviderClass)
        try:
            baseSelf.__class__.upgradeVehicleModule = upgradeModule
            baseSelf.__class__.buyVehicleModule = installModule
            baseSelf.__class__.setAutoRearm = setAutoRearm
            baseSelf.__class__.onManageBattleAbilitiesClicked = onManageBattleAbilitiesClicked
        except:
            LOG_CURRENT_EXCEPTION()

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
        if not self._initload:
            return baseSelf._TAB_IDX
        else:
            self._initload = False
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
            currXp = self.itemsCache.items.stats.vehiclesXPs.get(baseSelf._vehicle.intCD, 0)
            stats = {'money': self.itemsCache.items.stats.money,
            'exchangeRate': self.itemsCache.items.shop.exchangeRate, 
            'currXP': currXp, 
            'totalXP': currXp + self.itemsCache.items.stats.freeXP}
            for idx, vehicleModule in enumerate(data):
                if baseSelf._slotType != FITTING_TYPES.BATTLE_ABILITY:
                    isInstalled = vehicleModule.isInstalled(baseSelf._vehicle, baseSelf._slotIndex)
                    if isInstalled:
                        baseSelf._selectedIdx = idx
                else:
                    isInstalled = vehicleModule.isInstalled(baseSelf._vehicle)
                if typeId == GUI_ITEM_TYPE_INDICES['optionalDevice']:
                    inventoryVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
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
        newItem = self.itemsCache.items.getItemByCD(int(newId))
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
            
            copyVehicle.battleBoosters.layout[baseSelf._slotIndex] = newItem
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

g_ammoPanelHooks = LegacyAmmoPanelHooks()

"""
LEGACY HANGAR OVERRIDES
"""
class LegacyHangarHooks():
    appLoader = dependency.instance(IAppLoader)

    def __init__(self):

        override(Hangar, '_populate', self._Hangar__populate)
        override(Hangar, '_Hangar__onTeaserReceived', self._Hangar__onTeaserReceived)
        override(Hangar, 'hideTeaser', self._Hangar_hideTeaser)
        override(EventEntryPointsContainer, 'as_updateEntriesS', self._EventEntryPointsContainer_as_updateEntriesS)
        override(ResearchPanel, 'as_updateCurrentVehicleS', self._ResearchPanel_as_updateCurrentVehicleS)
        override(AmmunitionPanelMeta, 'as_updateVehicleStatusS', self._AmmunitionPanelMeta_as_updateVehicleStatusS)
        override(AmmunitionPanel, 'showRepairDialog', self._AmmunitionPanel_showRepairDialog)
        override(GraphicsOptimizationManager, 'switchOptimizationEnabled', self._GraphicsOptimizationManager__switchOptimizationEnabled)
        # if CURRENT_REALM != 'RU':
        #     override(Hangar, 'as_setPrestigeWidgetVisibleS', self._Hangar_as_setPrestigeWidgetVisibleS)

    def _Hangar__populate(self, base, baseSelf):
        base(baseSelf)
        
        app = self.appLoader.getApp()
        app.loadView(SFViewLoadParams('LegacyHangarUI'))

    def _Hangar__onTeaserReceived(self, base, baseSelf, teaserData, showCallback, closeCallback):
        baseSelf._Hangar__teaser = None
        return 

    def _Hangar_hideTeaser(self, base, baseSelf):
        baseSelf._Hangar__teaser = None
        return 

    def _EventEntryPointsContainer_as_updateEntriesS(self, base, baseSelf, data):
        base(baseSelf, [])

    def _ResearchPanel_as_updateCurrentVehicleS(self, base, baseSelf, _):
        if g_currentVehicle.isPresent():
            base(baseSelf, {'earnedXP': 0, 
                    'isElite': False, 
                    'vehCompareData': {'modeAvailable': False, 'btnEnabled': False, 'btnTooltip': ''}, 
                    'vehPostProgressionData': {'showCounter': False, 'btnEnabled': False, 'btnVisible': False}, 
                    'intCD': g_currentVehicle.item.intCD})
        else:
            base(baseSelf, {'earnedXP': 0})

    def _AmmunitionPanelMeta_as_updateVehicleStatusS(self, base, baseSelf, data):
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
        base(baseSelf, data)

    def _AmmunitionPanel_showRepairDialog(self, base, baseSelf):
        app = self.appLoader.getApp()
        app.loadView(SFViewLoadParams('TechnicalMaintenance'))

    def _Hangar_as_setPrestigeWidgetVisibleS(self, base, baseSelf, visible):
        base(baseSelf, False)

    def _GraphicsOptimizationManager__switchOptimizationEnabled(self, base, baseSelf, isVisible):
        base(baseSelf, False)


g_hangarHooks = LegacyHangarHooks()

"""
LEGACY LOBBYHEADER OVERRIDES
"""

class LegacyLobbyHeaderHooks():
    appLoader = dependency.instance(IAppLoader)
    platoonCtrl = dependency.descriptor(IPlatoonController)

    LEGACY_HEADER_TABS = (LobbyHeader.TABS.HANGAR, LobbyHeader.TABS.STORE, LobbyHeader.TABS.PROFILE, LobbyHeader.TABS.TECHTREE, LobbyHeader.TABS.BARRACKS, LobbyHeader.TABS.BROWSER, 
                        LobbyHeader.TABS.RESEARCH, LobbyHeader.TABS.PERSONAL_MISSIONS, LobbyHeader.TABS.PERSONAL_MISSIONS_PAGE)

    def __init__(self):
        override(LobbyHeader, '_populate', self._LobbyHeader_populate)
        override(LobbyHeader, 'as_hideMenuS', self._LobbyHeader_as_hideMenuS)
        override(LobbyHeader, 'as_toggleVisibilityMenuS', self._LobbyHeader_as_toggleVisibilityMenuS)
        override(BattleTypeSelectPopover, 'as_updateS', self._BattleTypeSelectPopover_as_updateS)
        override(BattleTypeSelectPopover, '_BattleTypeSelectPopover__selectFight', self._BattleTypeSelectPopover__selectFight)
        override(CachedBlur, 'enable', self._CachedBlur_enable)
        override(DailyQuestWidget, '_DailyQuestWidget__show', self._DailyQuestWidget__show)
        override(LobbyHeader, '_populateButtons', self._LobbyHeader_populateButtons)
        override(LobbyHeader, '_LobbyHeader__setCounter', self._LobbyHeader__setCounter)
        override(LobbyHeader, '_LobbyHeader__hideCounter', self._LobbyHeader__hideCounter)
        override(LobbyHeader, '_getHangarMenuItemDataProvider', self._LobbyHeader_getHangarMenuItemDataProvider)

    def _LobbyHeader_populate(self, base, baseSelf):
        base(baseSelf)
        app = self.appLoader.getApp()
        app.loadView(SFViewLoadParams('LegacyLobbyHeaderUI'))

    def _LobbyHeader_as_hideMenuS(self, base, baseSelf, visible):
        base(baseSelf, True)

    def _LobbyHeader_as_toggleVisibilityMenuS(self, base, baseSelf, state):
        base(baseSelf, 7)

    def _BattleTypeSelectPopover_as_updateS(self, base, baseSelf, items, extraItems, isShowDemonstrator, demonstratorEnabled):
        squad = _SquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.simpleSquad())), PREBATTLE_ACTION_NAME.SQUAD, 0)
        squad.setLocked(self.platoonCtrl.getQueueType() not in QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME)
        items.insert(1, squad.getVO())
        base(baseSelf, items, extraItems, isShowDemonstrator, demonstratorEnabled)

    @adisp_process
    def _BattleTypeSelectPopover__selectFight(self, base, baseSelf, actionName):
        if actionName == 'squad':
            prbDispatcher = g_prbLoader.getDispatcher()
            prbActionName = QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME[self.platoonCtrl.getQueueType()]
            yield prbDispatcher.doSelectAction(PrbAction(prbActionName))
        else:
            base(baseSelf, actionName)

    def _LobbyHeader__setCounter(self, base, baseSelf, alias, counter=None):
        if alias in self.LEGACY_HEADER_TABS:
            if alias in (LobbyHeader.TABS.PERSONAL_MISSIONS, LobbyHeader.TABS.PERSONAL_MISSIONS_PAGE) and not getGUIConfig()['showPersonalQuests']:
                return
            base(baseSelf, alias, counter)
        else: pass

    def _LobbyHeader__hideCounter(self, base, baseSelf, alias):
        if alias in self.LEGACY_HEADER_TABS:
            if alias in (LobbyHeader.TABS.PERSONAL_MISSIONS, LobbyHeader.TABS.PERSONAL_MISSIONS_PAGE) and not getGUIConfig()['showPersonalQuests']:
                return
            base(baseSelf, alias)
        else: pass

    def _LobbyHeader_getHangarMenuItemDataProvider(self, base, baseSelf):
        tabDataProvider = [
        {'label': MENU.HEADERBUTTONS_HANGAR, 
            'value': baseSelf.TABS.HANGAR, 
            'textColor': 16764006,
            'textColorOver': 16768409, 
            'tooltip': TOOLTIPS.HEADER_BUTTONS_HANGAR},
        {'label': MENU.HEADERBUTTONS_STORAGE, 
            'value': baseSelf.TABS.STORAGE, 
            'tooltip': TOOLTIPS.HEADER_BUTTONS_STORAGE},
        {'label': MENU.HEADERBUTTONS_SHOP, 
            'value': baseSelf.TABS.STORE, 
            'tooltip': TOOLTIPS.HEADER_BUTTONS_SHOP}]
        
        if getGUIConfig()['showPersonalQuests']:
            tabDataProvider.append(baseSelf._getPersonalMissionSelectorTabData())

        tabDataProvider.append({'label': MENU.HEADERBUTTONS_PROFILE, 
        'value': baseSelf.TABS.PROFILE, 
        'tooltip': TOOLTIPS.HEADER_BUTTONS_PROFILE})
        techTreeData = {'label': MENU.HEADERBUTTONS_TECHTREE, 
        'value': baseSelf.TABS.TECHTREE, 
        'tooltip': TOOLTIPS.HEADER_BUTTONS_TECHTREE, 
        'isTooltipSpecial': False, 
        'subValues': [
                    baseSelf.TABS.RESEARCH]}
        
        if baseSelf.techTreeEventsListener.actions:
            techTreeData['tooltip'] = TOOLTIPS_CONSTANTS.TECHTREE_DISCOUNT_INFO
            techTreeData['isTooltipSpecial'] = True
            if baseSelf.techTreeEventsListener.getNations(unviewed=True):
                techTreeData['actionIcon'] = backport.image(R.images.gui.maps.icons.library.discountIndicator())

        tabDataProvider.extend([techTreeData])
        tabDataProvider.extend([
        {'label': MENU.HEADERBUTTONS_BARRACKS, 
            'value': baseSelf.TABS.BARRACKS, 
            'tooltip': TOOLTIPS.HEADER_BUTTONS_BARRACKS}])
        tournamentsData = baseSelf._getTournamentsSelectorData()
        tournamentsData = None

        if tournamentsData is not None:
            tabDataProvider.append(tournamentsData)
        # if CURRENT_REALM == 'RU':
        override = baseSelf._tutorialLoader.gui.lastHangarMenuButtonsOverride
        if override is not None:
            tabDataProvider[:] = filter(lambda item: item['value'] in override, tabDataProvider)
        return tabDataProvider

    def _DailyQuestWidget__show(self, base, baseSelf):
        base(baseSelf)
        baseSelf._DailyQuestWidget__hide()

    def _CachedBlur_enable(self, base, baseSelf):
        baseSelf._switchEnabled(False)

    def _LobbyHeader_populateButtons(self, base, baseSelf):
        if hasattr(baseSelf, '_tutorialLoader'): # removed CURRENT_REALM == 'RU'
            if baseSelf._tutorialLoader.gui.lastHeaderMenuButtonsOverride is not None:
                baseSelf._LobbyHeader__onOverrideHeaderMenuButtons()
                return
        else:
            buttonsToExclude = [button for button in baseSelf.BUTTONS.ALL()]
            baseSelf.as_setHeaderButtonsS(baseSelf._getAvailableButtons(buttonsToExclude))
            return

if getGUIConfig()['isLegacyLobbyHeaderEnabled']:
    g_lobbyHeaderHooks = LegacyLobbyHeaderHooks()