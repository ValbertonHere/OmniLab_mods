import BigWorld, CGF, logging, SoundGroups

from cgf_components.hangar_camera_manager import HangarCameraManager

from frameworks.wulf import ViewFlags, ViewModel, ViewSettings, WindowLayer

from gui import InputHandler
from gui.impl.common.fade_manager import useDefaultFade
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showHangar
from gui.shared.utils.key_mapping import getBigworldNameFromKey

from helpers import dependency

from openwg_gameface import ModDynAccessor

from skeletons.gui.shared.utils import IHangarSpace

from _constants import LUGANSK_HANGAR_TGUIDE_VIEW, STAND_ID_TO_CAMERA, STAND_ID_TO_LIGHT_PARAMS, WWISE_STAND_SWITCH, WWISE_TGUIDE_RTPC

logger = logging.getLogger(__name__)

class LuganskHangarTravelGuideViewModel(ViewModel):
  
    def __init__(self, properties=0, commands=1):
        super(LuganskHangarTravelGuideViewModel, self).__init__(properties=properties, commands=commands)
    
    def _initialize(self):
        super(LuganskHangarTravelGuideViewModel, self)._initialize()
        self._addStringProperty('standID')
        self.onFooterItemClick = self._addCommand('onFooterItemClick')
        self.onCloseClick = self._addCommand('onCloseClick')
    
    def setStandID(self, standID):
        self._setString(0, standID)

class LuganskHangarTravelGuideView(ViewImpl):
    hangarSpace = dependency.descriptor(IHangarSpace)
    viewLayoutID = ModDynAccessor(LUGANSK_HANGAR_TGUIDE_VIEW)
    
    def __init__(self, layoutID=None):
        settings = ViewSettings(LuganskHangarTravelGuideView.viewLayoutID(), flags=ViewFlags.LOBBY_SUB_VIEW, model=LuganskHangarTravelGuideViewModel())
        super(LuganskHangarTravelGuideView, self).__init__(settings)
        self.standLight = BigWorld.PySpotLight()
        self.standLight.multiplier = 10000
        self.standLight.castShadows = True
        self.standLight.outerRadius = 20.0
        self.currentStand = None
        self.viewModel.onFooterItemClick += self.onFooterItemClick
        self.viewModel.onCloseClick += self.onCloseClick

    @property
    def viewModel(self):
        return super(LuganskHangarTravelGuideView, self).getViewModel()
    
    def _initialize(self, *args, **kwargs):
        SoundGroups.g_instance.setRTPC(WWISE_TGUIDE_RTPC, 0)
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': False}), EVENT_BUS_SCOPE.LOBBY)
        InputHandler.g_instance.onKeyDown += self.onEscape
    
    def _onLoading(self, *args, **kwargs):
        super(LuganskHangarTravelGuideView, self)._onLoading()
        self.currentStand = 'main'
        self.__switchStand('main')

    def _finalize(self):
        super(LuganskHangarTravelGuideView, self)._finalize()
        InputHandler.g_instance.onKeyDown -= self.onEscape
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': True}), EVENT_BUS_SCOPE.LOBBY)
        cameraMgr = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
        if cameraMgr:
            cameraMgr.switchToTank()

    @useDefaultFade(layer=WindowLayer.SUB_VIEW, fadeInDuration=0.5, fadeOutDuration=0.5)
    def switchStandWithFade(self, standID):
        self.__switchStand(standID)
        self.viewModel.setStandID(standID)
    
    def __switchStand(self, standID):
        self.__changeStandLight(standID)
        cameraMgr = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
        if cameraMgr:
            cameraMgr.switchByCameraName(STAND_ID_TO_CAMERA[standID])
            SoundGroups.g_instance.setSwitch(WWISE_STAND_SWITCH, WWISE_STAND_SWITCH + '_%s' % standID)

    def onFooterItemClick(self, ctx):
        standID = ctx['standID']

        if self.currentStand != standID:
            self.switchStandWithFade(standID)
            self.currentStand = standID
    
    def onCloseClick(self):
        self.__destroyWithFade()
    
    def __changeStandLight(self, standID):
        self.standLight.direction, self.standLight.position = STAND_ID_TO_LIGHT_PARAMS[standID]

    @useDefaultFade(layer=WindowLayer.VIEW, fadeInDuration=.5, fadeOutDuration=.5)
    def __destroyWithFade(self):
        SoundGroups.g_instance.setSwitch(WWISE_STAND_SWITCH, WWISE_STAND_SWITCH + '_main')
        SoundGroups.g_instance.playSound2D('lugansk_travel_guide_exit')
        SoundGroups.g_instance.playSound2D('lugansk_travel_guide_stop')
        SoundGroups.g_instance.setRTPC(WWISE_TGUIDE_RTPC, 100)

        self.standLight.destroyLight()
        self.standLight = None
        showHangar()

    def onEscape(self, event):
        key = getBigworldNameFromKey(event.key)
        if key == 'KEY_ESCAPE':
            self.__destroyWithFade()