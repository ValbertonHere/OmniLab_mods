import logging, CGF, SoundGroups

from PlayerEvents import g_playerEvents

from frameworks.wulf import WindowLayer

from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.game_loading.resources.consts import Milestones
from gui.impl.common.fade_manager import useDefaultFade
from gui.shared import events, g_eventBus

from helpers import dependency

from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared.utils import IHangarSpace

from ._constants import HANGAR_NAME
from .main_view import LuganskHangarTravelGuideView
from .prefab_stuff import LuganskSelectionComponent

logger = logging.getLogger(__name__)

class LuganskHangarExtras():
    hangarSpace = dependency.descriptor(IHangarSpace)
    appLoader = dependency.descriptor(IAppLoader)
    uiLoader = dependency.descriptor(IGuiLoader)
    
    def __init__(self):
        logger.info('Lugansk extras inited!')
        g_playerEvents.onLoadingMilestoneReached += self.onHangarLoaded

    def onGameObjectClicked(self):
        self.__loadView()
        return
    
    def onGOloaded(self, go):
        selectionComponent = go.findComponentByType(LuganskSelectionComponent)
        if selectionComponent:
            selectionComponent.onClickAction += self.onGameObjectClicked

    def onHangarLoaded(self, milestoneName):
        if milestoneName == Milestones.HANGAR_READY:
            if self.hangarSpace.spacePath.split('/')[-1].lower() == HANGAR_NAME:
                try:
                    logger.info('Catching prefabs...')
                    luganskQuery = CGF.Query(self.hangarSpace.spaceID, (CGF.GameObject, LuganskSelectionComponent))
                    for _, selectionComponent in luganskQuery:
                        selectionComponent.onClickAction += self.onGameObjectClicked

                    logger.info('Complete!')
                except:
                    logger.exception('Error during loading hangar extras, send lines below to developer. Telegram: @lrvval.')
    
    @useDefaultFade(layer=WindowLayer.VIEW, fadeInDuration=.5, fadeOutDuration=1) 
    def __loadView(self):
        SoundGroups.g_instance.playSound2D('lugansk_travel_guide')
        SoundGroups.g_instance.playSound2D('lugansk_travel_guide_enter')
        loadParams = GuiImplViewLoadParams(layoutID=0, viewClass=LuganskHangarTravelGuideView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(loadParams))
