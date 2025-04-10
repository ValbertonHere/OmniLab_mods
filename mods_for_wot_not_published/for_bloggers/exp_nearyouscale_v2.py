# Костыль для scale'a модели танка для прототипа ангара Near_You Team. Ныне не используется ввиду уменьшения геометрии.

import Math, math_utils, BigWorld
from gui.ClientHangarSpace import hangarCFG
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.hangar_vehicle_appearance import HangarVehicleAppearance, _CAMERA_CAPSULE_GUN_SCALE, _CAMERA_CAPSULE_SCALE
from vehicle_systems import camouflages
from vehicle_systems.stricted_loading import makeCallbackWeak
from vehicle_systems.tankStructure import ModelsSetParams, TankPartNames, ColliderTypes

def HangarVehicleAppearance__setupModel(self, buildIdx):
    self._HangarVehicleAppearance__assembleModel()
    matrix = math_utils.createSRTMatrix(Math.Vector3(1.4, 1.4, 1.4), Math.Vector3(self._HangarVehicleAppearance__vEntity.yaw, self._HangarVehicleAppearance__vEntity.pitch, self._HangarVehicleAppearance__vEntity.roll), self._HangarVehicleAppearance__vEntity.position)
    self._HangarVehicleAppearance__vEntity.model.matrix = matrix
    self._HangarVehicleAppearance__vEntity.typeDescriptor = self._HangarVehicleAppearance__vDesc
    typeDescr = self._HangarVehicleAppearance__vDesc
    wheelConfig = typeDescr.chassis.generalWheelsAnimatorConfig
    if self.wheelsAnimator is not None and wheelConfig is not None:
        self.wheelsAnimator.createCollision(wheelConfig, self.collisions)
    gunColBox = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.GUN) + 3)
    center = 0.5 * (gunColBox[1] - gunColBox[0])
    gunoffset = Math.Matrix()
    gunoffset.setTranslate((0.0, 0.0, center.z + gunColBox[0].z))
    gunNode = self._HangarVehicleAppearance__getGunNode()
    gunLink = math_utils.MatrixProviders.product(gunoffset, gunNode)
    collisionData = ((TankPartNames.getIdx(TankPartNames.CHASSIS), self._HangarVehicleAppearance__vEntity.model.matrix),
                     (TankPartNames.getIdx(TankPartNames.HULL), self._HangarVehicleAppearance__vEntity.model.node(TankPartNames.HULL)),
                     (TankPartNames.getIdx(TankPartNames.TURRET), self._HangarVehicleAppearance__vEntity.model.node(TankPartNames.TURRET)),
                     (TankPartNames.getIdx(TankPartNames.GUN), gunNode))
    self.collisions.connect(self._HangarVehicleAppearance__vEntity.id, ColliderTypes.VEHICLE_COLLIDER, collisionData)
    collisionData = ((TankPartNames.getIdx(TankPartNames.GUN) + 1,
                      self._HangarVehicleAppearance__vEntity.model.node(TankPartNames.HULL)),
                     (TankPartNames.getIdx(TankPartNames.GUN) + 2,
                      self._HangarVehicleAppearance__vEntity.model.node(TankPartNames.TURRET)),
                     (TankPartNames.getIdx(TankPartNames.GUN) + 3, gunLink))
    self.collisions.connect(self._HangarVehicleAppearance__vEntity.id, self._getColliderType(), collisionData)
    self._reloadColliderType(self._HangarVehicleAppearance__vEntity.state)
    self._HangarVehicleAppearance__reloadShadowManagerTarget(self._HangarVehicleAppearance__vEntity.state)
    return

