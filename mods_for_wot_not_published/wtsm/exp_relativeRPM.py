import BigWorld
from Avatar import PlayerAvatar
from time import sleep
from WWISE import WW_setRTCPGlobal
from PlayerEvents import g_playerEvents
from threading import Thread

def nig():
    while isinstance(BigWorld.player(), PlayerAvatar):
        relativeRPM = BigWorld.player().vehicle.appearance.detailedEngineState.relativeRPM
        WW_setRTCPGlobal('RTPC_ext_wtsm_rpm_rel', relativeRPM)
        sleep(0.3)
    return

def start_thread():
    thread = Thread(target=nig)
    thread.start()

g_playerEvents.onAvatarReady += start_thread