import logging
import struct
from copy import deepcopy

import BigWorld, CGF, LGC, Math, ResMgr

from CurrentVehicle import g_currentVehicle
from cgf_components.hangar_camera_manager import HangarCameraManager
from collections import namedtuple

from gui.customization.shared import C11nId
from gui.impl.common.fade_manager import useDefaultFade
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.Scaleform.framework.entities.View import View
from gui.shared import EVENT_BUS_SCOPE, events

from helpers import dependency

from items.components.c11n_constants import SLOT_DEFAULT_ALLOWED_MODEL

from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IOverlayController
from skeletons.gui.shared.utils import IHangarSpace
from frameworks.wulf import WindowLayer

from vehicle_outfit.outfit import Area
from vehicle_systems.tankStructure import TankPartNames

from .._constants import TEMPLATE_FOLDER, TEMPLATE_FILES
from ..config import g_ucConfig
from ..cache import g_ucCache
from ..utils import vfs2realfs, getDevModeState, loadUCSerialNumberView, playSound

logger = logging.getLogger(__name__)

CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'itemIntCD', 'uid'))

class UserCustomizationWindowMeta(View):
    def as_setVisibleS(self, isVisible):
        if self._isDAAPIInited():
            self.flashObject.as_setVisible(isVisible)

    def as_setBigButtonVisibillityS(self, buttonName, isVisible):
        if self._isDAAPIInited():
            self.flashObject.as_setBigButtonVisibillity(buttonName, isVisible)

    def as_resetSizeS(self, appWidth, appHeight):
        if self._isDAAPIInited():
            self.flashObject.as_resetSize(appWidth, appHeight)

    def as_setDevBtnVisibleS(self, isVisible):
        if self._isDAAPIInited():
            self.flashObject.as_setDevBtnVisible(isVisible)
            
    def as_setSeasonBarEnabledS(self, isEnabled):
        if self._isDAAPIInited():
            self.flashObject.as_setSeasonBarEnabled(isEnabled)

    def as_setSeasonBarSelectS(self, value):
        if value not in (1, 2, 4):
            value = 2 # SUMMER
            
        if self._isDAAPIInited():
            self.flashObject.as_setSeasonBarSelect(str(value))
    
    def as_setRemOutfitBtnEnabledS(self, isEnabled):
        if self._isDAAPIInited():
            self.flashObject.as_setRemOutfitBtnEnabled(isEnabled)
    
    def as_setSwitchOutfitBtnS(self, isEnabled, isSelected):
        if self._isDAAPIInited():
            self.flashObject.as_setSwitchOutfitBtn(isEnabled, isSelected)

class UserCustomizationWindow(UserCustomizationWindowMeta):
    mainWindow = None
    c11nService = dependency.descriptor(ICustomizationService)
    hangarSpace = dependency.descriptor(IHangarSpace)
    overlayController = dependency.descriptor(IOverlayController)

    def __init__(self):
        super(UserCustomizationWindow, self).__init__()
        self.vEntity = None
        self.cameraGameObject = None
        UserCustomizationWindow.mainWindow = self

    @property
    def view(self):
        return self.getComponent('UserCustomizationViewUI')

    def _populate(self):
        super(UserCustomizationWindow, self)._populate()
        isOutfitInConfig = g_ucConfig.isOutfitInConfig(self.view.vehicle.name)

        self.vEntity = self.hangarSpace.getVehicleEntity()
        self.__initAndLocateCameraToUCView()
        self.as_setSeasonBarSelectS(self.view.getVehicleActiveSeason())
        self.as_setDevBtnVisibleS(getDevModeState())
        self.as_setRemOutfitBtnEnabledS(isOutfitInConfig)
        self.as_setSwitchOutfitBtnS(isOutfitInConfig, isOutfitInConfig)
        self.addListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResized, scope=EVENT_BUS_SCOPE.GLOBAL)
        playSound('ue_hangar_generic_camera_fly_forward')
    
    def _dispose(self):
        playSound('ue_hangar_generic_camera_fly_backward')
        self.removeListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onAppResized, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__removeAndResetCamera()
        UserCustomizationWindow.mainWindow = None
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
        BigWorld.callback(0.0, g_ucCache.reloadCache())
    
    def py_saveOutfitAndExit(self):
        if self.view.outfit:
            g_ucConfig.saveVehicleOutfit(self.view.vehicle.name, self.view.outfit)
        self.destroy()
    
    def py_switchTankOutfit(self, isUserCustomVisible):
        self.as_setSeasonBarEnabledS(not self.view.checkVehicleOutfitForAllSeasons(True, isUserCustomVisible))
        g_currentVehicle.refreshModel(self.view.outfit if isUserCustomVisible else g_currentVehicle.item.outfits[self.view.getVehicleActiveSeason()])

    def py_removeOutfitFromConfig(self):
        g_ucConfig.removeOutfitFromConfig(self.view.vehicle.name)
        g_currentVehicle.refreshModel()
        self.destroy()
    
    def py_exitWithoutSave(self):
        g_currentVehicle.refreshModel()
        self.destroy()

    def py_playSound(self, *args):
        playSound(*args)
    
    def py_goToSerialNumberView(self):
        # Сделаем так, чтобы отображались 5 пустых ячеек номера.
        self.as_setSeasonBarSelectS(self.view.getVehicleActiveSeason())
        outfit = deepcopy(self.view.outfit)
        outfit.setSerialNumber('     ')
        g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
        g_currentVehicle.refreshModel(outfit)
        playSound('cust_choice_enter', 'ue_hangar_generic_camera_fly_forward')

        self.goToSerialNumberView()

    @useDefaultFade(layer=WindowLayer.OVERLAY, fadeInDuration=.5, fadeOutDuration=.5)
    def goToSerialNumberView(self):
        loadUCSerialNumberView()

    def py_moveSpace(self, dx, dy, dz):
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx, 'dy': dy, 'dz': dz}))
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx, 'dy': dy, 'dz': dz}))

    def py_notifyCursorOver3dScene(self, isOver3dScene):
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver3dScene}))

    def py_notifyCursorDragging(self, isDragging):
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, ctx={'isDragging': isDragging}))

    def setOutfitSerialNumber(self, number):
        self.as_setSwitchOutfitBtnS(True, True)
        self.view.outfit.setSerialNumber(number)
        g_currentVehicle.refreshModel(self.view.outfit)

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
            m = Math.Matrix(appearance.compoundModel.node(TankPartNames.HULL))
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