def HangarVehicleAppearance__startBuild(self, vDesc, vState):
    
    self._HangarVehicleAppearance__curBuildInd += 1
    self._HangarVehicleAppearance__vState = vState
    self._HangarVehicleAppearance__resources = {}
    self._HangarVehicleAppearance__vehicleStickers = None
    cfg = hangarCFG()
    if vState == 'undamaged':
        self._HangarVehicleAppearance__currentEmblemsAlpha = cfg['emblems_alpha_undamaged']
        self._HangarVehicleAppearance__isVehicleDestroyed = False
    else:
        self._HangarVehicleAppearance__currentEmblemsAlpha = cfg['emblems_alpha_damaged']
        self._HangarVehicleAppearance__isVehicleDestroyed = True
    self._HangarVehicleAppearance__vDesc = vDesc
    resources = camouflages.getCamoPrereqs(self._HangarVehicleAppearance__outfit, vDesc)
    if not self._HangarVehicleAppearance__isVehicleDestroyed:
        self._HangarVehicleAppearance__attachments = camouflages.getAttachments(self._HangarVehicleAppearance__outfit, vDesc)
    modelsSet = self._HangarVehicleAppearance__outfit.modelsSet
    splineDesc = vDesc.chassis.splineDesc
    if splineDesc is not None:
        for _, trackDesc in splineDesc.trackPairs.iteritems():
            resources += trackDesc.prerequisites(modelsSet)

    from vehicle_systems import model_assembler
    resources.append(model_assembler.prepareCompoundAssembler(self._HangarVehicleAppearance__vDesc, ModelsSetParams(modelsSet, self._HangarVehicleAppearance__vState, self._HangarVehicleAppearance__attachments), self._HangarVehicleAppearance__spaceId))
    g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.VEHICLE_LOADING, ctx={'started': True, 
       'vEntityId': self._HangarVehicleAppearance__vEntity.id, 
       'intCD': self._HangarVehicleAppearance__vDesc.type.compactDescr}), scope=EVENT_BUS_SCOPE.DEFAULT)
    cfg = hangarCFG()
    gunScale = cfg.get('cam_capsule_gun_scale', _CAMERA_CAPSULE_GUN_SCALE)
    capsuleScale = cfg.get('cam_capsule_scale', _CAMERA_CAPSULE_SCALE)
    hitTesterManagers = {TankPartNames.CHASSIS: vDesc.chassis.hitTesterManager, 
       TankPartNames.HULL: vDesc.hull.hitTesterManager, 
       TankPartNames.TURRET: vDesc.turret.hitTesterManager, 
       TankPartNames.GUN: vDesc.gun.hitTesterManager}
    bspModels = ()
    crashedBspModels = ()
    for partName, htManager in hitTesterManagers.iteritems():
        partId = TankPartNames.getIdx(partName)
        bspModel = (
         partId, htManager.modelHitTester.bspModelName)
        bspModels = bspModels + (bspModel,)
        if htManager.crashedModelHitTester:
            crashedBspModel = (
             partId, htManager.crashedModelHitTester.bspModelName)
            crashedBspModels = crashedBspModels + (crashedBspModel,)

    bspModels = bspModels + (
     (
      TankPartNames.getIdx(TankPartNames.GUN) + 1,
      vDesc.hull.hitTesterManager.modelHitTester.bspModelName, capsuleScale, True),
     (
      TankPartNames.getIdx(TankPartNames.GUN) + 2,
      vDesc.turret.hitTesterManager.modelHitTester.bspModelName, capsuleScale, True),
     (
      TankPartNames.getIdx(TankPartNames.GUN) + 3,
      vDesc.gun.hitTesterManager.modelHitTester.bspModelName, gunScale, True))
    if vDesc.hull.hitTesterManager.crashedModelHitTester:
        crashedBspModels = crashedBspModels + (
         (
          TankPartNames.getIdx(TankPartNames.GUN) + 1,
          vDesc.hull.hitTesterManager.crashedModelHitTester.bspModelName, capsuleScale, True),)
    if vDesc.turret.hitTesterManager.crashedModelHitTester:
        crashedBspModels = crashedBspModels + (
         (
          TankPartNames.getIdx(TankPartNames.GUN) + 2,
          vDesc.turret.hitTesterManager.crashedModelHitTester.bspModelName, capsuleScale, True),)
    if vDesc.gun.hitTesterManager.crashedModelHitTester:
        crashedBspModels = crashedBspModels + (
         (
          TankPartNames.getIdx(TankPartNames.GUN) + 3,
          vDesc.gun.hitTesterManager.crashedModelHitTester.bspModelName, gunScale, True),)
    modelCA = BigWorld.CollisionAssembler(bspModels, self._HangarVehicleAppearance__spaceId)
    modelCA.name = 'ModelCollisions'
    resources.append(modelCA)
    if crashedBspModels:
        crashedModelCA = BigWorld.CollisionAssembler(crashedBspModels, self._HangarVehicleAppearance__spaceId)
        crashedModelCA.name = 'CrashedModelCollisions'
        resources.append(crashedModelCA)
    physicalTracksBuilders = vDesc.chassis.physicalTracks
    for name, builders in physicalTracksBuilders.iteritems():
        for index, builder in enumerate(builders):
            resources.append(builder.createLoader(self._HangarVehicleAppearance__spaceId, ('{0}{1}PhysicalTrack').format(name, index), modelsSet))

    BigWorld.loadResourceListBG(tuple(resources), makeCallbackWeak(self._HangarVehicleAppearance__onResourcesLoaded, self._HangarVehicleAppearance__curBuildInd))
    return

base = HangarVehicleAppearance._HangarVehicleAppearance__setupModel
HangarVehicleAppearance._HangarVehicleAppearance__setupModel = HangarVehicleAppearance__setupModel

base2 = HangarVehicleAppearance._HangarVehicleAppearance__startBuild
HangarVehicleAppearance._HangarVehicleAppearance__startBuild = HangarVehicleAppearance__startBuild