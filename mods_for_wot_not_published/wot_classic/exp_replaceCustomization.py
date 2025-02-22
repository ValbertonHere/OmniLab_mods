from CurrentVehicle import g_currentVehicle
from vehicle_outfit.outfit import Outfit
from items.customizations import ProjectionDecalComponent, CustomizationOutfit, CamouflageComponent, PaintComponent, InsigniaComponent
from items.vehicles import g_cache
from items.components.c11n_constants import ApplyArea

hangarSpace = g_currentVehicle.hangarSpace
vehicle = hangarSpace.getVehicleEntity()


def getOutfit(camoID):
    camos = [CamouflageComponent(id=camoID, appliedTo=ApplyArea.HULL),
             CamouflageComponent(id=camoID, appliedTo=ApplyArea.TURRET),
             CamouflageComponent(id=camoID, appliedTo=ApplyArea.GUN)]
    
    return Outfit(CustomizationOutfit(camouflages=camos).makeCompDescr())

vehicle.updateVehicleCustomization(getOutfit(14881))