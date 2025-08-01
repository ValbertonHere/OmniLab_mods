import BigWorld, json, os

from ResMgr import isDir
from gui.modsListApi import g_modsListApi
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from gui import ClientHangarSpace, SystemMessages

from debug_utils import LOG_NOTE
from gui.game_control.hangar_switch_controller import SceneSpaceConfig
from gui.shared.personality import ServicesLocator
from skeletons.gui.app_loader import GuiGlobalSpaceID
from skeletons.gui.game_control import IHangarSpaceSwitchController
from gui.ClientHangarSpace import getHangarFullVisibilityMask

class ClassicSceneSpaceConfig(SceneSpaceConfig):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, spaceId=None, waitingMessage=None, waitingBackground=None):
        self._waitingMessage = waitingMessage
        self._waitingBackground = waitingBackground
        self._basicSpaceId = spaceId['basic']
        self._premiumSpaceId = spaceId['premium']
        self._visibilityMask = {True: None, False: None}
        self._spaceIdOverride = {}

    def getVisibilityMask(self, isPremium=False):
        if self.hangarSpace.inited and isPremium is None:
            isPremium = self.hangarSpace.isPremium
        else:
            isPremium = False
            
        if self._visibilityMask[isPremium] is not None:
            return self._visibilityMask[isPremium]
        else:
            return getHangarFullVisibilityMask(self.getHangarSpaceId(isPremium))

    def discardVisibilityMaskOverride(self, isPremium):
        self._visibilityMask[isPremium] = None
        return

    def setVisibilityMask(self, isPremium, visibilityMask):
        self._visibilityMask[isPremium] = visibilityMask

    def getHangarSpaceId(self, isPremium=None):
        if self.hangarSpace.inited and isPremium is None:
            isPremium = self.hangarSpace.isPremium
        else:
            isPremium = False
        return self._premiumSpaceId if isPremium else self._basicSpaceId

    def setSpaceIdOverride(self, isPremium, newId):
        self._spaceIdOverride[isPremium] = newId

    def discardSpaceIdOverride(self, isPremium):
        del self._spaceIdOverride[isPremium]

    def clear(self):
        self._visibilityMask = {True: None, False: None}
        self._spaceIdOverride = {}
        return

class ClassicHangarOverrider(object):
    hangarSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

    CLASSIC_HANGARS = ('hangar', 'hangar_premium', 'hangar_v2', 'hangar_premium_v2')
    SPECIAL_HANGARS = ('hangar_premium_9may', 'hangar_premium_23feb_v2', 'Luganks_5years_hangar', 'hangar_premium_igr')
    PREM_SENSETIVE_HANGARS = {'ps_v1': {'basic': 'hangar', 'premium': 'hangar_premium'},
                              'ps_v2': {'basic': 'hangar_v2', 'premium': 'hangar_premium_v2'}}

    def __init__(self):
        ServicesLocator.appLoader.onGUISpaceEntered += self.onGUISpaceEntered
        
        self.hangar_config = {
            'is_prem_sensetive': True,
            'current_hangar': 'ps_v2',
            'excepted_scenes': ['ARMORY_YARD', 'hb_offence', 'hb_defence']
        }

        self.updateHangarConfig()

    def _noti(self, msg, isError=False):
        SystemMessages.pushMessage(msg, (SystemMessages.SM_TYPE.Information if not isError else SystemMessages.SM_TYPE.Error), priority=True)

    def onGUISpaceEntered(self, spaceID, *args, **kwargs):
        if spaceID != GuiGlobalSpaceID.LOBBY:
            return
        
        if self.hangarSwitchController is not None:
            self.lockHangarOverride(self.hangar_config['current_hangar'], self.hangar_config['is_prem_sensetive'])

    def processSceneChange(self, hanLinkage, isPremSensetive):
        if hanLinkage.startswith('ps_'):
            for hangarName in self.PREM_SENSETIVE_HANGARS[hanLinkage].values():
                if isDir('spaces/%s' % hangarName) != 1:
                    self._noti('#wek_hangarSwitcher:loadError/hangarNotExists', True)
                    return
        else:
            if isDir('spaces/%s' % hanLinkage) != 1:
                self._noti('#wek_hangarSwitcher:loadError/hangarNotExists', True)
                return
        
        self.updateHangarConfig(hanLinkage, isPremSensetive, True)
        self.lockHangarOverride(hanLinkage, isPremSensetive)
        self.hangarSwitchController.processPossibleSceneChange()

    def lockHangarOverride(self, hanLinkage, isPremiumSensetive=False):
        self.hangarSwitchController._HangarSpaceSwitchController__isHangarOverridingLocked = False

        for name in self.hangarSwitchController._sceneSpaceParams.iterkeys():
            if name not in self.hangar_config['excepted_scenes']:
                if isPremiumSensetive:
                    self.hangarSwitchController._sceneSpaceParams[name] = ClassicSceneSpaceConfig(self.PREM_SENSETIVE_HANGARS[hanLinkage])
                else:
                    self.hangarSwitchController._sceneSpaceParams[name] = SceneSpaceConfig(hanLinkage)

        if isPremiumSensetive:
            self.hangarSwitchController._defaultHangarSpaceConfig.setSpaceIdOverride(False, self.PREM_SENSETIVE_HANGARS[hanLinkage]['basic'])
            self.hangarSwitchController._defaultHangarSpaceConfig.setSpaceIdOverride(True, self.PREM_SENSETIVE_HANGARS[hanLinkage]['premium'])
        else:
            for isPremium in (True, False):
                self.hangarSwitchController._defaultHangarSpaceConfig.setSpaceIdOverride(isPremium, hanLinkage)

        self.hangarSwitchController._HangarSpaceSwitchController__isHangarOverridingLocked = True
        LOG_NOTE('Hangar override was locked. Hangar preset:', hanLinkage, 'Excepted this scenes:', self.hangar_config['excepted_scenes'])
    
    def updateHangarConfig(self, spaceName=None, isPremSensetive=False, needToWrite=False):
        hangar_config_file_path = 'mods/configs/wotclassic/hangar_config.json'
        if os.path.isfile(hangar_config_file_path):
            with open(hangar_config_file_path, 'r') as f2r:
                data = json.load(f2r)
                self.hangar_config.update(data)
            if needToWrite:
                with open(hangar_config_file_path, 'w') as f2w:
                    self.hangar_config['current_hangar'] = spaceName
                    self.hangar_config['is_prem_sensetive'] = isPremSensetive
                    json.dump(self.hangar_config, f2w)
        else:
            try:
                os.makedirs(hangar_config_file_path.replace('/hangar_config.json', ''))
            except OSError:
                LOG_NOTE('Config folder already exists.')
            hangar_config_file = open(hangar_config_file_path, 'w')
            json.dump(self.hangar_config, hangar_config_file)
            print '[OMNILAB: HangarSwitcher] Hangar config file not found! Created and loaded default in "mods/configs/wotclassic".'

        if self.hangar_config['is_prem_sensetive']:
            spacePaths = {True: self.PREM_SENSETIVE_HANGARS[self.hangar_config['current_hangar']]['premium'], False: self.PREM_SENSETIVE_HANGARS[self.hangar_config['current_hangar']]['basic']}
        else:
            spacePaths = {True: self.hangar_config['current_hangar'], False: self.hangar_config['current_hangar']}
        ClientHangarSpace._getHangarPath = lambda isPremium, _: 'spaces/' + spacePaths[isPremium] if self.hangarSwitchController.currentSceneName not in self.hangar_config['excepted_scenes'] else 'spaces/' + self.hangarSwitchController._sceneSpaceParams[self.hangarSwitchController.currentSceneName].getHangarSpaceId()


