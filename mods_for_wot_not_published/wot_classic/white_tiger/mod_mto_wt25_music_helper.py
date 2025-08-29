import SoundGroups
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.drone_music_player import WhiteTigerDroneMusicPlayer
from constants import ARENA_PERIOD

def hook_setPeriod(self, period):
    base(self, period)
    if period != ARENA_PERIOD.AFTERBATTLE:
        SoundGroups.g_instance.setSwitch('SWITCH_mto_battle_state', 'SWITCH_mto_battle_state_battle')
    else:
        SoundGroups.g_instance.setSwitch('SWITCH_mto_battle_state', 'SWITCH_mto_battle_state_afterbattle')

base = WhiteTigerDroneMusicPlayer.setPeriod
WhiteTigerDroneMusicPlayer.setPeriod = hook_setPeriod