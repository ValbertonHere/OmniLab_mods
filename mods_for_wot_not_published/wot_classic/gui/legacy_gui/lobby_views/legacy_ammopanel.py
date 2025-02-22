import BigWorld, Keys

from gui.Scaleform.locale.MENU import MENU
from helpers import dependency
from helpers.i18n import makeString
from functools import partial
from constants import PREBATTLE_TYPE, QUEUE_TYPE, ROLE_TYPE_TO_LABEL
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_CURRENT_EXCEPTION

from items import getTypeInfoByName
from items import ITEM_TYPES as MODULE_ITEM_TYPES
from items.vehicles import g_cache

from account_helpers.AccountSettings import SHOW_OPT_DEVICE_HINT, AccountSettings
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS

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
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import _SlotVOConstants
from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import ModuleFittingSelectPopover, _POPOVER_FIRST_TAB_IDX, _POPOVER_SECOND_TAB_IDX, CommonFittingSelectPopover, _HangarLogicProvider, PopoverLogicProvider, _extendByModuleData
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import OptDeviceBonusesDescriptionBuilder
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS

from frameworks.wulf import Array
from frameworks.wulf.gui_constants import WindowLayer

from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IComp7Controller

_MODULE_SLOTS = (GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleGun],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleTurret],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleChassis],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleEngine],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.vehicleRadio],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.optionalDevice],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.shell],
 GUI_ITEM_TYPE_NAMES[MODULE_ITEM_TYPES.equipment],
 'battleBooster', 'battleAbility', 'modificator')

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

class HangarFittingSlotVO(dict):

    def __init__(self, modulesData, vehicle, moduleType, tooltipType=None, isDisabledTooltip=False):
        super(HangarFittingSlotVO, self).__init__()
        if moduleType == FITTING_TYPES.VEHICLE_TURRET and not vehicle.hasTurrets:
            ttType = ''
        else:
            ttType = tooltipType or TOOLTIPS_CONSTANTS.PREVIEW_MODULE
        vehicleModule = self._prepareModule(modulesData, vehicle, moduleType)
        if moduleType == FITTING_TYPES.VEHICLE_CHASSIS:
            if vehicleModule and vehicleModule.isWheeledChassis():
                moduleType = FITTING_TYPES.VEHICLE_WHEELED_CHASSIS
        self['tooltip'] = ''
        self['name'] = ''
        self['tooltipType'] = ttType
        self['slotType'] = moduleType
        self['removable'] = True
        if vehicleModule is None:
            self['id'] = _SlotVOConstants.UNRESOLVED_LIST_INDEX
            self['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
            if not isDisabledTooltip:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_EMPTY
            else:
                self['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_DISABLED
            self['moduleLabel'] = _SlotVOConstants.MODULE_LABEL_EMPTY
        elif moduleType == 'modificator':
            self['id'] = vehicleModule.id.itemID
            self['moduleLabel'] = vehicleModule.name
            self['name'] = vehicleModule.userString
            self['slotLocked'] = True
            return
        else:
            self['id'] = vehicleModule.intCD
            self['removable'] = vehicleModule.isRemovable
            self['moduleLabel'] = vehicleModule.getGUIEmblemID()
            self['name'] = vehicleModule.userName
        self._setNewCounter(vehicleModule, vehicle)
        return

    def _prepareModule(self, modulesData, vehicle, moduleType):
        module = modulesData[0]
        self['slotLocked'] = vehicle.isLocked or not vehicle.isAlive
        if module.itemTypeName == FITTING_TYPES.OPTIONAL_DEVICE:
            battleBooster = vehicle.battleBoosters.installed[0]
            if battleBooster is not None and battleBooster.isOptionalDeviceCompatible(module):
                self['highlight'] = True

            self['bgHighlightType'] = module.getHighlightType()
            self['overlayType'] = module.getOverlayType()
        elif module.itemTypeName == FITTING_TYPES.EQUIPMENT and moduleType != 'modificator':
            self['bgHighlightType'] = module.getHighlightType()
            self['overlayType'] = module.getOverlayType()
        elif module.itemTypeName == FITTING_TYPES.EQUIPMENT and moduleType == 'modificator':
            return module
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

    def _setNewCounter(self, vehicleModule, vehicle):
        if vehicleModule is None:
            return
        else:
            if vehicleModule.itemTypeID == MODULE_ITEM_TYPES.vehicleGun:
                if vehicleModule.isAutoReloadable(vehicle.descriptor):
                    uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage()
                    if not uiStorage.get(UI_STORAGE_KEYS.AUTO_RELOAD_MARK_IS_SHOWN):
                        self['counter'] = 1
                if vehicleModule.isDualGun(vehicle.descriptor):
                    uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage()
                    if not uiStorage.get(UI_STORAGE_KEYS.DUAL_GUN_MARK_IS_SHOWN):
                        if 'counter' in self:
                            self['counter'] += 3
                        else:
                            self['counter'] = 3
                if vehicleModule.hasDualAccuracy(vehicle.descriptor):
                    uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage2()
                    if not uiStorage.get(UI_STORAGE_KEYS.DUAL_ACCURACY_MARK_IS_SHOWN):
                        self['counter'] = self.get('counter', 0) + 1
            if vehicleModule.itemTypeID == MODULE_ITEM_TYPES.vehicleEngine:
                if vehicleModule.hasTurboshaftEngine():
                    uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage()
                    if not uiStorage.get(UI_STORAGE_KEYS.TURBOSHAFT_MARK_IS_SHOWN):
                        self['counter'] = self.get('counter', 0) + 1
                if vehicleModule.hasRocketAcceleration():
                    uiStorage = dependency.instance(ISettingsCore).serverSettings.getUIStorage2()
                    if not uiStorage.get(UI_STORAGE_KEYS.ROCKET_ACCELERATION_MARK_IS_SHOWN):
                        self['counter'] = self.get('counter', 0) + 1
            return
    
class LegacyAmmoPanel(View, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    comp7Controller = dependency.descriptor(IComp7Controller)
    appLoader = dependency.instance(IAppLoader)
    
    def __init__(self):
        super(LegacyAmmoPanel, self).__init__()
        self._initLoad = True

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

    def as_setModificationVisibleS(self, isVisible):
        self.flashObject.as_setModificationVisible(bool(isVisible))

    def as_setBattleAbilitiesVisibleS(self):
        isVisible = self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC)
        self.flashObject.as_setBattleAbilitiesVisible(isVisible)

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
                elif slotType == 'modificator':
                    elevenLVLModificator = g_cache.getEquipmentByID(vehicle.typeDescr.ability)

                    if self.comp7Controller.isSuitableVehicle(vehicle) is not None or not self.comp7Controller.isComp7PrbActive():
                        comp7Modificator = None
                    else:
                        comp7Modificator = self.comp7Controller.getRoleEquipment(ROLE_TYPE_TO_LABEL.get(vehicle.descriptor.role))
                    
                    if comp7Modificator is None and elevenLVLModificator is None:
                        modSlot = EmptySlotVO('modificator')
                    else:
                        modSlot = HangarFittingSlotVO([comp7Modificator or elevenLVLModificator], vehicle, 'modificator', tooltipType='')
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
            ammunitionData['modificator'] = modSlot

            self.as_setBattleAbilitiesVisibleS()
            self.as_setModificationVisibleS(comp7Modificator or elevenLVLModificator)
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