class HangarSwitcherWindow(AbstractWindowView):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HangarSwitcherWindow, self).__init__()

    def _populate(self):
        super(HangarSwitcherWindow, self)._populate()
        BigWorld.callback(0.01, self.currHangarCheck)

    def _noti(self, msg, isError=False):
        SystemMessages.pushMessage(msg, (SystemMessages.SM_TYPE.Information if not isError else SystemMessages.SM_TYPE.Error), priority=True)

    def onWindowClose(self):
        self.destroy()
        
    def saveHangarChoice(self, hanLinkage, isPremSensetive):
        g_classicHangarOverrider.processSceneChange(hanLinkage, isPremSensetive)

    def currHangarCheck(self):
        currHangar = self.hangarSpace.spacePath.split('/')[-1]
        
        if g_classicHangarOverrider.hangar_config['is_prem_sensetive']:
            for psHangarsSetName, psHangarsSetValue in g_classicHangarOverrider.PREM_SENSETIVE_HANGARS.items():
                for hangarName in psHangarsSetValue.values():
                    if hangarName == currHangar:
                        self.flashObject.as_setPremSensetive(True)
                        self.flashObject.PremSenseHanButtBar.selectedIndex = g_classicHangarOverrider.PREM_SENSETIVE_HANGARS.keys().index(psHangarsSetName)
                        return

        if currHangar in g_classicHangarOverrider.CLASSIC_HANGARS:
            self.flashObject.as_setPremSensetive(False)
            self.flashObject.StandardHanButtBar.selectedIndex = g_classicHangarOverrider.CLASSIC_HANGARS.index(currHangar)
            return
        elif currHangar in g_classicHangarOverrider.SPECIAL_HANGARS:
            self.flashObject.as_setPremSensetive(False)
            self.flashObject.SpecialHanButtBar.selectedIndex = g_classicHangarOverrider.SPECIAL_HANGARS.index(currHangar)
            return
        else:
            self.flashObject.as_setPremSensetive(False)

def callSwitcherWindow():
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    app.loadView(SFViewLoadParams('HangarSwitcherWindow'))

g_classicHangarOverrider = ClassicHangarOverrider()

g_modsListApi.addModification(id='HangarSwitcherWindow', name='#wek_hangarSwitcher:modButton/title', description='#wek_hangarSwitcher:modButton/tooltip',
            icon='gui/maps/icons/quests/bonuses/small/slots.png', enabled=True, login=False, lobby=True, callback=callSwitcherWindow)

''' For external import '''
if g_entitiesFactories.getSettings('HangarSwitcherWindow') is None:
    g_entitiesFactories.addSettings(ViewSettings('HangarSwitcherWindow', HangarSwitcherWindow, 'WoTCHangarSwitchWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE))
