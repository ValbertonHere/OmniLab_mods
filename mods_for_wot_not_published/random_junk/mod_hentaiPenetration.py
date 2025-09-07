import BigWorld, SoundGroups
from PlayerEvents import g_playerEvents

def onHealthChanged(attackedID, *args, **kwargs):
    if attackedID == BigWorld.player().playerVehicleID:
        SoundGroups.g_instance.playSound2D('hentai_sound')

def onAvatarReady():
    BigWorld.player().arena.onVehicleHealthChanged += onHealthChanged

g_playerEvents.onAvatarReady += onAvatarReady

print '[OMNILAB: HENTAI ROFL] INIT! Copyright (C) 2024 OmniLab R&D.'