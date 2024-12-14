from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VIEW_COMPONENT_RULE
from helpers import dependency, uniprof
from skeletons.gui.battle_session import IBattleSessionProvider

from .LegacyPreBattleTimer import LegacyPreBattleTimer

class _LegacyComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_LegacyComponentsConfig, self).__init__(config=((BATTLE_CTRL_ID.ARENA_PERIOD, ('LegacyPreBattleTimerUI', ))), viewsConfig=())

class LegacyBattlePage(View):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    
    @property
    def preBattleTimer(self):
        return self.getComponent('LegacyPreBattleTimerUI')

    def __init__(self):
        super(LegacyBattlePage, self).__init__()
        self.__componentsConfig = _LegacyComponentsConfig()

    def _populate(self):
        super(LegacyBattlePage, self)._populate()
    
    def _dispose(self):
        super(LegacyBattlePage, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        self.sessionProvider.addViewComponent(alias, viewPy)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        self.sessionProvider.removeViewComponent(alias)

    def pyLog(self, msg):
        print '[LegacyBattlePage]: %s' % msg

    def onAppResized(self, app_width, app_height):
        self.pyLog('%s, %s' % (app_width, app_height))