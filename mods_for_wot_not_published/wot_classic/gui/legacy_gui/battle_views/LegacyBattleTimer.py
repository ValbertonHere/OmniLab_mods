from gui.Scaleform.daapi.view.battle.shared.battle_timers import BattleTimer, _BATTLE_END_TIME

class LegacyBattleTimer(BattleTimer):
    def __init__(self):
        super(LegacyBattleTimer, self).__init__()
        self.__endingSoonTime = 60

    def setTotalTime(self, totalTime):
        minutes, seconds = divmod(int(totalTime), 60)
        if _BATTLE_END_TIME <= totalTime <= self.__endingSoonTime:
            if not self._BattleTimer__isTicking:
                self._startTicking()
        elif self._BattleTimer__isTicking:
            self.__stopTicking()
        self._sendTime(minutes, seconds)

    def _startTicking(self):
        self._BattleTimer__isTicking = True
        self._setColor()

    def __stopTicking(self):
        self._BattleTimer__isTicking = False
        self._setColor()