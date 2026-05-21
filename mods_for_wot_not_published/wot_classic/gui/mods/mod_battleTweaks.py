# Старый эффект попадания и отключение интерполяции камеры.

import BigWorld, ResMgr, Math
from helpers.EffectsList import _FlashBangEffectDesc
from VehicleEffects import DamageFromShotDecoder
from Vehicle import Vehicle
from constants import VEHICLE_HIT_EFFECT
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera

class LegacyFlashBangEffect(_FlashBangEffectDesc):

    def __init__(self, dataSection=ResMgr.openSection('scripts/item_defs/vehicles/common/shot_effects.xml/autoArmorPiercing/armorHit/effects/flashBang')):
        super(LegacyFlashBangEffect, self).__init__(dataSection)
        self.__fba = None
        self.__clbackId = None
        self._keyframes = {'armorHit': [(0.0, Math.Vector4Provider((0, 0, 0, 0))), (0.1, Math.Vector4Provider((1, 0, 0, 0.5))), (1.1, Math.Vector4Provider((0, 0, 0, 0)))],
                           'armorCriticalHit': [(0.0, Math.Vector4Provider((0, 0, 0, 0))), (0.1, Math.Vector4Provider((1, 0, 0, 0.7))), (1.4, Math.Vector4Provider((0, 0, 0, 0)))]}
    
    def create(self, model=None, list=None, args=None, effectCode=None):
        if effectCode in (VEHICLE_HIT_EFFECT.ARMOR_PIERCED, VEHICLE_HIT_EFFECT.CRITICAL_HIT, VEHICLE_HIT_EFFECT.ARMOR_PIERCED_DEVICE_DAMAGED):
            if self.__fba is not None:
                self.__removeMe()
                BigWorld.cancelCallback(self.__clbackId)
                self.__clbackId = None
            self.__fba = Math.Vector4Animation()
            self.__fba.keyframes = self._keyframes[DamageFromShotDecoder._HIT_EFFECT_CODE_TO_EFFECT_GROUP[effectCode]]
            for effStage in self._keyframes[DamageFromShotDecoder._HIT_EFFECT_CODE_TO_EFFECT_GROUP[effectCode]]:
                self._duration += effStage[0]
            self.__fba.duration = self._duration
            self.renderSettings.flashBangAnimation(self.__fba)
            self.__clbackId = BigWorld.callback(self._duration - 0.05, self.__removeMe)

    def __removeMe(self):
        if self.__fba is not None:
            self.renderSettings.removeFlashBangAnimation(self.__fba)
            self.__fba = None
            self._duration = 0.0
        return

def onOwnVehicleDamaged(self, attackerID, points, effectsIndex, damageFactor, lastMaterialIsShield): # Разработчик, который подумал, что добавлять в одной обнове и удалять в следующей один аргумент, https://youtu.be/BL3_cLKxLOI?si=svKE6AaguHpLDPxS
    base(self, attackerID, points, effectsIndex, damageFactor, lastMaterialIsShield)
    if self.id == BigWorld.player().playerVehicleID:
        maxComponentIdx = self.calcMaxComponentIdx()
        decodedPoints = DamageFromShotDecoder.decodeHitPoints(points, self.appearance.collisions, maxComponentIdx, self.typeDescriptor)
        g_legacyFlashBangEffect.create(effectCode=decodedPoints[(-1)].hitEffectCode)

def AC_advCollider(self, onChangeControlMode=None, postmortemMode=False, smartPointCalculator=True):
    self._ArcadeCamera__adCfg['enable'] = False
    base2(self, onChangeControlMode, postmortemMode, smartPointCalculator)
    self.setCameraDistance(self._baseCfg['optimalStartDist'] - 5)

g_legacyFlashBangEffect = LegacyFlashBangEffect()

base = Vehicle.showDamageFromShot
Vehicle.showDamageFromShot = onOwnVehicleDamaged

base2 = ArcadeCamera.create
ArcadeCamera.create = AC_advCollider
