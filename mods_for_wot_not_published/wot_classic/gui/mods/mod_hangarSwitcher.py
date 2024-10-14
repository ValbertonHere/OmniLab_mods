import BigWorld, json, os

from ResMgr import isDir
from gui.modsListApi import g_modsListApi
from gui.shared.utils.hangar_space_reloader import HangarSpaceReloader
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared.utils.hangar_space_reloader import HangarSpaceReloader
from gui import ClientHangarSpace, SystemMessages
from skeletons.gui.shared.utils import IHangarSpace

class HangarSwitcherWindow(AbstractWindowView):
    hangarSpace = dependency.descriptor(IHangarSpace)
    CLASSIC_HANGARS = ('hangar', 'hangar_premium', 'hangar_v2', 'hangar_premium_v2')

    def __init__(self):
        super(HangarSwitcherWindow, self).__init__()

    def _populate(self):
        super(HangarSwitcherWindow, self)._populate()
        BigWorld.callback(0.01, self.currHangarCheck)

    def _noti(msg, isError=False):
        SystemMessages.pushMessage(msg, (SystemMessages.SM_TYPE.Information if not isError else SystemMessages.SM_TYPE.Error), priority=True)

    def onWindowClose(self):
        self.destroy()
    
    def pyLog(self, msg):
        print msg
        
    def saveHangarChoice(self, hanName):
        spacePath = 'spaces/%s' % hanName
        if isDir(spacePath) == 1:
            ClientHangarSpace._getHangarPath = lambda nigger1, nigger2: spacePath
            updateHangarConfig(hanName, True)
            HangarSpaceReloader().changeHangarSpace(hanName, None)
        else:
            self._noti('#wek_hangarSwitcher:loadError/hangarExists', True)

    def currHangarCheck(self):
        currHangar = self.hangarSpace.spacePath.split('/')[-1]
        if currHangar in self.CLASSIC_HANGARS:
            self.flashObject.hanButtBar.selectedIndex = self.CLASSIC_HANGARS.index(currHangar)

def callSwitcherWindow():
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    app.loadView(SFViewLoadParams('HangarSwitcherWindow'))

def updateHangarConfig(spaceName=None, needToWrite=False):
    hangar_config_file_path = 'mods/configs/wotclassic/hangar_config.json'
    if os.path.isfile(hangar_config_file_path):
        with open(hangar_config_file_path, 'r') as f2r:
            data = json.load(f2r)
            hangar_config.update(data)
        if needToWrite:
            with open(hangar_config_file_path, 'w') as f2w:
                hangar_config['currHangar'] = spaceName
                json.dump(hangar_config, f2w)
    else:
        os.mkdir(hangar_config_file_path.replace('/hangar_config.json', ''))
        hangar_config_file = open(hangar_config_file_path, 'w')
        json.dump(hangar_config, hangar_config_file)
        print '[OMNILAB: HangarSwitcher] Hangar config file not found! Created and loaded default in "mods/configs/wotclassic".'

hangar_config = {
    'currHangar': 'hangar_v2'
}
updateHangarConfig()
ClientHangarSpace._getHangarPath = lambda nigger1, nigger2: 'spaces/' + hangar_config['currHangar']

g_modsListApi.addModification(id='HangarSwitcherWindow', name='#wek_hangarSwitcher:modButton/title', description='#wek_hangarSwitcher:modButton/tooltip',
            icon='gui/maps/icons/quests/bonuses/small/slots.png', enabled=True, login=False, lobby=True, callback=callSwitcherWindow)

g_entitiesFactories.addSettings(ViewSettings('HangarSwitcherWindow', HangarSwitcherWindow, 'WoTCHangarSwitchWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE))