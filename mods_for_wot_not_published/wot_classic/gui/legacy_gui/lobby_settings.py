# На переработке.

from debug_utils import LOG_CURRENT_EXCEPTION
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.modsSettingsApi import g_modsSettingsApi
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.prb_control.events_dispatcher import g_eventDispatcher
from lobby_views import getGUIConfig

class ActiveWidgetsPlaceholder(object):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

    def __init__(self):
        super(ActiveWidgetsPlaceholder, self).__init__()

    def update(self, position, alias):
        return False

lootbox_visible = None
header_visible = None

modLinkage = 'wot_classic_lobby_gui'
modDataVersion = 1.2
default_settings = {'enabled': True, 'enable_lootboxes': getGUIConfig()['showLootBoxes'], 'enable_battlepass': getGUIConfig()['showBattlePass'], 
                    'enable_lobbyHeader': getGUIConfig()['isLegacyLobbyHeaderEnabled'], 'set_crystalAsPremium': getGUIConfig()['isCrystalPremium'], 
                    'show_personalQuests': getGUIConfig()['showPersonalQuests'], 'show_personalReserves': getGUIConfig()['showPersonalReserves'], 
                    'show_tasks': getGUIConfig()['showTasks']}
template = {'modDisplayName': 'Классический интерфейс ангара',
 'enabled': True,
 'column1': [{'type': 'CheckBox',
              'text': '#wek:settings/enableLootBoxes/label',
              'value': getGUIConfig()['showLootBoxes'],
              'tooltip': '#wek:settings/enableLootBoxes/tooltip',
              'varName': 'enable_lootboxes'},
             {'type': 'CheckBox',
              'text': '#wek:settings/enableBattlePass/label',
              'value': getGUIConfig()['showBattlePass'],
              'tooltip': '#wek:settings/enableBattlePass/tooltip',
              'varName': 'enable_battlepass'},
             {'type': 'CheckBox',
              'text': '#wek:settings/enableLobbyHeader/label',
              'value': getGUIConfig()['isLegacyLobbyHeaderEnabled'],
              'tooltip': '#wek:settings/enableLobbyHeader/tooltip',
              'varName': 'enable_lobbyHeader'},
             {'type': 'CheckBox',
              'text': '#wek:settings/crystalAsPremium/label',
              'value': getGUIConfig()['isCrystalPremium'],
              'tooltip': '#wek:settings/crystalAsPremium/tooltip',
              'varName': 'set_crystalAsPremium'}],
 'column2': [{'type': 'CheckBox',
              'text': '#wek:settings/showPersonalQuests/label',
              'value': getGUIConfig()['showPersonalQuests'],
              'tooltip': '#wek:settings/showPersonalQuests/tooltip',
              'varName': 'show_personalQuests'},
             {'type': 'CheckBox',
              'text': '#wek:settings/showPersonalReserves/label',
              'value': getGUIConfig()['showPersonalReserves'],
              'tooltip': '#wek:settings/showPersonalReserves/tooltip',
              'varName': 'show_personalReserves'},
             {'type': 'CheckBox',
              'text': '#wek:settings/showTasks/label',
              'value': getGUIConfig()['showTasks'],
              'tooltip': '#wek:settings/showTasks/tooltip',
              'varName': 'show_tasks'},
             {'type': 'CheckBox',
              'text': '#wek:settings/showTutorial/label',
              'value': getGUIConfig()['showTutorial'],
              'tooltip': '#wek:settings/showTutorial/tooltip',
              'varName': 'show_tutorial'}]}

def setHangarHeaderVisible(self):
    header_base(self)
    if not getGUIConfig()['showBattlePass']:
        self.headerComponent.destroy()
        self.headerComponent._currentVehicle = g_currentVehicle
        self.headerComponent._HangarHeader__widgets = {}
        self.headerComponent._HangarHeader__activeWidgets = ActiveWidgetsPlaceholder()

header_base = Hangar._populate
Hangar._populate = setHangarHeaderVisible

def setLootBoxesVisible(self, _):
    lootbox_base(self, getGUIConfig()['showLootBoxes'])

lootbox_base = Hangar.as_updateCarouselEventEntryStateS
Hangar.as_updateCarouselEventEntryStateS = setLootBoxesVisible

def restartSubView():
    appLoader = dependency.instance(IAppLoader)
    lobby = appLoader.getDefLobbyApp()
    if lobby and lobby.containerManager:
        view = lobby.containerManager.getView(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_HANGAR})
        if view is not None:
            view.destroy()
        g_eventDispatcher.loadHangar()

def setCrystalPremium(isCrystalPremium):
    appLoader = dependency.instance(IAppLoader)
    lobby = appLoader.getDefLobbyApp()
    if lobby and lobby.containerManager:
        view = lobby.containerManager.getView(WindowLayer.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: 'LegacyLobbyHeaderUI'})
        if view is not None:
            view.isCrystalPremium = isCrystalPremium
            view._LegacyLobbyHeader__onPremiumExpireTimeChanged(None)

