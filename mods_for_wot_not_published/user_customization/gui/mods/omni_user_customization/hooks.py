import logging
import BigWorld

from CurrentVehicle import g_currentVehicle

from gui.hangar_vehicle_appearance import HangarVehicleAppearance

from gui.impl.pub.dialog_window import DialogButtons

from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel import AmmunitionPanel

from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import makeTooltip

from items.components.c11n_constants import ApplyArea

from vehicle_systems.camouflages import _currentMapSeason
from vehicle_systems.CompoundAppearance import CompoundAppearance

from .cache import g_oucCache
from .config import g_oucConfig
from .utils import override, isInCustomization, set3DStylePrefabs, showCustomizationDialog, loadOUCWindow

__all__ = ()
logger = logging.getLogger(__name__)

@override(AmmunitionPanel, 'showCustomization')
def AmmunitionPanel_showCustomization(base, self):
    isServerCamoApplied = False
    vehicle = g_currentVehicle.item
    isCustomizationEnabled = g_currentVehicle.getViewState().isCustomizationEnabled()
    isVehicleCustomizable = g_currentVehicle.isInHangar()

    # Интересно, повторяется ли этот (https://github.com/ValbertonHere/user-customization-bugtracker/issues/18) баг?
    # А баг ли это? Или просто не на всех сезонах камуфляж применён? Шамиль, дай ответ пж.
    for camo in vehicle.getOutfitComponent(vehicle.getAnyOutfitSeason()).camouflages: 
        if camo.appliedTo in (ApplyArea.HULL, ApplyArea.CAMOUFLAGE_REGIONS_VALUE):
            isServerCamoApplied = True 
            break
    
    def onResult(result):
        if result == DialogButtons.SUBMIT or result == DialogButtons.PURCHASE:
            base(self)
        elif result == DialogButtons.RESEARCH:
            loadOUCWindow()

    if isVehicleCustomizable and not isCustomizationEnabled:
        loadOUCWindow()
    else:
        showCustomizationDialog(isServerCamoApplied, onResult)
    
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

    if isInCustomization() or not g_oucCache.is3DStyleCustom(self.outfit.id):
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