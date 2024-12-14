from gui.Scaleform.daapi.view.battle.shared.prebattle_timers.timer_base import _STATE_TO_MESSAGE, PreBattleTimerBase
from gui.Scaleform.daapi.view.meta.PrebattleTimerMeta import PrebattleTimerMeta
from gui.impl import backport
from gui.Scaleform.framework.entities.View import View
from constants import ARENA_PERIOD
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

from ..avatar_hooks import g_prbTimerHooks

class LegacyPreBattleTimer(View):
    def __init__(self):
        super(LegacyPreBattleTimer, self).__init__()

    def _populate(self):
        super(LegacyPreBattleTimer, self)._populate()
        g_prbTimerHooks.preBattleTimerSWF = self

        self.as_setMessages()
        
    def _dispose(self):
        g_prbTimerHooks.preBattleTimerSWF = None
        super(LegacyPreBattleTimer, self)._dispose()

    def as_setMessages(self):
        if self._isDAAPIInited():
            self.flashObject.as_setTimerPeriod(g_prbTimerHooks.arenaPeriod != ARENA_PERIOD.PREBATTLE)
            self.flashObject.as_setMessage(backport.text(_STATE_TO_MESSAGE[g_prbTimerHooks.state]))
            self.flashObject.as_setWinText(g_prbTimerHooks.battleWinText)
            if g_prbTimerHooks.arenaPeriod == ARENA_PERIOD.BATTLE:
                self.flashObject.as_hideAll(False)

    def pyLog(self, msg):
        print msg