from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
import CGF, GUI
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from frameworks.wulf import WindowLayer
from cgf_components.hover_component import SelectionComponent
from AvatarInputHandler import cameras
from constants import CollisionFlags
from vehicle_systems.tankStructure import ColliderTypes
from Math import Matrix
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE

scale = 0.18

def callback(go):
    print go

#print BigWorld.camera().position
#entityID = BigWorld.createEntity('ClientSelectableCameraObject', BigWorld.player().hangarSpace.spaceID, 0, (-180, 0, 6), (0, 0, 0), {'modelName': '', 'clickSoundName': 'play'})
CGF.loadGameObject('content/OmniPrefabs/OmniCamera.prefab', BigWorld.player().hangarSpace.spaceID, (-0.348, 2, 0.06), callback)

#null = (-3.983, 1, 4.341)

#print BigWorld.camera().position

for go in CGF.listAllActiveGameObjects(BigWorld.player().hangarSpace.spaceID):
    if go.name == 'Model':
        go.getComponents()[1].position = (-0.348, 2, 0.06)

#model = BigWorld.Model('content/Hangars/nyh_res/tv.model')
#model.position = BigWorld.player().hangarSpace.getVehicleEntity().position + (2, 1, 0)
#BigWorld.addModel(model)
#print Matrix(model.matrix)