# Попытка в тундровскую камеру.

import BigWorld
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import MinMax

def c(self, onChangeControlMode=None, postmortemMode=False, smartPointCalculator=True):
    base(self, onChangeControlMode, postmortemMode, smartPointCalculator)
    self._cfg['startDist'] = 12.5
    self._cfg['startAngle'] = -0.2
    self._ArcadeCamera__defaultAimOffset = (0, 0.325)
    self._cfg['distRange'] = MinMax(min=2.0, max=12.5)
    self._cfg['heightAboveBase'] = BigWorld.player().vehicle.typeDescriptor.turret.hitTester.bbox[1][2] + 0.5
    self.setPivotSettings(BigWorld.player().vehicle.typeDescriptor.turret.hitTester.bbox[1][2] + 0.5, self._cfg['focusRadius'])

def u(self, newDist):
    print newDist
    if newDist < 5.0:
        self._cfg['heightAboveBase'] = BigWorld.player().vehicle.typeDescriptor.turret.hitTester.bbox[1][2] + 2.5
    elif newDist < 10.0:
        self._cfg['heightAboveBase'] = BigWorld.player().vehicle.typeDescriptor.turret.hitTester.bbox[1][2] + 1.7
    else: self._cfg['heightAboveBase'] = BigWorld.player().vehicle.typeDescriptor.turret.hitTester.bbox[1][2] + 0.5
    base2(self, newDist)

try:
    ArcadeCamera.create = base
    ArcadeCamera._updateCameraSettings = base2
except:
    'base not found'
    
base = ArcadeCamera.create
base2 = ArcadeCamera._updateCameraSettings

ArcadeCamera.create = c
ArcadeCamera._updateCameraSettings = u
    
