

import CGF
import BigWorld
import logging
import SoundGroups
from cgf_components.hangar_camera_manager import HangarCameraManager
from frameworks.wulf import ViewModel
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings, ViewFlags
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.impl.common.fade_manager import useDefaultFade
from frameworks.wulf import WindowLayer

logger = logging.getLogger(__name__)

try: 
    from openwg_gameface import ModDynAccessor
except ImportError:
  logger.critical('\n' +
                  "!!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!\n"
                  "!!!\n"
                  "!!!   Valberton's Lobby Header Inject mod requires the openwg_gameface module to function.\n"
                  "!!!   Without it, this and other GF UI mods will not work correctly.\n"
                  "!!!   Please download and install it from: https://gitlab.com/openwg/wot.gameface/-/releases/\n"
                  "!!!\n"
                  "!!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!\n")

  BigWorld.crash(1)

MTO_LEGACY_LOBBY_HEADER = 'MTOLegacyLobbyHeader'
STAND_ID_TO_CAMERA = {'main': 'MainViewCamera',
                      'graphics': 'GraphicsStandCamera',
                      'ui_hngr': 'UIAndHangarsStandCamera',
                      'sounds': 'SoundsStandCamera'}
WWISE_STAND_STATE = 'SWITCH_mto_lugansk_travel_guide_stand'


class MTOLegacyLobbyHeaderModel(ViewModel):
  
    def __init__(self, properties=0, commands=1):
        super(MTOLegacyLobbyHeaderModel, self).__init__(properties=properties, commands=commands)
    
    def _initialize(self):
        super(MTOLegacyLobbyHeaderModel, self)._initialize()
        self._addStringProperty('standID')
        self.onClick = self._addCommand('onClick')
    
    def setStandID(self, standID):
        self._setString(0, standID)

class MTOLegacyLobbyHeader(ViewImpl):
    hangarSpace = dependency.descriptor(IHangarSpace)
    viewLayoutID = ModDynAccessor(MTO_LEGACY_LOBBY_HEADER)
    
    def __init__(self, layoutID=None):
        settings = ViewSettings(MTOLegacyLobbyHeader.viewLayoutID(), flags=ViewFlags.LOBBY_SUB_VIEW, model=MTOLegacyLobbyHeaderModel())
        super(MTOLegacyLobbyHeader, self).__init__(settings)
        self.currentStand = None
        self.viewModel.onClick += self.onClick

    @property
    def viewModel(self):
        return super(MTOLegacyLobbyHeader, self).getViewModel()
    
    def _onLoading(self, *args, **kwargs):
        super(MTOLegacyLobbyHeader, self)._onLoading()
        self.currentStand = 'main'
        # self.switchStandWithoutFade('main')
    
    def switchStandWithoutFade(self, standID):
        cameraMgr = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
        if cameraMgr:
            cameraMgr.switchByCameraName(STAND_ID_TO_CAMERA[standID])
            SoundGroups.g_instance.setState(WWISE_STAND_STATE, WWISE_STAND_STATE + '_%s' % standID)

    @useDefaultFade(layer=WindowLayer.SUB_VIEW, fadeInDuration=.5, fadeOutDuration=.5)
    def switchStandWithFade(self, standID):
        cameraMgr = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
        if cameraMgr:
            cameraMgr.switchByCameraName(STAND_ID_TO_CAMERA[standID])
            self.viewModel.setStandID(standID)
            SoundGroups.g_instance.setState(WWISE_STAND_STATE, WWISE_STAND_STATE + '_%s' % standID)

    def onClick(self, ctx):
        standID = ctx['standID']

        if self.currentStand != standID:
            self.switchStand(standID)
            self.currentStand = standID

'''
# From PjOrion
from gui.mods.mod_lugansk import MTOLegacyLobbyHeader, MTO_LEGACY_LOBBY_HEADER
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from openwg_gameface import res_id_by_key
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.impl.common.fade_manager import FadeManager
import GUI
from gui.impl.common.fade_manager import useDefaultFade
from frameworks.wulf import WindowLayer
from armory_yard.managers.fade_manager import ArmoryYardFadeManager
from adisp import adisp_process

uiLoader = dependency.instance(IGuiLoader)
loadParams = GuiImplViewLoadParams(layoutID=0, viewClass=MTOLegacyLobbyHeader, scope=ScopeTemplates.LOBBY_SUB_SCOPE)

def work():
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(loadParams))

def loadWindow():
    uiLoader = dependency.instance(IGuiLoader)
    view = uiLoader.windowsManager.getViewByLayoutID(res_id_by_key(MTO_LEGACY_LOBBY_HEADER))
    if view:
        view.destroy()
    window = MTOLegacyLobbyHeader()
    BigWorld.callback(0, lambda: work())

loadWindow()
'''