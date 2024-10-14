from debug_utils import LOG_CURRENT_EXCEPTION
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.modsSettingsApi import g_modsSettingsApi
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from CurrentVehicle import g_currentVehicle

class ActiveWidgetsPlaceholder(object):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

    def __init__(self):
        super(ActiveWidgetsPlaceholder, self).__init__()

    def update(self, position, alias):
        return False

lootbox_visible = False
header_visible = False

modLinkage = 'wot_classic_lobby_gui'
modDataVersion = 1.1
settings = {'disable_lootboxes': True, 'disable_battlepass': True}
template = {'modDisplayName': '\xd0\x9a\xd0\xbb\xd0\xb0\xd1\x81\xd1\x81\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd0\xb8\xd0\xbd\xd1\x82\xd0\xb5\xd1\x80\xd1\x84\xd0\xb5\xd0\xb9\xd1\x81 \xd0\xb0\xd0\xbd\xd0\xb3\xd0\xb0\xd1\x80\xd0\xb0',
 'enabled': True,
 'column1': [{'type': 'CheckBox',
              'text': '\xd0\xa1\xd0\xba\xd1\x80\xd1\x8b\xd1\x82\xd1\x8c \xd0\xbb\xd1\x83\xd1\x82\xd0\xb1\xd0\xbe\xd0\xba\xd1\x81\xd1\x8b',
              'value': True,
              'tooltip': '{HEADER}\xd0\xa1\xd0\xba\xd1\x80\xd1\x8b\xd1\x82\xd1\x8c \xd0\xba\xd0\xbe\xd0\xbd\xd1\x82\xd0\xb5\xd0\xb9\xd0\xbd\xd0\xb5\xd1\x80\xd1\x8b{/HEADER}{BODY}\xd0\x98\xd0\xb7 \xd0\xb0\xd0\xbd\xd0\xb3\xd0\xb0\xd1\x80\xd0\xb0 \xd0\xb1\xd1\x83\xd0\xb4\xd0\xb5\xd1\x82 \xd1\x81\xd0\xba\xd1\x80\xd1\x8b\xd1\x82 \xd1\x84\xd1\x83\xd0\xbd\xd0\xba\xd1\x86\xd0\xb8\xd0\xbe\xd0\xbd\xd0\xb0\xd0\xbb \xd0\xba\xd0\xbe\xd0\xbd\xd1\x82\xd0\xb5\xd0\xb9\xd0\xbd\xd0\xb5\xd1\x80\xd0\xbe\xd0\xb2.{/BODY}',
              'varName': 'disable_lootboxes'},
             {'type': 'CheckBox',
              'text': '\xd0\xa1\xd0\xba\xd1\x80\xd1\x8b\xd1\x82\xd1\x8c \xd0\xb1\xd0\xbe\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xb9 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xbf\xd1\x83\xd1\x81\xd0\xba',
              'value': True,
              'tooltip': '{HEADER}\xd0\xa1\xd0\xba\xd1\x80\xd1\x8b\xd1\x82\xd1\x8c \xd0\xb1\xd0\xbe\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xb9 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xbf\xd1\x83\xd1\x81\xd0\xba{/HEADER}{BODY}\xd0\x9e\xd1\x82\xd0\xba\xd0\xbb\xd1\x8e\xd1\x87\xd0\xb8\xd1\x82\xd1\x8c \xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb8\xd0\xba\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80\xd1\x8b \xd1\x83\xd1\x80\xd0\xbe\xd0\xb2\xd0\xbd\xd1\x8f \xd0\xb1\xd0\xbe\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbf\xd1\x80\xd0\xbe\xd0\xbf\xd1\x83\xd1\x81\xd0\xba\xd0\xb0 \xd0\xb2 \xd0\xbe\xd0\xba\xd0\xbd\xd0\xb5 \xd0\xb0\xd0\xbd\xd0\xb3\xd0\xb0\xd1\x80\xd0\xb0.{/BODY}',
              'varName': 'disable_battlepass'}]}

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

        value = settings.get('disable_lootboxes')
        print 'disable_lootboxes', not value
        lootbox_visible = not value

        value = settings.get('disable_battlepass')
        print 'disable_battlepass', not value
        header_visible = not value

        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        hangar = app.containerManager.getContainer(WindowLayer.VIEW).getChildContainer(5).getView()
        hangar.as_updateCarouselEventEntryStateS(lootbox_visible)
    except:
        print "[WeK_old_lobby] Couldn't apply_settings"
        LOG_CURRENT_EXCEPTION()

try:
    savedSettings = g_modsSettingsApi.getModSettings(modLinkage, template)
    if savedSettings:
        settings = savedSettings
        apply_settings(settings)
        g_modsSettingsApi.registerCallback(modLinkage, onModSettingsChanged, onButtonClicked)
    else:
        settings = g_modsSettingsApi.setModTemplate(modLinkage, template, onModSettingsChanged, onButtonClicked)
    print '[WeK_old_lobby] Configuration menu has been created successfully'
except:
    print "[WeK_old_lobby] Couldn't create configuration menu"
    LOG_CURRENT_EXCEPTION()