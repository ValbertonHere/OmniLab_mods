import logging
import os
import struct

import BigWorld, CGF, LGC, Math, ResMgr

from CurrentVehicle import g_currentVehicle
from cgf_components.hangar_camera_manager import HangarCameraManager

from gui.customization.shared import C11nId
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationSlotUpdateVO
from gui.Scaleform.framework.entities.View import View
from gui.shared import EVENT_BUS_SCOPE, events

from helpers import dependency

from items.components.c11n_constants import SLOT_DEFAULT_ALLOWED_MODEL

from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IOverlayController
from skeletons.gui.shared.utils import IHangarSpace

from vehicle_outfit.outfit import Area
from vehicle_systems.tankStructure import TankPartNames

from .._constants import TEMPLATE_FOLDER, TEMPLATE_FILES
from ..config import g_oucConfig
from ..cache import g_oucCache
from ..utils import vfs2realfs

logger = logging.getLogger(__name__)

class UserCustomizationWindowMeta(View):
    def as_resetSizeS(self, appWidth, appHeight):
        if self._isDAAPIInited():
            self.flashObject.as_resetSize(appWidth, appHeight)

    def as_setDevBtnVisibleS(self, isVisible):
        if self._isDAAPIInited():
            self.flashObject.as_setDevBtnVisible(isVisible)

class UserCustomizationWindow(UserCustomizationWindowMeta):
    c11nService = dependency.descriptor(ICustomizationService)
    hangarSpace = dependency.descriptor(IHangarSpace)
    overlayController = dependency.descriptor(IOverlayController)

    def __init__(self):
        super(UserCustomizationWindow, self).__init__()
        self.vEntity = None
        self.cameraGameObject = None

    @property
    def view(self):
        return self.getComponent('UserCustomizationViewUI')

    def _populate(self):
        super(UserCustomizationWindow, self)._populate()
        self.vEntity = self.hangarSpace.getVehicleEntity()
        self.__initAndLocateCameraToUCView()
        self.as_setDevBtnVisibleS(g_oucConfig.getDevModeState())
        self.addListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResized, scope=EVENT_BUS_SCOPE.GLOBAL)
    
    def _dispose(self):
        self.removeListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResized, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__removeAndResetCamera()
        super(UserCustomizationWindow, self)._dispose()

    def py_reloadModel(self):
        g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
        BigWorld.callback(0.2, lambda: g_currentVehicle.refreshModel(self.view.outfit)) # https://youtu.be/LZNw8t1k1rI?si=RKiYaxToafDS5Wap&t=27

    def py_createOutfitTemplate(self):
        res_mods_folder = ResMgr.openSection('../paths.xml')['Paths'].values()[0].asString
        
        for file in TEMPLATE_FILES:
            vfs2realfs(TEMPLATE_FOLDER + file, res_mods_folder + '/valberton/user_customization/' + file)

        BigWorld.savePreferences()
        LGC.notifyRestart()
        BigWorld.worldDrawEnabled(False)
        BigWorld.restartGame()
        
    def py_reloadCache(self):
        self.destroy()
        g_oucCache.doReloadCache()
    
    def py_saveOutfitAndExit(self):
        if self.view.outfit:
            g_oucConfig.saveVehicleOutfit(self.view.vehicle.name, self.view.outfit)
        self.destroy()
    
    def py_exitWithoutSave(self):
        g_currentVehicle.refreshModel()
        self.destroy()

    def py_moveSpace(self, dx, dy, dz):
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx, 'dy': dy, 'dz': dz}))
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx, 'dy': dy, 'dz': dz}))

    def py_notifyCursorOver3dScene(self, isOver3dScene):
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver3dScene}))

    def py_notifyCursorDragging(self, isDragging):
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, ctx={'isDragging': isDragging}))

    def __onAppResized(self, event):
        self.as_resetSizeS(event.ctx['width']/event.ctx['scale'], event.ctx['height']/event.ctx['scale'])

    def _getAnchorVOs(self, slotType):
        anchorVOs = []
        if g_currentVehicle.isPresent():
            for areaId in Area.ALL:
                slot = self.view.outfit.getContainer(areaId).slotFor(slotType)
                for regionIdx, anchor in g_currentVehicle.item.getAnchors(slotType, areaId):
                    model = self.view.outfit.modelsSet or SLOT_DEFAULT_ALLOWED_MODEL
                    if model not in anchor.compatibleModels:
                        continue
                    slotId = C11nId(areaId, self.slotType, regionIdx)
                    intCD = slot.getItemCD(regionIdx)
                    uid = self.__customizationSlotIdToUid(slotId)
                    anchorVO = CustomizationSlotUpdateVO(slotId=slotId._asdict(), itemIntCD=intCD, uid=uid)
                    anchorVOs.append(anchorVO._asdict())

        return anchorVOs
    
    def __customizationSlotIdToUid(self, slotId):
        s = struct.pack('bbh', slotId.areaId, slotId.slotType, slotId.regionIdx)
        uid = struct.unpack('I', s)[0]
        return uid
    
    def __initAndLocateCameraToUCView(self):
        cameraManager = None

        def onCameraInit(go):
            self.cameraGameObject = go
            BigWorld.callback(0.1, lambda: cameraManager.switchByCameraName('UserCustomizationCamera', False, False))

        cameraManager = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
        if not cameraManager:
            return False
        else:
            if self.vEntity is None or self.vEntity.appearance is None or self.vEntity.appearance.compoundModel is None:
                return
            self.overlayController.setOverlayState(True)
            appearance = self.vEntity.appearance
            # position = appearance.getVehicleCentralPoint()
            m = Math.Matrix(appearance.compoundModel.node(TankPartNames.HULL))
            # targetPos = m.applyPoint(position)
            targetPos = m.translation
            CGF.loadGameObject('content/HangarPrefabs/UserCustomizationCamera.prefab', self.hangarSpace.spaceID, targetPos, onCameraInit)
            return

    def __removeAndResetCamera(self):
        CGF.removeGameObject(self.cameraGameObject)
        self.cameraGameObject = None
        self.overlayController.setOverlayState(False)

        try:
            cameraManager = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
            if not cameraManager:
                return
            cameraManager.switchToTank(False, False)
        except:
            logger.exception('Failed to reset camera, maybe it not exist anymore.')