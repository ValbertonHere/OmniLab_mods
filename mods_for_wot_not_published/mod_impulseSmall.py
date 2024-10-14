from debug_utils import LOG_CURRENT_EXCEPTION

from OpenModsCore import overrideMethod
from AvatarInputHandler import DynamicCameraSettings
from AvatarInputHandler.DynamicCameras.SniperCamera import SniperCamera

@overrideMethod(SniperCamera, '__applyNoiseImpulse')
def SniperCamera__updateOscillators(base, self, noiseMagnitude):
    noiseM = noiseMagnitude - 1.5
    if noiseM < 0.0:
        noiseM = 0.0
    base(self, noiseM)

@overrideMethod(SniperCamera, 'enable')
def SniperCamera_enable(base, self, targetPos, saveZoom):
    base(self, targetPos, saveZoom)
    try:
        self._SniperCamera__movementOscillator.constraints = (0, 0, 0)
    except:
        LOG_CURRENT_EXCEPTION()

@overrideMethod(DynamicCameraSettings, 'getGunImpulse')
def DynamicCameraSettings_getGunImpulse(base, self, cal):
    """0.7"""
    return 0.7


@overrideMethod(DynamicCameraSettings, 'getSensitivityToImpulse')
def DynamicCameraSettings_getSensitivityToImpulse(base, self, data):
    """0.3"""
    return 0.3