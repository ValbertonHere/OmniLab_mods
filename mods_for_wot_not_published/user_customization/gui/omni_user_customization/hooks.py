# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

from debug_utils import LOG_ERROR
from items.vehicles import g_cache
from items.components.c11n_components import CamouflageItem, DecalItem, PaintItem
from vehicle_systems import camouflages
from vehicle_systems.CompoundAppearance import CompoundAppearance
from VehicleStickers import VehicleStickers

from .utils import readBrandingItem, awaitGameLoadingComplete

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

def customization_inject():
	print 'NIGGER INJECT!'
	cache = g_cache.customization20()
	readBrandingItem(CamouflageItem, 'camouflage', cache, cache.camouflages)
	#readBrandingItem(DecalItem, 'decal', cache, cache.decals)
	#readBrandingItem(PaintItem, 'paint', cache, cache.paints)

customization_inject()