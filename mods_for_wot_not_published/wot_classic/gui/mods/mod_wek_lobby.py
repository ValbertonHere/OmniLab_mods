from debug_utils import LOG_CURRENT_EXCEPTION
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.modsSettingsApi.skeleton import IModsSettingsApi
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from CurrentVehicle import g_currentVehicle
from skeletons.gui.shared.utils import IHangarSpace
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE

class ActiveWidgetsPlaceholder(object):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

    def __init__(self):
        super(ActiveWidgetsPlaceholder, self).__init__()

    def update(self, position, alias):
        return False

class ClassicModSettingsAPI(IModsSettingsApi):
    














lootbox_visible = None
header_visible = None

modLinkage = 'wot_classic_lobby_gui'
modDataVersion = 1.2
default_settings = {'enabled': True, 'enable_lootboxes': False, 'enable_battlepass': False}
template = {'modDisplayName': 'Классический интерфейс ангара',
 'enabled': True,
 'column1': [{'type': 'CheckBox',
              'text': 'Отображать лутбоксы',
              'value': False,
              'tooltip': '{HEADER}Отображать лутбоксы{/HEADER}{BODY}В ангаре будет показана/скрыта функциональность контейнеров.{/BODY}',
              'varName': 'enable_lootboxes'},
             {'type': 'CheckBox',
              'text': 'Отображать кнопки в верхней части окна ангара',
              'value': False,
              'tooltip': '{HEADER}Отображать кнопки в верхней части окна ангара{/HEADER}{BODY}Включить/отключить кнопки в верхней части окна ангара (боевой пропуск, ЛБЗ и т. д.).{/BODY}',
              'varName': 'enable_battlepass'}]}

try:
    from gui.legacy_gui.lobby_views import getGUIConfig
    default_settings['enable_lobbyHeader'] = getGUIConfig()['isLegacyLobbyHeaderEnabled']
    template['column1'].append({'type': 'CheckBox',
                                'text': 'Включить старую шапку ангара',
                                'value': getGUIConfig()['isLegacyLobbyHeaderEnabled'],
                                'tooltip': '{HEADER}Включить старую шапку ангара{/HEADER}{BODY}Включить старый вид шапки ангара (Требуется перезапуск клиента).{/BODY}',
                                'varName': 'enable_lobbyHeader'})
except:
    print '[WeK_old_lobby] No Legacy Lobby Header found. Skipping...'

def setHangarHeaderVisible(self):
    header_base(self)
    if not header_visible:
        self.headerComponent.destroy()
        self.headerComponent._currentVehicle = g_currentVehicle
        self.headerComponent._HangarHeader__widgets = {}
        self.headerComponent._HangarHeader__activeWidgets = ActiveWidgetsPlaceholder()

header_base = Hangar._populate
Hangar._populate = setHangarHeaderVisible

def setLootBoxesVisible(self, _):
    lootbox_base(self, lootbox_visible)

lootbox_base = Hangar.as_updateCarouselEventEntryStateS
Hangar.as_updateCarouselEventEntryStateS = setLootBoxesVisible

def restartSubView():
    appLoader = dependency.instance(IAppLoader)
    hangarSpace = dependency.instance(IHangarSpace)
    if hangarSpace.spaceInited:
        lobby = appLoader.getDefLobbyApp()
        if lobby and lobby.containerManager:
            view = lobby.containerManager.getView(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_HANGAR})
            if view is not None:
                view.destroy()
            g_eventDispatcher.loadHangar()

def setLootboxesVisibillity(lb_value):
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    hangar = app.containerManager.getContainer(WindowLayer.VIEW).getChildContainer(5).getView()
    hangar.as_updateCarouselEventEntryStateS(lb_value)

def onModSettingsChanged(linkage, newSettings):
    if linkage == modLinkage:
        print '[WeK_old_lobby] Configuration modified: ', newSettings
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

        global lootbox_visible
        global header_visible

        lootboxes_value = settings.get('enable_lootboxes')
        battlepass_value = settings.get('enable_battlepass')
        lobbyHeader_value = settings.get('enable_lobbyHeader', None)
        
        lootbox_visible = lootboxes_value
        header_visible = battlepass_value

        setLootboxesVisibillity(lootboxes_value)
        restartSubView()
        
        if lobbyHeader_value is not None:
            getGUIConfig(lobbyHeader_value)

    except:
        print "[WeK_old_lobby] Couldn't apply_settings"
        LOG_CURRENT_EXCEPTION()

try:
    savedSettings = g_modsSettingsApi.getModSettings(modLinkage, template)
    if savedSettings:
        print savedSettings
        print default_settings
        default_settings = savedSettings
        g_modsSettingsApi.registerCallback(modLinkage, onModSettingsChanged, onButtonClicked)
        apply_settings(savedSettings)
    else:
        print 'g_modsSettingsApi.setModTemplate'
        default_settings = g_modsSettingsApi.setModTemplate(modLinkage, template, onModSettingsChanged, onButtonClicked)
    print '[WeK_old_lobby] Configuration menu has been created successfully'
except:
    print "[WeK_old_lobby] Couldn't create configuration menu"
    LOG_CURRENT_EXCEPTION()