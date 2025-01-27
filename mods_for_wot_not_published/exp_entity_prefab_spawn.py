from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
import CGF
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from frameworks.wulf import WindowLayer
from cgf_components.hover_component import SelectionComponent
#from gui.mods.mod_nearyouhangarextras import g_nearYouHangarExtras

from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE



#niggerID = BigWorld.createEntity('ClientSelectableCameraObject', BigWorld.player().hangarSpace.spaceID, 0, (-180, 0, 6), (0, 0, 0), {'modelName': '', 'clickSoundName': 'play'})
#CGF.loadGameObject('content/OmniPrefabs/OmniCameraCopy.prefab', BigWorld.player().hangarSpace.spaceID, (-180, 0, 6))

#CGF.loadGameObjectIntoHierarchy('content/OmniPrefabs/OmniCameraCopy.prefab', BigWorld.entities[niggerID].entityGameObject, (0, 0, 0))

ClientSelectableCameraObject.switchCamera(BigWorld.entities[niggerID], 'OmniPrefabCamera')

#for i in BigWorld.entities.values():
#    if isinstance(i, ClientSelectableCameraObject):
#        print i
        
#for go in CGF.listAllActiveGameObjects(BigWorld.player().hangarSpace.spaceID):
#    print go.name

def hideGUI():
    g_eventBus.handleEvent(events.GameEvent(events.GameEvent.HIDE_LOBBY_SUB_CONTAINER_ITEMS), scope=EVENT_BUS_SCOPE.GLOBAL)

def showGUI():
    g_eventBus.handleEvent(events.GameEvent(events.GameEvent.REVEAL_LOBBY_SUB_CONTAINER_ITEMS), scope=EVENT_BUS_SCOPE.GLOBAL)

#ClientSelectableCameraObject.onMouseClick = base
#base = ClientSelectableCameraObject.onMouseClick
#ClientSelectableCameraObject.onMouseClick = onClick