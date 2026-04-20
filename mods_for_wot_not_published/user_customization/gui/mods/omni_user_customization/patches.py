import logging
import BigWorld
import items

from CurrentVehicle import g_currentVehicle

from gui import makeHtmlString
from gui.SystemMessages import SM_TYPE, pushI18nMessage
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.impl.pub.dialog_window import DialogButtons
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel import AmmunitionPanel
from gui.shared.gui_items.customization.c11n_items import Style
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import makeTooltip

from vehicle_systems.camouflages import SeasonType, _currentMapSeason
from vehicle_systems.CompoundAppearance import CompoundAppearance

from ._constants import NOTIFICATION_HEADER
from .cache import g_oucCache
from .config import g_oucConfig
from .utils import override, isInCustomization, set3DStylePrefabs, showCustomizationDialog, loadOUCWindow, checkCurrentVehicleServerOutfit

__all__ = ()
logger = logging.getLogger(__name__)

Style.isHidden = property(lambda self: True if self.id in (g_oucCache.mod_cache['styles']['2d'].values() + g_oucCache.mod_cache['styles']['3d'].values()) else self._isHidden)

# Уведомление в случае, если на танк на стороне сервера не нанесён камуфляж.
@override(AmmunitionPanel, 'as_updateVehicleStatusS')
def AmmunitionPanel_as_updateVehicleStatusS(base, self, data):
    if not data['message']:
        if not checkCurrentVehicleServerOutfit():
            data['message'] = makeHtmlString('html_templates:vehicleStatus', Vehicle.VEHICLE_STATE_LEVEL.CRITICAL, {'message': 'Нет маскировки на сервере!'})
    base(self, data)


@override(AmmunitionPanel, 'showCustomization')
def AmmunitionPanel_showCustomization(base, self):
    if not checkCurrentVehicleServerOutfit():
        base(self)
        pushI18nMessage('#userCustomization:notification/noOutfitOnServer', type=SM_TYPE.WarningHeader, messageData=NOTIFICATION_HEADER)
        return
    isCustomizationEnabled = g_currentVehicle.getViewState().isCustomizationEnabled()
    isVehicleCustomizable = g_currentVehicle.isInHangar()
    
    def onResult(result):
        if result == DialogButtons.SUBMIT or result == DialogButtons.PURCHASE:
            base(self)
        elif result == DialogButtons.RESEARCH:
            loadOUCWindow()

    if isVehicleCustomizable and not isCustomizationEnabled:
        loadOUCWindow()
    else:
        showCustomizationDialog(onResult)
    
@override(Hangar, 'as_setupAmmunitionPanelS')
def Hangar_as_setupAmmunitionPanelS(base, self, data):
    isCustomizationEnabled = g_currentVehicle.getViewState().isCustomizationEnabled()
    isVehicleCustomizable = g_currentVehicle.isInHangar()
    if isVehicleCustomizable and not isCustomizationEnabled:
        data['customizationTooltip'] = makeTooltip('#userCustomization:button/goToUserCustomization/tooltip/header', '#userCustomization:button/goToUserCustomization/tooltip/body')
        self.ammoPanel.flashObject.tuningBtn.label = '#userCustomization:button/goToUserCustomization/label'
    else:
        self.ammoPanel.flashObject.tuningBtn.label = '#menu:hangar/ammunitionPanel/tuningBtn'

    data['customizationEnabled'] = isCustomizationEnabled or isVehicleCustomizable
    base(self, data)

# Загрузка аутфита в ангаре.
@override(Vehicle, 'getOutfit')
def Vehicle_getOutfit(base, self, season):
    outfit = g_oucConfig.getVehicleOutfit(self.descriptor, season)

    if isInCustomization() or outfit is None:
        return base(self, season)
    
    return outfit

# Загрузка префабов в ангаре.
@override(HangarVehicleAppearance, '_HangarVehicleAppearance__assembleModel')
def HangarVehicleAppearance__assembleModel(base, self):
    base(self)
    vehicleDescriptor = self._HangarVehicleAppearance__vEntity.typeDescriptor

    if isInCustomization() or not g_oucCache.isCustomStyle3D(self.outfit.id):
        return
    
    if self.outfit.modelsSet:
        set3DStylePrefabs(vehicleDescriptor, self, self.outfit, g_oucCache)

# Загрузка аутфита и префабов к нему в бою.
@override(CompoundAppearance, '_prepareOutfit')
def CompoundAppearance_prepareOutfit(base, self, outfitCD):
    player = BigWorld.player()
    if player is not None and player.playerVehicleID == self.id:
        outfit = g_oucConfig.getVehicleOutfit(self.typeDescriptor, _currentMapSeason())
        if outfit is not None:
            if outfit.modelsSet:
                set3DStylePrefabs(self.typeDescriptor, self, outfit, g_oucCache)
            return outfit
        
    return base(self, outfitCD)
