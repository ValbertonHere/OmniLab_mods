from vehicle_outfit.outfit import Outfit
from vehicle_systems.CompoundAppearance import CompoundAppearance
from OpenModsCore import overrideMethod

@overrideMethod(CompoundAppearance, '_prepareOutfit')
def _prepareOutfit(baseMethod, baseInstance, outfitCD):
	outfit = Outfit()
	return outfit or baseMethod(baseInstance, outfitCD)

@overrideMethod(CompoundAppearance, '_CompoundAppearance__applyVehicleOutfit')
def _applyVehicleOutfit(baseMethod, baseInstance):
	outfit = Outfit()
	baseInstance._CommonTankAppearance__outfit = outfit or baseInstance.outfit
	return baseMethod(baseInstance)