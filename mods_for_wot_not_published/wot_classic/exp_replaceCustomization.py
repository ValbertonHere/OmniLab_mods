from CurrentVehicle import g_currentVehicle
from vehicle_outfit.outfit import Outfit
from items.customizations import ProjectionDecalComponent, CustomizationOutfit, CamouflageComponent, PaintComponent, InsigniaComponent
from items.vehicles import g_cache

hangarSpace = g_currentVehicle.hangarSpace
vehicle = hangarSpace.getVehicleEntity()

projectionDecals = [ProjectionDecalComponent(id=882, tags=[('front', 'safe', 'formfactor_square')])]
modifications = [(4)]
styleId = 781
insignias = [InsigniaComponent(31016, 4096)]
camos = [CamouflageComponent(15940, 1, 4368, 0)]
paints = [PaintComponent(401, 30583)]
custOutfit = Outfit(component=CustomizationOutfit(camouflages=camos, styleId=styleId, paints=paints, projection_decals=projectionDecals))

print g_cache.customization20().itemTypes[4]