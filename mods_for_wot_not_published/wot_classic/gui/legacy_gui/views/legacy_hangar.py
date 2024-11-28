from GUI import screenResolution

from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers import dependency
from realm import CURRENT_REALM
from PlayerEvents import g_playerEvents
from CurrentVehicle import g_currentVehicle
from frameworks.wulf.gui_constants import WindowLayer

from gui.game_loading.resources.consts import Milestones
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.event_dispatcher import showResearchView

from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel import AmmunitionPanel
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.view.lobby.hangar.entry_points.event_entry_points_container import EventEntryPointsContainer
from gui.Scaleform.daapi.view.lobby.hangar.ResearchPanel import ResearchPanel
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES

from skeletons.gui.app_loader import IAppLoader

from . import getGUIConfig
from ..utils import override

class LegacyHangar(View, IGlobalListener):
    appLoader = dependency.instance(IAppLoader)
    
    def __init__(self):
        super(LegacyHangar, self).__init__()

        override(Hangar, '_Hangar__onTeaserReceived', self._Hangar__onTeaserReceived)
        override(Hangar, 'hideTeaser', self._Hangar_hideTeaser)
        override(EventEntryPointsContainer, 'as_updateEntriesS', self._EventEntryPointsContainer_as_updateEntriesS)
        override(ResearchPanel, 'as_updateCurrentVehicleS', self._ResearchPanel_as_updateCurrentVehicleS)
        override(AmmunitionPanelMeta, 'as_updateVehicleStatusS', self._AmmunitionPanelMeta_as_updateVehicleStatusS)
        override(AmmunitionPanelMeta, 'showRepairDialog', self._AmmunitionPanelMeta_showRepairDialog)
        if CURRENT_REALM != 'RU':
            override(Hangar, 'as_setPrestigeWidgetVisibleS', self._Hangar_as_setPrestigeWidgetVisibleS)

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
    
    def _Hangar__onTeaserReceived(self, base, baseSelf, teaserData, showCallback, closeCallback):
        baseSelf._Hangar__teaser = None
        return 

    def _Hangar_hideTeaser(self, base, baseSelf):
        baseSelf._Hangar__teaser = None
        return 

    def _EventEntryPointsContainer_as_updateEntriesS(self, base, baseSelf, data):
        base(baseSelf, [])

    def _ResearchPanel_as_updateCurrentVehicleS(self, base, baseSelf, _):
        if g_currentVehicle.isPresent():
            base(baseSelf, {'earnedXP': 0, 
                    'isElite': False, 
                    'vehCompareData': {'modeAvailable': False, 'btnEnabled': False, 'btnTooltip': ''}, 
                    'vehPostProgressionData': {'showCounter': False, 'btnEnabled': False, 'btnVisible': False}, 
                    'intCD': g_currentVehicle.item.intCD})
        else:
            base(baseSelf, {'earnedXP': 0})

    def _AmmunitionPanelMeta_as_updateVehicleStatusS(self, base, baseSelf, data):
        message = '<font face="$TitleFont" size="20" color="#497212">%s</font>' % g_currentVehicle.getHangarMessage()[1]

        if g_currentVehicle.getHangarMessage()[0] != 'undamaged':
            message = '<font face="$TitleFont" size="20" color="#9b0202">%s</font>' % g_currentVehicle.getHangarMessage()[1]

        data = {'message': message,
                    'rentAvailable': '',
                    'isElite': False,
                    'tankType': '',
                    'vehicleLevel': '',
                    'vehicleName': '',
                    'roleId': '',
                    'roleMessage': '', 
                    'vehicleCD': ''}
        base(baseSelf, data)

    def _AmmunitionPanelMeta_showRepairDialog(self, base, baseSelf):
        app = self.appLoader.getApp()
        app.loadView(SFViewLoadParams('TechnicalMaintenance'))

    def _Hangar_as_setPrestigeWidgetVisibleS(self, base, baseSelf, visible):
        base(baseSelf, False)

    @property
    def researchPanel(self):
        return self.getComponent('LegacyResearchPanelUI')
    
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

    def pyLog(self, msg):
        print '[OMNILAB: LegacyHangar] %s' % msg

    def closeView(self):
        self.destroy()

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
                    nig = view.flashObject.getDisplayInfo()
                    nig.y = 65
                    view.flashObject.setDisplayInfo(nig)
                elif view.alias == VIEW_ALIAS.LOBBY_TECHTREE:
                    view.flashObject.nationTree.levelsBg.visible = False
                    view.flashObject.background.y = 65
                elif view.alias in (VIEW_ALIAS.LOBBY_HANGAR, VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, VIEW_ALIAS.BADGES_PAGE, VIEW_ALIAS.MANUAL_CHAPTER_VIEW):
                    view.flashObject.updateStage(self.__appWidth, self.__appHeight-125)
                    nig = view.flashObject.getDisplayInfo()
                    nig.y = 40
                    view.flashObject.setDisplayInfo(nig)
                elif view.alias == VIEW_ALIAS.LOBBY_CUSTOMIZATION:
                    view.flashObject.updateStage(self.__appWidth, self.__appHeight-180)
                    nig = view.flashObject.getDisplayInfo()
                    nig.y = 95
                    view.flashObject.setDisplayInfo(nig)

        except Exception:
            LOG_CURRENT_EXCEPTION()

    def guiTrainingsSubViewReplace(self):
        trainView = self._getHangarSrc()
        nig = trainView.flashObject.getDisplayInfo()
        nig.y = -80
        trainView.flashObject.setDisplayInfo(nig)

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