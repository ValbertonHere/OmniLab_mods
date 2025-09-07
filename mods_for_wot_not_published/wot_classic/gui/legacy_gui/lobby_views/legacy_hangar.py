from GUI import screenResolution

from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers import dependency
from PlayerEvents import g_playerEvents
from CurrentVehicle import g_currentVehicle
from frameworks.wulf.gui_constants import WindowLayer

from gui.game_loading.resources.consts import Milestones
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showResearchView

from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES

from skeletons.gui.app_loader import IAppLoader

from . import getGUIConfig

from ..utils import restartOnlyHangar

class LegacyHangar(View, IGlobalListener):
    appLoader = dependency.instance(IAppLoader)
    
    def __init__(self):
        super(LegacyHangar, self).__init__()

    def _populate(self):
        super(LegacyHangar, self)._populate()
        self.__appWidth = screenResolution()[0]
        self.__appHeight = screenResolution()[1]

        if getGUIConfig()['isLegacyLobbyHeaderEnabled']:
            g_playerEvents.onLoadingMilestoneReached += self.onHangarUIReady
            self.startGlobalListening()
            self.onPrbEntitySwitched()
            self.guiSubViewsReplace(None, self._getHangarSrc())
    
    def _dispose(self):
        if getGUIConfig()['isLegacyLobbyHeaderEnabled']:
            self.stopGlobalListening()
        super(LegacyHangar, self)._dispose()
    
    def _getHangarSrc(self):
        app = self.appLoader.getApp()
        return app.containerManager.getContainer(WindowLayer.VIEW).getChildContainer(5).getView()

    @property
    def researchPanel(self):
        return self.getComponent('LegacyResearchPanelUI')
    
    @property
    def vehicleParams(self):
        return self.getComponent('LegacyVehicleParamsUI')
    
    def onAppResized(self, appWidth, appHeight):
        if getGUIConfig()['isLegacyLobbyHeaderEnabled']:
            self.__appWidth = appWidth
            self.__appHeight = appHeight

            self.guiSubViewsReplace(None, self._getHangarSrc())

    def onPrbEntitySwitched(self):
        if self.prbDispatcher is not None:
            state = self.prbDispatcher.getFunctionalState()
            isInCorrectPreQueue = state.isInPreQueue(QUEUE_TYPE.BATTLE_ROYALE) or state.isInPreQueue(400)
            isInCorrectUnit =  state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE) or state.isInUnit(400)
            self.researchPanel.flashObject.visible = not (isInCorrectPreQueue or isInCorrectUnit)

    def reloadView(self):
        restartOnlyHangar()

    def showResearch(self):
        if g_currentVehicle.isPresent():
            showResearchView(g_currentVehicle.item.intCD)

    def guiSubViewsReplace(self, container, view):
        try:
            if container is None:
                cont_layer = view.layer
            else:
                cont_layer = container.getLayer()
            
            if cont_layer in (WindowLayer.SUB_VIEW, WindowLayer.TOP_SUB_VIEW) and hasattr(view, 'flashObject'):
                if view.alias in (VIEW_ALIAS.LOBBY_STORE, VIEW_ALIAS.LOBBY_STORAGE, VIEW_ALIAS.LOBBY_MISSIONS, VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS,
                                VIEW_ALIAS.LOBBY_PROFILE, VIEW_ALIAS.VEHICLE_PREVIEW, VIEW_ALIAS.HERO_VEHICLE_PREVIEW, VIEW_ALIAS.VEH_POST_PROGRESSION,
                                VIEW_ALIAS.VEHICLE_COMPARE, VIEW_ALIAS.AMMUNITION_SETUP_VIEW, VIEW_ALIAS.PERSONAL_MISSIONS_PAGE, VIEW_ALIAS.LOBBY_PERSONAL_MISSION_DETAILS,
                                PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS, PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_VIEW_ALIAS,
                                VIEW_ALIAS.PERSONAL_MISSIONS_BROWSER_VIEW, VIEW_ALIAS.LOBBY_STRONGHOLD, VIEW_ALIAS.WIKI_VIEW, VIEW_ALIAS.STYLE_PREVIEW, 
                                VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW, VIEW_ALIAS.SHOWCASE_STYLE_BUYING_PREVIEW, VIEW_ALIAS.MANUAL_BROWSER_VIEW, VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB):
                    view.flashObject.updateStage(self.__appWidth, self.__appHeight-155)
                    displayInfo = view.flashObject.getDisplayInfo()
                    displayInfo.y = 65
                    view.flashObject.setDisplayInfo(displayInfo)
                elif view.alias == VIEW_ALIAS.LOBBY_TECHTREE:
                    view.flashObject.nationTree.levelsBg.visible = False
                    view.flashObject.background.y = 65
                elif view.alias in (VIEW_ALIAS.LOBBY_HANGAR, VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, VIEW_ALIAS.BADGES_PAGE, VIEW_ALIAS.MANUAL_CHAPTER_VIEW):
                    view.flashObject.updateStage(self.__appWidth, self.__appHeight-125)
                    displayInfo = view.flashObject.getDisplayInfo()
                    displayInfo.y = 40
                    view.flashObject.setDisplayInfo(displayInfo)
                elif view.alias == VIEW_ALIAS.LOBBY_CUSTOMIZATION:
                    view.flashObject.updateStage(self.__appWidth, self.__appHeight-180)
                    displayInfo = view.flashObject.getDisplayInfo()
                    displayInfo.y = 95
                    view.flashObject.setDisplayInfo(displayInfo)

        except Exception:
            LOG_CURRENT_EXCEPTION()

    def guiTrainingsSubViewReplace(self):
        trainView = self._getHangarSrc()
        displayInfo = trainView.flashObject.getDisplayInfo()
        displayInfo.y = -80
        trainView.flashObject.setDisplayInfo(displayInfo)

    def onHangarUIReady(self, milestone):
        if (milestone == Milestones.HANGAR_READY or milestone == Milestones.HANGAR_UI_READY):
            try:
                appLoader = dependency.instance(IAppLoader)
                app = appLoader.getApp()
                if self.guiSubViewsReplace not in app.containerManager.onViewAddedToContainer:
                    app.containerManager.onViewAddedToContainer += self.guiSubViewsReplace
            except Exception:
                LOG_CURRENT_EXCEPTION()

print '[OMNILAB R&D: views.LegacyHangar] INITIALIZED!'