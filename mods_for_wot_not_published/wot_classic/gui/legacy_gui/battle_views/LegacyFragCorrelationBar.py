from debug_utils import LOG_NOTE
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class LegacyFragCorrelationBar(BaseDAAPIComponent, IBattleFieldListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LegacyFragCorrelationBar, self).__init__()

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def _populate(self):
        super(LegacyFragCorrelationBar, self)._populate()
        self.sessionProvider.addArenaCtrl(self)

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        super(LegacyFragCorrelationBar, self)._dispose()
    
    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        pass

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        LOG_NOTE(aliveAllies, deadAllies, aliveEnemies, deadEnemies)
        if self._isDAAPIInited():
            self.flashObject.updateFrags(len(deadEnemies), len(deadAllies))

    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        pass