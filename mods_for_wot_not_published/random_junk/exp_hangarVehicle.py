# Спавн танка в ангаре.

import BigWorld
from CurrentVehicle import g_currentVehicle
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from gui.shared.utils.requesters import REQ_CRITERIA

itemsCache = dependency.instance(IItemsCache)
#entities = []
print itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.LEVELS([6])).values()[100].descriptor
#entity = BigWorld.createEntity('HangarPoster', g_currentVehicle.hangarSpace.spaceID, 0, BigWorld.player().position + (-4, 1, 0), (0.0, 0.0, 0.0), {})
#entities.append(entity)
print BigWorld.entities[entities[1]].modelName