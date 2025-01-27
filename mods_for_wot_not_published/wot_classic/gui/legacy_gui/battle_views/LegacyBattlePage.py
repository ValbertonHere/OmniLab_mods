from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VIEW_COMPONENT_RULE
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.app_loader import GuiGlobalSpaceID, IAppLoader

class _LegacyComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_LegacyComponentsConfig, self).__init__(config=((BATTLE_CTRL_ID.ARENA_PERIOD, ('LegacyPreBattleTimerUI', ))), viewsConfig=())

class LegacyBattlePage(View):
    appLoader = dependency.descriptor(IAppLoader)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    
    @property
    def preBattleTimer(self):
        return self.getComponent('LegacyPreBattleTimerUI')

    def __init__(self):
        super(LegacyBattlePage, self).__init__()
        self.__componentsConfig = _LegacyComponentsConfig()

    def _populate(self):
        self.addListener(events.GameEvent.RADIAL_MENU_CMD, self._handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self._handleToggleFullStatsQuestProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_STATS_PERSONAL_RESERVES, self._handleToggleFullStatsPersonalReserves, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.TOGGLE_GUI, self._handleGUIToggled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.ViewEventType.LOAD_VIEW, self.__handleLobbyEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.sessionProvider.registerViewComponents(self.__componentsConfig.getConfig())
        self.sessionProvider.addViewComponent('LegacyPreBattleTimerUI', self.preBattleTimer, rule=VIEW_COMPONENT_RULE.NONE)
        super(LegacyBattlePage, self)._populate()
        if self.appLoader.getSpaceID() == GuiGlobalSpaceID.BATTLE_LOADING and self._isDAAPIInited():
            self.flashObject.as_setComponentsVisibility('LegacyPreBattleTimerUI', False)
    
    def _dispose(self):
        self.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.RADIAL_MENU_CMD, self._handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self._handleToggleFullStatsQuestProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_STATS_PERSONAL_RESERVES, self._handleToggleFullStatsPersonalReserves, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.TOGGLE_GUI, self._handleGUIToggled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.ViewEventType.LOAD_VIEW, self.__handleLobbyEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        super(LegacyBattlePage, self)._dispose()

    def _handleRadialMenuCmd(self, event):
        if self._isDAAPIInited():
            self.flashObject.as_setComponentsVisibility('LegacyPreBattleTimerUI', not event.ctx['isDown'])
            
    def _handleToggleFullStats(self, event):
        if self._isDAAPIInited():
            self.flashObject.as_setComponentsVisibility('LegacyPreBattleTimerUI', not event.ctx['isDown'])

    def _handleToggleFullStatsQuestProgress(self, event):
        if self._isDAAPIInited():
            self.flashObject.as_setComponentsVisibility('LegacyPreBattleTimerUI', not event.ctx['isDown'])

    def _handleToggleFullStatsPersonalReserves(self, event):
        if self._isDAAPIInited():
            self.flashObject.as_setComponentsVisibility('LegacyPreBattleTimerUI', not event.ctx['isDown'])

    def _handleGUIToggled(self, event):
        if self._isDAAPIInited():
            self.flashObject.as_setComponentsVisibility('LegacyPreBattleTimerUI', not event.ctx['isDown'])

    def _handleHelpEvent(self, event):
        if self._isDAAPIInited():
            self.flashObject.as_setComponentsVisibility('LegacyPreBattleTimerUI', not event.ctx['isDown'])

    def __handleLobbyEvent(self, event):
        if event.alias in (VIEW_ALIAS.INGAME_HELP, VIEW_ALIAS.INGAME_DETAILS_HELP):
            self._handleHelpEvent(event)

    def __handleBattleLoading(self, event):
        if self._isDAAPIInited():
            self.flashObject.as_setComponentsVisibility('LegacyPreBattleTimerUI', not event.ctx['isShown'])
    
    def _onRegisterFlashComponent(self, viewPy, alias):
        self.sessionProvider.addViewComponent(alias, viewPy)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        self.sessionProvider.removeViewComponent(alias)

    def pyLog(self, msg):
        print '[LegacyBattlePage]: %s' % msg

    def onAppResized(self, app_width, app_height):
        self.pyLog('%s, %s' % (app_width, app_height))