def setLootboxesVisibillity(lb_value):
    appLoader = dependency.instance(IAppLoader)
    lobby = appLoader.getDefLobbyApp()
    if lobby and getattr(lobby, 'containerManager'):
        hangar = lobby.containerManager.getContainer(WindowLayer.VIEW).getChildContainer(5).getView()
        hangar.as_updateCarouselEventEntryStateS(lb_value)

def setShowPersonalQuests(pq_value):
    appLoader = dependency.instance(IAppLoader)
    lobby = appLoader.getDefLobbyApp()
    if lobby and lobby.containerManager:
        view = lobby.containerManager.getView(WindowLayer.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: 'LegacyLobbyHeaderUI'})
        if view is not None:
            view.as_showPersonalQuestsS(pq_value)

def setShowPersonalReserves(pr_value):
    appLoader = dependency.instance(IAppLoader)
    lobby = appLoader.getDefLobbyApp()
    if lobby and lobby.containerManager:
        view = lobby.containerManager.getView(WindowLayer.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: 'LegacyLobbyHeaderUI'})
        if view is not None:
            view.as_showPersonalReservesS(pr_value)

def setShowTasks(tasks_value):
    appLoader = dependency.instance(IAppLoader)
    lobby = appLoader.getDefLobbyApp()
    if lobby and lobby.containerManager:
        view = lobby.containerManager.getView(WindowLayer.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: 'LegacyLobbyHeaderUI'})
        if view is not None:
            view.as_showTasksS(tasks_value)

def setShowTutorial(tutorial_value):
    appLoader = dependency.instance(IAppLoader)
    lobby = appLoader.getDefLobbyApp()
    if lobby and lobby.containerManager:
        view = lobby.containerManager.getView(WindowLayer.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: 'LegacyLobbyHeaderUI'})
        if view is not None:
            view.as_showTutorialS(tutorial_value)

def onModSettingsChanged(linkage, newSettings):
    if linkage == modLinkage:
        print '[MTO_lobby_settings] Configuration modified: ', newSettings
        apply_settings(newSettings)

def onButtonClicked(linkage, varName, value):
    if linkage == modLinkage:
        clicks = g_modsSettingsApi.getModData(modLinkage, modDataVersion, 0)
        clicks += 1
        g_modsSettingsApi.saveModData(modLinkage, modDataVersion, clicks)

def onGameKeyDown(event):
    pass

def apply_settings(settings):
    try:

        lootboxes_value = settings.get('enable_lootboxes', None)
        battlepass_value = settings.get('enable_battlepass', None)
        lobbyHeader_value = settings.get('enable_lobbyHeader', None)
        crystalIsPremium_value = settings.get('set_crystalAsPremium', None)
        personalQuests_value = settings.get('show_personalQuests', None)
        personalReserves_value = settings.get('show_personalReserves', None)
        tasks_value = settings.get('show_tasks', None)
        tutorial_value = settings.get('show_tutorial', None)

        if lootboxes_value is not None:
            getGUIConfig('showLootBoxes', lootboxes_value)
            setLootboxesVisibillity(lootboxes_value)

        if battlepass_value is not None:
            getGUIConfig('showBattlePass', battlepass_value)
        
        if lobbyHeader_value is not None:
            getGUIConfig('isLegacyLobbyHeaderEnabled', lobbyHeader_value)
        
        if crystalIsPremium_value is not None:
            getGUIConfig('isCrystalPremium', crystalIsPremium_value)
            setCrystalPremium(crystalIsPremium_value)
        
        if personalQuests_value is not None:
            getGUIConfig('showPersonalQuests', personalQuests_value)
            setShowPersonalQuests(personalQuests_value)
        
        if personalReserves_value is not None:
            getGUIConfig('showPersonalReserves', personalReserves_value)
            setShowPersonalReserves(personalReserves_value)
        
        if tasks_value is not None:
            getGUIConfig('showTasks', tasks_value)
            setShowTasks(tasks_value)
        
        if tutorial_value is not None:
            getGUIConfig('showTutorial', tutorial_value)
            setShowTutorial(tutorial_value)
        
        restartSubView()

    except:
        print "[MTO_lobby_settings] Couldn't apply_settings"
        LOG_CURRENT_EXCEPTION()

try:
    savedSettings = g_modsSettingsApi.getModSettings(modLinkage, template)
    if savedSettings:
        default_settings = savedSettings
        g_modsSettingsApi.registerCallback(modLinkage, onModSettingsChanged, onButtonClicked)
        apply_settings(savedSettings)
    else:
        print 'g_modsSettingsApi.setModTemplate'
        default_settings = g_modsSettingsApi.setModTemplate(modLinkage, template, onModSettingsChanged, onButtonClicked)
    print '[MTO_lobby_settings] Configuration menu has been created successfully'
except:
    print "[MTO_lobby_settings] Couldn't create configuration menu"
    LOG_CURRENT_EXCEPTION()