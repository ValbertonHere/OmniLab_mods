import logging

import BigWorld, CGF, Math, ResMgr

from AvatarInputHandler.cameras import FovExtended

from CurrentVehicle import g_currentVehicle
from cgf_components import serial_number_component
from cgf_components.hangar_camera_manager import HangarCameraManager
from collections import namedtuple

from GenericComponents import TransformComponent, DynamicModelComponent
from gui import InputHandler
from gui.Scaleform.framework.entities.View import View
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.utils.key_mapping import getBigworldNameFromKey

from helpers import dependency

from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared.utils import IHangarSpace

from gui.impl.common.fade_manager import useDefaultFade
from frameworks.wulf import WindowLayer

from .userCustomizationWindow import UserCustomizationWindow
from ..cache import g_ucCache
from ..utils import playSound

logger = logging.getLogger(__name__)

CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'itemIntCD', 'uid'))

class UserCustomizationSerialNumberViewMeta(View):
    def as_setForbiddenNumbersS(self, array):
        if self._isDAAPIInited():
            self.flashObject.as_setForbiddenNumbers(array)

    def as_showHintS(self, type, msg):
        if self._isDAAPIInited():
            self.flashObject.as_showHint(type, msg)

    def as_resetSizeS(self, appWidth, appHeight):
        if self._isDAAPIInited():
            self.flashObject.as_resetSize(appWidth, appHeight)

class UserCustomizationSerialNumberView(UserCustomizationSerialNumberViewMeta):
    hangarSpace = dependency.descriptor(IHangarSpace)
    c11nService = dependency.descriptor(ICustomizationService)

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
        self.as_setForbiddenNumbersS(g_ucCache.forbiddenContent['numbers'])
        self.vEntity = self.hangarSpace.getVehicleEntity()
        self.__initAndLocateCameraToUCSNView()
        self.addListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResized, scope=EVENT_BUS_SCOPE.GLOBAL)
        InputHandler.g_instance.onKeyDown += self.onKeyDown
    
    def _dispose(self):
        InputHandler.g_instance.onKeyDown -= self.onKeyDown
        self.removeListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResized, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__removeAndResetCamera()
        super(UserCustomizationSerialNumberView, self)._dispose()

    def py_playSound(self, *args):
        playSound(*args)

    def py_reloadModel(self):
        g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
        BigWorld.callback(0.2, lambda: g_currentVehicle.refreshModel(self.view.outfit)) # https://youtu.be/LZNw8t1k1rI?si=RKiYaxToafDS5Wap&t=27
    
    def exitView(self):
        g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
        g_currentVehicle.refreshModel(self.mainWindow.view.outfit)
        self.destroy()
    
    @useDefaultFade(layer=WindowLayer.OVERLAY, fadeInDuration=.5, fadeOutDuration=.5)
    def py_exitWithoutSave(self):
        self.exitView()
    
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
        numberLength = len(self.serialNumber)

        if numberLength == 0:
            self.exitView()
            return
        elif numberLength < 3:
            self.serialNumber = '0'*(3-numberLength) + self.serialNumber

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

        # Штурмпидр из-за своего короткого, но мощного пиструна не имеет на нём номера, а второе табло, из-за чего матрица путается.
        # Поэтому камера крепится к верхушке кармы, а не прям на табло.
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
            self.py_playSound('cust_choise_esc')
            self.py_exitWithoutSave()
        elif key == 'KEY_RETURN':
            self.py_playSound('cust_select_double', 'radial_big_close')
            self.__applySerialNumber()
