import BigWorld
from CurrentVehicle import g_currentVehicle
from vehicle_outfit.outfit import Outfit
from items.customizations import parseOutfitDescr, CustomizationOutfit, CamouflageComponent, AttachmentComponent, PaintComponent
from items.vehicles import makeIntCompactDescrByID, getItemByCompactDescr
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from helpers import dependency
from vehicle_systems.camouflages import getOutfitComponent
from gui.hangar_vehicle_appearance import HangarVehicleAppearance

class Nig():
    customizationService = dependency.descriptor(ICustomizationService)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

customizationService = Nig().customizationService
itemsFactory = Nig().itemsFactory

hangarSpace = g_currentVehicle.hangarSpace
vehicle = hangarSpace.getVehicleEntity()
vehicleApp = hangarSpace.getVehicleEntityAppearance()

print vehicleApp.outfit.pack()
camos = [CamouflageComponent(518, 2, 4368, 0)]#, CamouflageComponent(id=camoId, appliedTo=256), CamouflageComponent(id=camoId, appliedTo=4096)]
paints = [PaintComponent(262, 30583)]
custOutfit = Outfit(component=CustomizationOutfit(camouflages=camos, paints=paints))
#outfit = customizationService.getEmptyOutfitWithNationalEmblems(vehicle.typeDescriptor.makeCompactDescr())
hangarSpace.updateVehicleOutfit(custOutfit)