# Основа от POLIROID.

import ResMgr
from debug_utils import LOG_ERROR
from items.vehicles import g_cache
from items.components.c11n_components import StyleItem, CamouflageItem, DecalItem, PaintItem
from vehicle_systems import camouflages
from vehicle_systems.CompoundAppearance import CompoundAppearance
from VehicleStickers import VehicleStickers

from .utils import readUserCustomItem, awaitGameLoadingComplete

__all__ = ()

'''
# change vehicle outfit (may dont work if arena data not ready)
@override(CompoundAppearance, '_prepareOutfit')
def _prepareOutfit(baseMethod, baseInstance, outfitCD):
	if isBattleRestricted():
		return baseMethod(baseInstance, outfitCD)
	from .controllers import g_controllers
	outfit = g_controllers.vehicle.getVehicleOutfit(baseInstance, baseInstance.outfit)
	return outfit or baseMethod(baseInstance, outfitCD)

# this need for fix vehicles that dont changed during arena not ready
@override(CompoundAppearance, '_CompoundAppearance__applyVehicleOutfit')
def _applyVehicleOutfit(baseMethod, baseInstance):
	if isBattleRestricted():
		return baseMethod(baseInstance)
	from .controllers import g_controllers
	outfit = g_controllers.vehicle.getVehicleOutfit(baseInstance, baseInstance.outfit)
	baseInstance._CommonTankAppearance__outfit = outfit or baseInstance.outfit
	# update cammo
	camouflages.updateFashions(baseInstance)
	# recreate stickers
	baseInstance._createStickers()
	return baseMethod(baseInstance)

# fix decals transperent problem
@override(VehicleStickers, '__init__')
def _createAndAttachStickers(baseMethod, baseInstance, *a, **kw):
	baseMethod(baseInstance, *a, **kw)
	if isBattleRestricted():
		return
	baseInstance._VehicleStickers__defaultAlpha = 1.0

# modsListApi
g_modsListApi = None
try:
	from gui.modsListApi import g_modsListApi
except ImportError:
	LOG_ERROR('modsListApi not installed')
if g_modsListApi:
	g_modsListApi.addModification(id='branding', name=l10n('modslist.name'), enabled=True,
		description=l10n('modslist.description'), icon='gui/maps/icons/brandingIcon.png',
		login=True, lobby=True, callback=g_eventsManager.showUI)
'''

def injectUserCustomization():
	cache = g_cache.customization20()
	for filename, dataSection in ResMgr.openSection('omnilab/user_customization/xml').items():
		if 'styles' in filename:
			itemClass = StyleItem
			itemType = 'style'
			storage = cache.styles
		elif 'camouflages' in filename:
			itemClass = CamouflageItem
			itemType = 'camouflage'
			storage = cache.camouflages
		elif 'decals' in filename:
			itemClass = DecalItem
			itemType = 'decal'
			storage = cache.decals
		elif 'paints' in filename:
			itemClass = PaintItem
			itemType = 'paint'
			storage = cache.paints
		else:
			return
		
		readUserCustomItem(itemClass, itemType, filename, dataSection, cache, storage)

injectUserCustomization()