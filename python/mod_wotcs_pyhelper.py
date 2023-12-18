import SoundGroups
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AmmoPlugin

def onGunReloadTimeSet(self, _, state, skipAutoLoader):
    h_onGunReloadTimeSet(self, _, state, skipAutoLoader)
    isAutoReload = self._AmmoPlugin__guiSettings.hasAutoReload
    isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
    timeLast = state.getActualValue()
    timeLeft = state.getTimeLeft()
    if timeLeft == 0.0 and not isAutoReload and not isInPostmortem and (timeLast != -1):
        SoundGroups.g_instance.playSound2D('reloaded_old')

def onGunAutoReloadTimeSet(self, state, stunned):
    h_onGunAutoReloadTimeSet(self, state, stunned)
    isAutoReload = self._AmmoPlugin__guiSettings.hasAutoReload
    isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
    timeLast = state.getActualValue()
    timeLeft = state.getTimeLeft()
    if timeLeft == 0.0 and not isAutoReload and not isInPostmortem and (timeLast != -1):
        SoundGroups.g_instance.playSound2D('reloaded_old')

h_onGunReloadTimeSet = AmmoPlugin._AmmoPlugin__onGunReloadTimeSet
AmmoPlugin._AmmoPlugin__onGunReloadTimeSet = onGunReloadTimeSet

h_onGunAutoReloadTimeSet = AmmoPlugin._AmmoPlugin__onGunAutoReloadTimeSet
AmmoPlugin._AmmoPlugin__onGunAutoReloadTimeSet = onGunAutoReloadTimeSet

print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'
print 'WoT Classics Mod - OLD GOOD SOUNDS. Python Helper executed!'
print 'Copyright (C) 2023 OmniLab R&D.'
print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'