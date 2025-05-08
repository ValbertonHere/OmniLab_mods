import BigWorld, Event, json, os, WGC
from account_helpers.settings_core import settings_constants
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_WARNING
from external_strings_utils import unicode_from_utf8
from gui import InputHandler
from gui.Scaleform.daapi.view.common.settings.SettingsParams import SettingsParams
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.utils.key_mapping import getBigworldNameFromKey
from helpers import dependency, isPlayerAccount
from frameworks.wulf import WindowLayer
from skeletons.gui.app_loader import IAppLoader

class SettingsPresetWindow(AbstractWindowView):
    SETTINGS_FILE = os.path.normpath(os.path.join(os.path.dirname(unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]), 'mods', 'omnilab', 'settings.preset'))
    SETTINGS_FOLDER = os.path.dirname(SETTINGS_FILE)

    def __init__(self):
        super(SettingsPresetWindow, self).__init__()
        self.onPresetStatusUpdate = Event.Event()
        self.params = SettingsParams()
        self.isPresetFound = False

    def _populate(self):
        super(SettingsPresetWindow, self)._populate()
        self.onPresetStatusUpdate += self.__onPresetStatusUpdate
        self.__updatePresetFolder()

    def _dispose(self):
        self.onPresetStatusUpdate -= self.__onPresetStatusUpdate
        super(SettingsPresetWindow, self)._dispose()

    def py_createApplyPreset(self):
        self.__applyPreset() if self.isPresetFound else self.__createPreset()

    def py_updateDeletePreset(self):
        self.__deleteCurrentPreset() if self.isPresetFound else self.__updatePresetFolder()

    def py_showPresetFolder(self):
        os.startfile(self.SETTINGS_FOLDER)

    def __createPreset(self):
        try:
            if not os.path.isdir(self.SETTINGS_FOLDER):
                os.makedirs(self.SETTINGS_FOLDER)

            settings = (self.params.getGameSettings(), 
                        self.params.getGraphicsSettings(), 
                        self.params.getSoundSettings(), 
                        self.params.getControlsSettings(), 
                        self.params.getAimSettings(), 
                        self.params.getMarkersSettings(), 
                        self.params.getFeedbackSettings())
            json.dump(settings, open(self.SETTINGS_FILE, 'wb'))
            self.isPresetFound = True
            self.onPresetStatusUpdate('created')
        except:
            LOG_ERROR('Failed to create settings preset.')
            LOG_CURRENT_EXCEPTION()

    def __updatePresetFolder(self):
        self.isPresetFound = os.path.exists(self.SETTINGS_FILE)
        self.onPresetStatusUpdate()
    
    def __deleteCurrentPreset(self):
        self.isPresetFound = False
        if os.path.exists(self.SETTINGS_FILE):
            os.remove(self.SETTINGS_FILE)
            self.onPresetStatusUpdate('deleted')
        else:
            LOG_WARNING("Settings preset file does not exist")
            self.onPresetStatusUpdate()
    
    def __applyPreset(self):
        try:
            savedSettings = json.load(open(self.SETTINGS_FILE, 'r'))
            for settingsValues in savedSettings:
                for key, value in settingsValues.items():
                    if key in (settings_constants.CONTROLS.KEYBOARD, settings_constants.SPGAim.SPG_SCALE_WIDGET) + settings_constants.AIM.ALL() + settings_constants.MARKERS.ALL() + settings_constants.FEEDBACK.ALL():
                        for subKey, subValue in value.items():
                            if isinstance(subValue, dict) and subValue.get('current', None) is not None:
                                self.params.apply({key: {subKey: subValue['current']}}, False)
                            elif isinstance(value, int):
                                self.params.apply({key: {subKey: bool(subValue)}}, False)
                            else:
                                self.params.apply({key: {subKey: subValue}}, True)
                    elif isinstance(value, dict) and value.get('current', None) is not None:
                        if key == settings_constants.GRAPHICS.RENDER_PIPELINE:
                            isRestart = self.params.apply({key: value['current']}, True)
                        self.params.apply({key: value['current']}, True)
                    elif isinstance(value, int):
                        self.params.apply({key: bool(value)}, True)
                    else:
                        self.params.apply({key: value}, True)
            self.onPresetStatusUpdate('applied')
            if isRestart:
                BigWorld.savePreferences()
                WGC.notifyRestart()
                BigWorld.worldDrawEnabled(False)
                BigWorld.restartGame()
        except IOError:
            self.__updatePresetFolder()
        except:
            self.onPresetStatusUpdate('apply_failed')
            LOG_CURRENT_EXCEPTION()

    def __getPresetStatusI18nKey(self, status):
        if status is None:
            status = 'found' if self.isPresetFound else 'not_found'
        return '#settingsPresetWindow:presetStatus/%s' % status

    def __onPresetStatusUpdate(self, statusText=None):
        self.flashObject.as_updatePresetStatus(self.isPresetFound, self.__getPresetStatusI18nKey(statusText))

    def onWindowClose(self):
        self.destroy()
        
g_entitiesFactories.addSettings(ViewSettings('SettingsPresetWindowUI', SettingsPresetWindow, 'settingsPresetWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE))

def onhandleKeyEvent(event):
    key = getBigworldNameFromKey(event.key)
    if key == 'KEY_F9':
        openSettingsPresetWindow()

def openSettingsPresetWindow():
    if isPlayerAccount():
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        app.loadView(SFViewLoadParams('SettingsPresetWindowUI'))

try:
    from gui.modsListApi import g_modsListApi
    g_modsListApi.addModification(id='SettingsPresetWindow', name='#settingsPresetWindow:modsListAPI/title', description='#settingsPresetWindow:modsListAPI/tooltip',
            icon='gui/maps/icons/omnilab/settingsPresetIcon.png', enabled=True, login=False, lobby=True, callback=openSettingsPresetWindow)
except:
    InputHandler.g_instance.onKeyDown += onhandleKeyEvent