import BigWorld, Event, json, os, LGC, logging
from account_helpers.settings_core import settings_constants
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_WARNING
from external_strings_utils import unicode_from_utf8
from gui import InputHandler
from gui.Scaleform.daapi.view.common.settings.SettingsParams import SettingsParams
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.utils.key_mapping import getBigworldNameFromKey
from helpers import dependency, i18n, isPlayerAccount
from frameworks.wulf import WindowLayer
from skeletons.gui.app_loader import IAppLoader

class SettingsPresetWindow(AbstractWindowView):
    SETTINGS_FOLDER = os.path.normpath(os.path.join(os.path.dirname(unicode_from_utf8(BigWorld.getPreferencesFilePath())[1]), 'mods', 'omnilab'))
    SELECTED_PRESET_INFO_FILE = SETTINGS_FOLDER + '\selected_preset'
    DEFAULT_PRESETS_DATA = [{'label': 'Slot 0'},
                            {'label': 'Slot 1'},
                            {'label': 'Slot 2'},
                            {'label': 'Slot 3'},
                            {'label': 'Slot 4'}]

    def __init__(self):
        super(SettingsPresetWindow, self).__init__()
        self.onPresetStatusUpdate = Event.Event()
        self.params = SettingsParams()
        self.isPresetFound = False
        self.__selectedPreset = 0
        self.__selectedPresetFile = None
        self.py_selectPreset(self.py_getSelectedPreset())

    def _populate(self):
        super(SettingsPresetWindow, self)._populate()
        self.onPresetStatusUpdate += self.__onPresetStatusUpdate
        self.__updatePresetInfo()
        
    def _dispose(self):
        self.onPresetStatusUpdate -= self.__onPresetStatusUpdate
        super(SettingsPresetWindow, self)._dispose()
    
    def py_createApplyPreset(self, presetName):
        self.__applyPreset(presetName) if self.isPresetFound else self.__createPreset(presetName)

    def py_updateDeletePreset(self):
        self.__deleteCurrentPreset() if self.isPresetFound else self.__updatePresetInfo()

    def py_showPresetFolder(self):
        os.startfile(self.SETTINGS_FOLDER)
    
    def py_selectPreset(self, presetID):
        self.__selectedPreset = presetID
        self.__selectedPresetFile = self.SETTINGS_FOLDER + '\settings_%s.preset' % self.__selectedPreset
        self.__saveSelectedPreset()
        self.__updatePresetInfo()
    
    def py_applyPresetName(self, presetName):
        preset = json.load(open(self.__selectedPresetFile, 'r'))
        preset['name'] = presetName
        self.__saveExistingPreset(preset)

    def py_getPresets(self):
        presetsData = self.DEFAULT_PRESETS_DATA
        presets = [preset for preset in os.listdir(self.SETTINGS_FOLDER) if preset.startswith('settings_')]

        for idx, preset_file in enumerate(presets):
            presetData = json.load(open(self.SETTINGS_FOLDER + '\%s' % preset_file, 'r'))

            if not presetData:
                presetsData[idx] = {'label': i18n.makeString('#settingsPresetWindow:presetsList/emptySlot', slotID=idx)}
                continue
            elif isinstance(presetData, list): # См. __applyPreset
                presetsData[idx] = {'label': i18n.makeString('#settingsPresetWindow:presetsList/presetWithoutName', slotID=idx)}
            else:
                presetsData[idx] = {'label': presetData['name']}
        
        return presetsData

    def py_getSelectedPreset(self):
        try:
            if not os.path.isfile(self.SELECTED_PRESET_INFO_FILE):
                self.__saveSelectedPreset()

            return int(open(self.SELECTED_PRESET_INFO_FILE, 'r').read(1)) # Защита от дурака.
        except:
            LOG_ERROR('Failed to load selected preset. See lines below.')
            LOG_CURRENT_EXCEPTION()
            
    def __createPreset(self, presetName):
        try:
            presetDict = {'name': presetName if presetName else i18n.makeString('#settingsPresetWindow:presetsList/presetWithoutName', slotID=self.__selectedPreset),
                          'settings': (self.params.getGameSettings(), 
                                       self.params.getGraphicsSettings(), 
                                       self.params.getSoundSettings(), 
                                       self.params.getControlsSettings(), 
                                       self.params.getAimSettings(), 
                                       self.params.getMarkersSettings(), 
                                       self.params.getFeedbackSettings())}
            
            json.dump(presetDict, open(self.__selectedPresetFile, 'wb'))
            self.isPresetFound = True
            self.onPresetStatusUpdate('created')
        except:
            LOG_ERROR('Failed to create settings preset.')
            LOG_CURRENT_EXCEPTION()

    def __updatePresetInfo(self):
        self.isPresetFound = os.path.exists(self.__selectedPresetFile) and open(self.__selectedPresetFile, 'r').read(2) != '{}'
        self.onPresetStatusUpdate()
    
    def __deleteCurrentPreset(self):
        self.isPresetFound = False
        if os.path.exists(self.__selectedPresetFile):
            open(self.__selectedPresetFile, 'wb').write('{}')
            self.onPresetStatusUpdate('deleted')
        else:
            LOG_WARNING("Settings preset file does not exist")
            self.onPresetStatusUpdate()
    
    def __applyPreset(self, presetName):
        try:
            savedSettings = json.load(open(self.__selectedPresetFile, 'r'))

            if not isinstance(savedSettings, list): # Для нового формата пресетов.
                savedSettings = savedSettings['settings']
                self.py_applyPresetName(presetName)

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
                LGC.notifyRestart()
                BigWorld.worldDrawEnabled(False)
                BigWorld.restartGame()
        except IOError:
            self.__updatePresetInfo()
        except:
            self.onPresetStatusUpdate('apply_failed')
            LOG_CURRENT_EXCEPTION()

    def __getPresetStatusI18nKey(self, status):
        if status is None:
            status = 'found' if self.isPresetFound else 'not_found'
        return '#settingsPresetWindow:presetStatus/%s' % status

    def __onPresetStatusUpdate(self, statusText=None):
        self.flashObject.as_setNameInputEnabled(self.isPresetFound, not isinstance(json.load(open(self.__selectedPresetFile, 'r')), list))
        self.flashObject.as_updatePresetStatus(self.isPresetFound, self.__getPresetStatusI18nKey(statusText))
    
    def __saveSelectedPreset(self):
        try:
            open(self.SELECTED_PRESET_INFO_FILE, 'wb').write(str(self.__selectedPreset))
        except:
            LOG_ERROR('Failed to save selected preset. See lines below.')
            LOG_CURRENT_EXCEPTION()
    
    def __saveExistingPreset(self, preset):
        json.dump(preset, open(self.__selectedPresetFile, 'wb'))

    def onWindowClose(self):
        self.destroy()

def init():
    if not os.path.isdir(SettingsPresetWindow.SETTINGS_FOLDER):
        os.makedirs(SettingsPresetWindow.SETTINGS_FOLDER)
    
    for i in xrange(0, 5):
        file = SettingsPresetWindow.SETTINGS_FOLDER + '\settings_%s.preset' % i
        if not os.path.isfile(file):
            open(file, 'wb').write('{}')


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