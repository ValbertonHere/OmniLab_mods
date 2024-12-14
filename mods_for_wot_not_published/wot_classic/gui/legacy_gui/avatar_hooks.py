
from gui.Scaleform.daapi.view.battle.shared.prebattle_timers.timer_base import PreBattleTimerBase
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from battle_royale.gui.Scaleform.daapi.view.battle.respawn_message_panel import RespawnMessagePanel
from constants import ARENA_PERIOD

#from .battle_views.LegacyPreBattleTimer import LegacyPreBattleTimer
from .utils import override

class PreBattleTimerHooks():
    appLoader = dependency.instance(IAppLoader)

    def __init__(self):
        self.state = COUNTDOWN_STATE.WAIT
        self.battleWinText = None
        self.preBattleTimerSWF = None
        self.arenaPeriod = None

        override(SharedPage, '_populate', self._SharedPage__populate)
        override(PreBattleTimerBase, 'setPeriod', self._PreBattleTimer_setPeriod)
        override(PreBattleTimerBase, 'setCountdown', self._PreBattleTimer_setCountdown)
        override(PreBattleTimerBase, 'hideCountdown', self._PreBattleTimer_hideCountdown)
        override(PreBattleTimerBase, 'updateBattleCtx', self._PreBattleTimer_updateBattleCtx)
        override(SharedPage, '_onRegisterFlashComponent', self._SharedPage__onRegisterFlashComponent)
        override(RespawnMessagePanel, 'updateRespawnTime', self._RespawnMessagePanel_updateRespawnTime)
        
    def _SharedPage__populate(self, base, baseSelf):
        base(baseSelf)

        app = self.appLoader.getApp()
        app.graphicsOptimizationManager.switchOptimizationEnabled(False)
        app.loadView(SFViewLoadParams('LegacyBattlePageUI'))

    def _SharedPage__onRegisterFlashComponent(self, base, baseSelf, viewPy, alias):
        base(baseSelf, viewPy, alias)

    def _PreBattleTimer_setPeriod(self, base, baseSelf, period):
        if self.arenaPeriod is None and period == ARENA_PERIOD.BATTLE and self.preBattleTimerSWF is not None:
            self.preBattleTimerSWF.flashObject.as_hideAll(False)
        self.arenaPeriod = period
    
    def _PreBattleTimer_setCountdown(self, base, baseSelf, state, timeLeft):
        if self.state != state:
            self.state = state
        if self.preBattleTimerSWF is not None:
            self.preBattleTimerSWF.flashObject.as_setTimer(timeLeft)
            self.as_setMessages()

    def _PreBattleTimer_hideCountdown(self, base, baseSelf, state, speed):
        if self.state != state:
            self.state = state
        if self.preBattleTimerSWF is not None:
            self.preBattleTimerSWF.flashObject.as_hideAll(speed != 0)
            self.as_setMessages()
    
    def _PreBattleTimer_updateBattleCtx(self, base, baseSelf, battleCtx):
        self.battleWinText = battleCtx.getArenaWinString()
        base(baseSelf, battleCtx)
    
    def _RespawnMessagePanel_updateRespawnTime(self, base, baseSelf, timeLeft):
        if self.preBattleTimerSWF is not None:
            print timeLeft
            self.preBattleTimerSWF.flashObject.as_setTimer(timeLeft)
            self.preBattleTimerSWF.flashObject.as_setTimerPeriod(False)
            self.preBattleTimerSWF.flashObject.as_setMessage('#battle_royale:battle/respawnMessagePanel/respawnActivated/title')
            if timeLeft == 0:
                self.preBattleTimerSWF.flashObject.as_hideAll(False)
    
g_prbTimerHooks = PreBattleTimerHooks()

print 'NIGGER'