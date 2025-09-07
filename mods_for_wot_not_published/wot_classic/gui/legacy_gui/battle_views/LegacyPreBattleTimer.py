from gui.Scaleform.daapi.view.battle.shared.prebattle_timers.timer_base import _STATE_TO_MESSAGE, PreBattleTimerBase
from gui.impl import backport
from constants import ARENA_PERIOD
from gui.battle_control.battle_constants import COUNTDOWN_STATE

class LegacyPreBattleTimer(PreBattleTimerBase):

    def __init__(self):
        super(LegacyPreBattleTimer, self).__init__()
        self._state = COUNTDOWN_STATE.WAIT
        self._battleWinText = self.sessionProvider.getCtx().getArenaWinString()
        self.__arenaPeriod = None

    def setPeriod(self, period):
        if self.__arenaPeriod is None and period == ARENA_PERIOD.BATTLE and self._isDAAPIInited():
            self.flashObject.as_hideAll(False)
        self.__arenaPeriod = period
    
    def setCountdown(self, state, timeLeft):
        if self._state != state:
            self._state = state
        if self._isDAAPIInited():
            self.flashObject.as_setTimer(timeLeft)
            self.as_setMessages()

    def hideCountdown(self, state, speed):
        if self._state != state:
            self._state = state
        if self._isDAAPIInited():
            self.flashObject.as_hideAll(speed != 0)
            self.as_setMessages()
    
    def updateBattleCtx(self, battleCtx):
        self._battleWinText = battleCtx.getArenaWinString()
    
    def updateRespawnTime(self, timeLeft):
        if self._isDAAPIInited():
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