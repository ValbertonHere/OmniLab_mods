import logging
import os
import struct

import BigWorld, CGF, LGC, Math, ResMgr

from CurrentVehicle import g_currentVehicle
from cgf_components.hangar_camera_manager import HangarCameraManager
from collections import namedtuple

from gui import g_tankActiveCamouflage
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
from gui.impl.common.fade_manager import useDefaultFade
from frameworks.wulf import WindowLayer

from .._constants import TEMPLATE_FOLDER, TEMPLATE_FILES
from ..config import g_oucConfig
from ..cache import g_oucCache
from ..utils import vfs2realfs, getDevModeState


import CGF
from cgf_components import serial_number_component
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from GenericComponents import TransformComponent, DynamicModelComponent
from cgf_components.hangar_camera_manager import HangarCameraManager
import Math, ResMgr
from AvatarInputHandler.cameras import FovExtended
import BigWorld, Keys, ResMgr
from gui import InputHandler
from gui.shared.utils.key_mapping import getBigworldNameFromKey
import SoundGroups

from .userCustomizationWindow import UserCustomizationWindow

logger = logging.getLogger(__name__)

CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'itemIntCD', 'uid'))

class UserCustomizationSerialNumberViewMeta(View):
    def as_showHintS(self, type, msg):
        if self._isDAAPIInited():
            self.flashObject.as_showHint(type, msg)

    def as_resetSizeS(self, appWidth, appHeight):
        if self._isDAAPIInited():
            self.flashObject.as_resetSize(appWidth, appHeight)

class UserCustomizationSerialNumberView(UserCustomizationSerialNumberViewMeta):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(UserCustomizationSerialNumberView, self).__init__()
        self.vEntity = None
        self.serialNumberComponent = None
        self.serialNumber = ''

    @property
    def mainWindow(self):
        return UserCustomizationWindow.mainWindow

    def _populate(self):
        super(UserCustomizationSerialNumberView, self)._populate()
        self.vEntity = self.hangarSpace.getVehicleEntity()
        self.__initAndLocateCameraToUCSNView()
        self.addListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResized, scope=EVENT_BUS_SCOPE.GLOBAL)
        InputHandler.g_instance.onKeyDown += self.onKeyDown
    
    def _dispose(self):
        InputHandler.g_instance.onKeyDown -= self.onKeyDown
        self.removeListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResized, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__removeAndResetCamera()
        super(UserCustomizationSerialNumberView, self)._dispose()

    def py_playSound(self, eventName):
        SoundGroups.g_instance.playSound2D(eventName)

    def py_reloadModel(self):
        g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
        BigWorld.callback(0.2, lambda: g_currentVehicle.refreshModel(self.view.outfit)) # https://youtu.be/LZNw8t1k1rI?si=RKiYaxToafDS5Wap&t=27
    
    @useDefaultFade(layer=WindowLayer.OVERLAY, fadeInDuration=.5, fadeOutDuration=.5)
    def py_exitWithoutSave(self):
        g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
        g_currentVehicle.refreshModel(self.mainWindow.view.outfit)
        self.destroy()
    
    def py_setSerialNumber(self, number):
        self.serialNumber = number
        for i in xrange(0, 5):
            try:
                stringChar = self.serialNumber[i]
            except IndexError:
                stringChar = ''
            
            self.serialNumberComponent.decalComponent().setCounterStickerValue(i, stringChar)

    @useDefaultFade(layer=WindowLayer.OVERLAY, fadeInDuration=.5, fadeOutDuration=.5)
    def __applySerialNumber(self):
        self.mainWindow.setOutfitSerialNumber(self.serialNumber)
        self.destroy()

    def __onAppResized(self, event):
        self.as_resetSizeS(event.ctx['width']/event.ctx['scale'], event.ctx['height']/event.ctx['scale'])
    
    def __initAndLocateCameraToUCSNView(self):
        self.mainWindow.as_setVisibleS(False)
        cameraManager = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
        hierManager = CGF.HierarchyManager(self.hangarSpace.spaceID)

        if not cameraManager or not hierManager:
            return False
        
        serialNumberGOs = CGF.Query(self.hangarSpace.spaceID, (CGF.GameObject, serial_number_component.SerialNumberComponent))
        for go, serialNumberComponent in serialNumberGOs:
            dynamicModel = go.findComponentByType(DynamicModelComponent)
            if dynamicModel is not None and dynamicModel.getModelName() != '':
                numberModelPath = dynamicModel.getModelName()
                self.serialNumberComponent = serialNumberComponent
                serialNumberGO = go
                break

        serialNumberVisualSection = ResMgr.openSection(numberModelPath.replace('.model', '.visual_processed') + '/renderSet/geometry/primitiveGroup')
        serialNumberLocalPos = serialNumberVisualSection.readVector3('groupOrigin')

        serialNumberTransform = serialNumberGO.findComponentByType(TransformComponent)
        serialNumberWorldMatrix = serialNumberTransform.worldTransform
        serialNumberWorldMatrix.setTranslate(serialNumberWorldMatrix.applyPoint(serialNumberLocalPos))

        if g_currentVehicle.item.name == 'germany:G178_Sturmtiger_V1':
            matrix = Math.Matrix(self.vEntity.matrix)
            pos = serialNumberWorldMatrix.translation
            yaw = matrix.yaw
            pitch = serialNumberWorldMatrix.pitch -0.2
        else:
            pos = serialNumberWorldMatrix.translation
            yaw = serialNumberTransform.worldTransform.yaw
            pitch = serialNumberTransform.worldTransform.pitch

        cameraManager.switchByCameraName('Customization', True, False)
        FovExtended.instance().setFovByMultiplier(0.4)
        cameraManager.moveCamera(pos, yaw, pitch, 0, 0)
        return

    def __removeAndResetCamera(self):
        self.mainWindow.as_setVisibleS(True)
        try:
            cameraManager = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
            if not cameraManager:
                return
            cameraManager.switchByCameraName('UserCustomizationCamera', True, False)
        except:
            logger.exception('Failed to reset camera, maybe it not exist anymore.')

    def onKeyDown(self, event):
        key = getBigworldNameFromKey(event.key)
        if key == 'KEY_ESCAPE':
            self.py_exitWithoutSave()
        elif key == 'KEY_RETURN':
            self.__applySerialNumber()
