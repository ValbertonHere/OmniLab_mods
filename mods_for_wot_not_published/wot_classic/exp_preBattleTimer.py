import BigWorld, json, os

from gui.Scaleform.daapi.view.battle.shared.prebattle_timers.timer_base import _STATE_TO_MESSAGE, PreBattleTimerBase
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.impl import backport
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.entities.View import View
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from OpenModsCore import overrideMethod
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from battle_royale.gui.Scaleform.daapi.view.battle.respawn_message_panel import RespawnMessagePanel
from constants import ARENA_PERIOD

class LegacyPreBattleTimer(View):
    def __init__(self):
        super(LegacyPreBattleTimer, self).__init__()
        self._state = COUNTDOWN_STATE.WAIT
        self.__arenaPeriod = None

        overrideMethod(PreBattleTimerBase, 'setPeriod', self._PreBattleTimer_setPeriod)
        overrideMethod(PreBattleTimerBase, 'setCountdown', self._PreBattleTimer_setCountdown)
        overrideMethod(PreBattleTimerBase, 'hideCountdown', self._PreBattleTimer_hideCountdown)
        overrideMethod(PreBattleTimerBase, 'updateBattleCtx', self._PreBattleTimer_updateBattleCtx)
        overrideMethod(RespawnMessagePanel, 'updateRespawnTime', self._RespawnMessagePanel_updateRespawnTime)
        return

    def _PreBattleTimer_setPeriod(self, base, baseSelf, period):
        if self.__arenaPeriod is None and period == ARENA_PERIOD.BATTLE and self._isDAAPIInited():
            self.flashObject.as_hideAll(False)
        self.__arenaPeriod = period
    
    def _PreBattleTimer_setCountdown(self, base, baseSelf, state, timeLeft):
        if self._state != state:
            self._state = state
        if self._isDAAPIInited():
            self.flashObject.as_setTimer(timeLeft)
            self.as_setMessages()

    def _PreBattleTimer_hideCountdown(self, base, baseSelf, state, speed):
        if self._state != state:
            self._state = state
        if self._isDAAPIInited():
            self.flashObject.as_hideAll(speed != 0)
            self.as_setMessages()
    
    def _PreBattleTimer_updateBattleCtx(self, base, baseSelf, battleCtx):
        self._battleWinText = battleCtx.getArenaWinString()
        base(baseSelf, battleCtx)
    
    def _RespawnMessagePanel_updateRespawnTime(self, base, baseSelf, timeLeft):
        if self._isDAAPIInited():
            print timeLeft
            self.flashObject.as_setTimer(timeLeft)
            self.flashObject.as_setTimerPeriod(False)
            self.flashObject.as_setMessage('#battle_royale:battle/respawnMessagePanel/respawnActivated/title')
            if timeLeft == 0:
                self.flashObject.as_hideAll(False)

    def _populate(self):
        super(LegacyPreBattleTimer, self)._populate()
        self.as_setMessages()
        
    def _dispose(self):
        super(LegacyPreBattleTimer, self)._dispose()

    def as_setMessages(self):
        if self._isDAAPIInited():
            self.flashObject.as_setTimerPeriod(self.__arenaPeriod != ARENA_PERIOD.PREBATTLE)
            self.flashObject.as_setMessage(backport.text(_STATE_TO_MESSAGE[self._state]))
            self.flashObject.as_setWinText(self._battleWinText)
            if self.__arenaPeriod == ARENA_PERIOD.BATTLE:
                self.flashObject.as_hideAll(False)

    def pyLog(self, msg):
        print msg

g_entitiesFactories.addSettings(ViewSettings('LegacyPreBattleTimerUI', LegacyPreBattleTimer, 'legacyPreBattleTimer.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE))

@overrideMethod(SharedPage, '_onRegisterFlashComponent')
def onPBTPopulate(base, self, viewPy, alias):
    base(self, viewPy, alias)
    if alias == BATTLE_VIEW_ALIASES.PREBATTLE_TIMER:
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        app.loadView(SFViewLoadParams('LegacyPreBattleTimerUI'))