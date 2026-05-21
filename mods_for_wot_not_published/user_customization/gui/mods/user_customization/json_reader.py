import items.components.c11n_components as cc
import Math
import json
import logging
import ResMgr

from gui.shared.gui_items.customization.c11n_items import Style
from nations import AVAILABLE_NAMES
from items.vehicles import g_cache, makeVehicleTypeCompDescrByName, CompositeVehicleDescriptor
from items.components import shared_components
from items.components.c11n_constants import CustomizationNamesToTypes, DecalType
from items.customizations import CustomizationOutfit
from items.components.c11n_constants import SeasonType, CamouflageTilingTypeNameToType

from skeletons.gui.shared import IItemsCache
from helpers import dependency

from ._constants import OUTFIT_COMPONENT_NAME_TO_OBJECT, USER_START_UNIQUE_ID
from .utils import reader_exception_handler, getDevModeState

logger = logging.getLogger(__name__)

class JSONReaderError(Exception): pass

def readColor(palette):
    for color in palette:
        if not 0 <= color < 256:
            raise JSONReaderError('Color component is out of range [0, 255].')
    
    return palette[0] + (palette[1] << 8) + (palette[2] << 16) + (palette[3] << 24)

class BaseJSONReader(object):
    def __init__(self, itemCls, itemTypeName, storage, mod_storage):
        self.itemTypeName = itemTypeName
        self.itemCls = itemCls
        self.storage = storage
        self.mod_storage = mod_storage
        self.item = None
        self.jsonObj = None
        self.itemStrID = ''

    def __getItemUniqueID(self):
        try:
            return max(self.mod_storage.mod_cache[self.itemTypeName].values()) + 1 if self.itemTypeName != 'styles' else max([v[0] for v in self.mod_storage.mod_cache['styles']['2d'].values()] + [v[0] for v in self.mod_storage.mod_cache['styles']['3d'].values()]) + 1
        except ValueError:
            return USER_START_UNIQUE_ID
    
    def setItemDefaults(self):
        self.item.id = self.__getItemUniqueID()

        if hasattr(self.item, 'tags'):
            self.item.tags = set(['hiddenInUI'])
        
        if hasattr(self.item, 'customizationDisplayType'):
            self.item.customizationDisplayType = 0
    
    def putItemToStorage(self, strID):
        self.storage[self.item.id] = self.item
        self.mod_storage.mod_cache[self.itemTypeName][strID] = self.item.id

    def readItems(self):
        self.item = self.itemCls()
        self.setItemDefaults()

class AttachmentsJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(AttachmentsJSONReader, self).__init__(cc.AttachmentItem, 'attachments', g_cache.customization20().attachments, mod_storage)
    
    def setItemDefaults(self):
        super(AttachmentsJSONReader, self).setItemDefaults()
        self.item.initialVisibility = True
    
    @reader_exception_handler
    def readItems(self, jsonObj):
        for strID, obj in jsonObj.items():
            super(AttachmentsJSONReader, self).readItems()
            self.itemStrID = strID
            self.item.modelName = obj.get('modelName')
            self.item.hangarModelName = obj.get('hangarModelName', '')
            self.item.sequenceId = obj.get('sequenceId', None)
            self.item.attachmentLogic = obj.get('attachmentLogic')
            self.putItemToStorage(strID)

class CamouflagesJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(CamouflagesJSONReader, self).__init__(cc.CamouflageItem, 'camouflages', g_cache.customization20().camouflages, mod_storage)
    
    def setItemDefaults(self):
        super(CamouflagesJSONReader, self).setItemDefaults()
        self.item.invisibilityFactor = 1
        self.item.palettes = ([4278190335, 4278255360, 4294901760, 4278190080], )

    @reader_exception_handler
    def readItems(self, jsonObj):
        for strID, obj in jsonObj.items():
            super(CamouflagesJSONReader, self).readItems()
            self.itemStrID = strID

            # Значения из JSON.
            # Сразу отсеиваем конфиги без обязательных параметров.
            if 'tilingSettings' not in obj or 'scales' not in obj or 'texture' not in obj:
                raise JSONReaderError("One of these necessary parameters not found in [%s] camouflage JSON object: %s." % (strID, ('tilingSettings', 'scales', 'texture')))
            
            # Если всё прошло успешно - продолжаем читать.
            tilingSettings = obj['tilingSettings']
            self.item.tilingSettings = (CamouflageTilingTypeNameToType[tilingSettings['type'].upper()], tuple(tilingSettings['factor']), tuple(tilingSettings['offset']))
            
            self.item.scales = tuple(obj['scales'])
            self.item.texture = obj['texture']
            self.item.glossMetallicSettings = {'glossMetallicMap': obj.get('glossMetallicMap', ''), 
                                        'metallic': Math.Vector4(obj.get('metallic', (0.23, 0.23, 0.23, 0.23))), 
                                        'gloss': Math.Vector4(obj.get('gloss', (0.509, 0.509, 0.509, 0.509)))}
            self.item.emissionSettings = {'emissionMap': obj.get('emissionMap', ''), 
                                    'emissionPatternMap': obj.get('emissionPatternMap', ''),
                                    'emissionAnimationSpeed': obj.get('emissionAnimationSpeed', 1.0), 
                                    'forwardEmissionBrightness': obj.get('forwardEmissionBrightness', 1.0),
                                    'deferredEmissionBrightness': obj.get('deferredEmissionBrightness', 1.0)}
            self.item.normalSettings = {'normalMap': obj.get('normalMap', ''), 
                                'normalMaxLod': obj.get('normalMaxLod', 1), 
                                'normalMapFactor': obj.get('normalMapFactor', 1.0)}

            if 'rotation' in obj:
                self.item.rotation = {'hull': obj['rotation'].get('hull', 0.0),
                                'turret': obj['rotation'].get('turret', 0.0),
                                'gun': obj['rotation'].get('gun', 0.0)}
            
            if 'palettes' in obj:
                palettes = []
                jpalettes = obj['palettes']
                if len(jpalettes) != 4:
                    raise JSONReaderError("Need 4 lists of values in palettes. It's RGBA! Example: [[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255], [0, 0, 0, 255]] | strID=%s" % strID)
            
                for palette in jpalettes:
                    palettes.append(readColor(palette))

                self.item.palettes = (palettes, )

            self.putItemToStorage(strID)

class DecalsJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(DecalsJSONReader, self).__init__(cc.DecalItem, 'decals', g_cache.customization20().decals, mod_storage)
    
    @reader_exception_handler
    def readItems(self, jsonObj):
        for strID, obj in jsonObj.items():
            super(DecalsJSONReader, self).readItems()
            self.itemStrID = strID

            if 'texture' not in obj or 'type' not in obj:
                raise JSONReaderError("One of these necessary parameters not found in [%s] camouflage JSON object: %s." % (strID, ('texture', 'type')))
            
            self.item.texture = obj['texture']
            self.item.type = getattr(DecalType, obj['type'])
            self.item.canBeMirrored = obj.get('mirror', False)

            self.putItemToStorage(strID)

class FontsJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(FontsJSONReader, self).__init__(cc.Font, 'fonts', g_cache.customization20().fonts, mod_storage)
    
    @reader_exception_handler
    def readItems(self, jsonObj):
        for strID, obj in jsonObj.items():
            super(FontsJSONReader, self).readItems()
            self.itemStrID = strID

            if 'alphabet' not in obj or 'texture' not in obj:
                raise JSONReaderError("One of these necessary parameters not found in [%s] font JSON object: %s." % (strID, ('alphabet', 'texture')))
            
            self.item.texture = obj['texture']
            self.item.alphabet = obj['alphabet']
            self.item.mask = obj.get('mask', '')
            self.putItemToStorage(strID)

class InsigniasJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(InsigniasJSONReader, self).__init__(cc.InsigniaItem, 'insignias', g_cache.customization20().insignias, mod_storage)
    
    @reader_exception_handler
    def readItems(self, jsonObj):
        for strID, obj in jsonObj.items():
            super(InsigniasJSONReader, self).readItems()
            self.itemStrID = strID

            if 'atlas' not in obj or 'alphabet' not in obj or 'texture' not in obj:
                raise JSONReaderError("One of these necessary parameters not found in [%s] insignia JSON object: %s." % (strID, ('atlas', 'alphabet', 'texture')))

            self.item.atlas = obj['atlas']
            self.item.alphabet = obj['alphabet']
            self.item.texture = obj['texture']
            self.item.emissionSettings = {'emissionMap': obj.get('emissionMap', ''), 
                                    'emissionPatternMap': obj.get('emissionPatternMap', ''),
                                    'emissionAnimationSpeed': obj.get('emissionAnimationSpeed', 1.0), 
                                    'forwardEmissionBrightness': obj.get('forwardEmissionBrightness', 1.0),
                                    'deferredEmissionBrightness': obj.get('deferredEmissionBrightness', 1.0)}
        
            self.item.canBeMirrored = obj.get('mirror', False)

            self.putItemToStorage(strID)

class PaintsJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(PaintsJSONReader, self).__init__(cc.PaintItem, 'paints', g_cache.customization20().paints, mod_storage)
    
    def setItemDefaults(self):
        super(PaintsJSONReader, self).setItemDefaults()
        self.item.tags.add('styleOnly')

    @reader_exception_handler
    def readItems(self, jsonObj):
        for strID, obj in jsonObj.items():
            super(PaintsJSONReader, self).readItems()
            self.itemStrID = strID

            if 'color' not in obj or 'texture' not in obj:
                raise JSONReaderError("One of these necessary parameters not found in [%s] paints JSON object: %s." % (strID, ('color', 'texture')))
            
            self.item.texture = obj['texture']
            self.item.color = readColor(obj['color'])
            self.item.gloss = obj.get('gloss', 0.0)
            self.item.metallic = obj.get('metallic', 0.0)
            self.putItemToStorage(strID)

class PersonalNumbersJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(PersonalNumbersJSONReader, self).__init__(cc.PersonalNumberItem, 'personal_numbers', g_cache.customization20().personal_numbers, mod_storage)
    
    @reader_exception_handler
    def readItems(self, jsonObj):
        fontsCache = g_cache.customization20().fonts
        for strID, obj in jsonObj.items():
            super(PersonalNumbersJSONReader, self).readItems()
            self.itemStrID = strID

            if 'fontID' not in obj or 'texture' not in obj:
                raise JSONReaderError("One of these necessary parameters not found in [%s] paints JSON object: %s." % (strID, ('fontID', 'texture')))
            
            self.item.texture = obj['texture']
            self.item.digitsCount = obj.get('digitsCount', 3)

            # Так как мы можем использовать шрифты из модов и из игры, лучше проверить, является ли ID шрифта строкой или нет.
            if isinstance(obj['fontID'], str):
                self.item.fontInfo = fontsCache[self.mod_storage.mod_cache['fonts'][obj['fontID']]]
            else:
                self.item.fontInfo = fontsCache[obj['fontID']]
            self.putItemToStorage(strID)

class ProjectionDecalsJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(ProjectionDecalsJSONReader, self).__init__(cc.ProjectionDecalItem, 'projection_decals', g_cache.customization20().projection_decals, mod_storage)
    
    @reader_exception_handler
    def readItems(self, jsonObj):
        for strID, obj in jsonObj.items():
            super(ProjectionDecalsJSONReader, self).readItems()
            self.itemStrID = strID

            if 'texture' not in obj:
                raise JSONReaderError("Necessary parameter 'texture' not found in [%s] projection decal JSON object." % (strID))

            self.item.texture = obj['texture']
            self.item.glossTexture = obj.get('glossTexture', '')
            self.item.scaleFactorId = obj.get('scaleFactorId', 3)

            self.item.canBeMirroredHorizontally = obj.get('mirror', False)
            self.item.emissionSettings = {'emissionMap': obj.get('emissionMap', ''), 
                                    'emissionPatternMap': obj.get('emissionPatternMap', ''),
                                    'emissionAnimationSpeed': obj.get('emissionAnimationSpeed', 1.0), 
                                    'forwardEmissionBrightness': obj.get('forwardEmissionBrightness', 1.0),
                                    'deferredEmissionBrightness': obj.get('deferredEmissionBrightness', 1.0)}
            self.putItemToStorage(strID)

class SequencesJSONReader(BaseJSONReader):
    def __init__(self, mod_storage):
        super(SequencesJSONReader, self).__init__(cc.SequenceItem, 'sequences', g_cache.customization20().sequences, mod_storage)
    
    @reader_exception_handler
    def readItems(self, jsonObj):
        for strID, obj in jsonObj.items():
            super(SequencesJSONReader, self).readItems()
            self.itemStrID = strID

            if 'sequenceName' not in obj:
                raise JSONReaderError("Necessary parameter 'sequenceName' not found in [%s] sequence JSON object." % (strID))
            
            self.item.sequenceName = obj['sequenceName']
            self.putItemToStorage(strID)

class StyleJSONReader(BaseJSONReader):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, mod_storage):
        super(StyleJSONReader, self).__init__(cc.StyleItem, 'styles', g_cache.customization20().styles, mod_storage)
    
    def __readFilterNode(self, jsonObj):
        if 'nations' not in jsonObj and 'levels' not in jsonObj and 'vehicles' not in jsonObj:
            raise JSONReaderError('No available nodes found! Available node names: nations, levels, vehicles.')
        
        node = cc.VehicleFilter.FilterNode()
        for nodeName, nodeData in jsonObj.items():
            if nodeName not in ('nations', 'levels', 'vehicles'):
                raise JSONReaderError('Node name "%s" not available! Available node names: nations, levels, vehicles.' % nodeName)
            
            if nodeName == 'nations':
                for nation in nodeData:
                    if nation not in AVAILABLE_NAMES:
                        raise JSONReaderError('Unknown nation: %s. Available nations: %s' % (nation, list(AVAILABLE_NAMES))) 
                node.nations = nodeData

            if nodeName == 'levels':
                node.levels = tuple(nodeData)

            if nodeName == 'vehicles':
                vehicles = set()
                for vehicleName in nodeData:
                    try:
                        vehTypeCompDescr = makeVehicleTypeCompDescrByName(vehicleName)
                        vehicles.add(vehTypeCompDescr)
                    except:
                        raise JSONReaderError('Unknown vehicle: %s. Vehicle naming usage: nation:vehicleTechnicalName!')
                node.vehicles = vehicles

        return node
        
    def __readVehicleFilter(self, jsonObj):
        if jsonObj is None:
            return
        if 'include' in jsonObj and 'exclude' in jsonObj:
            raise JSONReaderError('Don\'t use "include" and "exclude" at the same time in one item. Choose only one! StyleID = %s' % self.itemStrID)
        if 'include' not in jsonObj and 'exclude' not in jsonObj:
            raise JSONReaderError('Should be "include" or "exclude"! StyleID = %s' % self.itemStrID)

        filter = cc.VehicleFilter()
        for filterType, node in jsonObj.items():
            getattr(filter, filterType).append(self.__readFilterNode(node))

        return filter

    def __readOutfits(self, outfitsList):
        outfits = {}
        for jsonOutfit in outfitsList:
            outfit = CustomizationOutfit()
            outfit.styleId = self.item.id

            for field, data in jsonOutfit.items():
                if field in OUTFIT_COMPONENT_NAME_TO_OBJECT:
                    items = []
                    for item in data:
                        if isinstance(item['id'], unicode):
                            item['id'] = self.mod_storage.getComponentIntIDFromStrID(field, item['id'])

                        items.append(OUTFIT_COMPONENT_NAME_TO_OBJECT[field](**item))

                    setattr(outfit, field, items)
                elif field == 'modification':
                    outfit.modifications.append(data)

            season = getattr(SeasonType, jsonOutfit['season'])

            for s in SeasonType.SEASONS:
                if s & season:
                    outfits[s] = outfit
                    
        return outfits

    def __read3DStyleModels(self, vehicleCD, modelsSet):
        self.mod_storage.prefabs[modelsSet] = {'guns': {}, 'turrets': {}, 'hull': {}, 'chassis': {}}
        vehicleGunsAndTurrets = {'guns': {}, 'turrets': {}}

        vehicle = self.itemsCache.items.getItemByCD(vehicleCD)

        if isinstance(vehicle, CompositeVehicleDescriptor):
            vehicle = vehicle.currentDescr

        styleModels = json.loads(ResMgr.openSection('valberton/user_customization/3Dst_json/%s.json' % modelsSet).asString)
        for gun in vehicle.getComponentsByType('vehicleGun')[1]:
            if getDevModeState():
                logger.info('Reading gun in %s: %s' % (vehicle.name, gun.name))
            vehicleGunsAndTurrets['guns'][gun.name] = gun

        for turret in vehicle.getComponentsByType('vehicleTurret')[1]:
            vehicleGunsAndTurrets['turrets'][turret.name] = turret

        for tankPartName, styleModels in styleModels.items():
            if tankPartName in ('gun', 'turret'):
                raise JSONReaderError('Use "guns" and "turrets" instead of "gun" and "turret" in %s.json!' % modelsSet)

            elif tankPartName in vehicleGunsAndTurrets:
                for partSubName, models in styleModels.items():
                    vehicleGunsAndTurrets[tankPartName][partSubName].modelsSets[modelsSet] = shared_components.ModelStatesPaths(models['undamaged'], models['destroyed'], models['exploded'])
                    if models.get('prefab', None) is not None:
                        self.mod_storage.prefabs[modelsSet][tankPartName][partSubName] = models['prefab']
            else:
                tankPart = getattr(vehicle, tankPartName)
                tankPart.modelsSets[modelsSet] = shared_components.ModelStatesPaths(styleModels['undamaged'], styleModels['destroyed'], styleModels['exploded'])
                if styleModels.get('prefab', None) is not None:
                    self.mod_storage.prefabs[modelsSet][tankPartName] = styleModels['prefab']

    def putItemToStorage(self, is3DStyle, strID):
        if strID in self.mod_storage.mod_cache['styles']['3d'] or strID in self.mod_storage.mod_cache['styles']['2d']:
            raise JSONReaderError('Style string ID "%s" already in 2D or 3D styles IDs pool!' % strID)
        
        g_cache.customization20().styles[self.item.id] = self.item
        self.mod_storage.mod_cache['styles']['3d' if is3DStyle else '2d'][strID] = (self.item.id, Style(self.item.compactDescr))

    @reader_exception_handler
    def readItems(self, strID, jsonObj):
        self.itemStrID = strID

        if 'styleIcon' not in jsonObj or 'styleName' not in jsonObj or 'outfits' not in jsonObj:
            raise JSONReaderError("One of these necessary parameters not found in [%s] style JSON object: %s." % (strID, ('styleIcon', 'styleName', 'outfits')))
        
        # Это чисто для тултипов стилей.
        group = cc.ItemGroup(self.itemCls)
        group.itemPrototype = self.itemCls()
        self.item = self.itemCls(group)
        self.setItemDefaults()

        self.item.texture = jsonObj['styleIcon']
        self.item.i18n = shared_components.I18nExposedComponent(jsonObj['styleName'], jsonObj.get('styleDescription', ''), '')

        is3DStyle = jsonObj.get('is3D', False)

        if jsonObj.get('isWithSerialNumber', False):
            self.item.tags.add('styleSerialNumber')

        self.item.filter = self.__readVehicleFilter(jsonObj.get('vehicleFilter', None))
        
        if is3DStyle:
            if not jsonObj.has_key('modelsSet'):
                raise JSONReaderError("Necessary parameter 'modelsSet' not found in [%s] 3D style JSON object." % (strID))
            
            self.item.modelsSet = jsonObj['modelsSet']
            for vehicleCD in self.item.filter.include[0].vehicles:
                self.__read3DStyleModels(vehicleCD, self.item.modelsSet)
        
        jsonAlternateItems = jsonObj.get('alternateItems', None)
        if jsonAlternateItems is not None:
            self.item.isEditable = True
            alternateItems = {}
            for itemTypeName, itemsList in jsonAlternateItems.items():
                itemsIntList = []
                c11nType = CustomizationNamesToTypes[itemTypeName.upper()]
                for itemID in itemsList:
                    itemsIntList.append(self.mod_storage.getComponentIntIDFromStrID(itemTypeName + 's', itemID) if isinstance(itemID, unicode) else itemID)
                alternateItems[c11nType] = tuple(itemsIntList)
            
            self.item.alternateItems = alternateItems
        
        jsonOutfits = jsonObj.get('outfits', None)
        if jsonOutfits is None:
            raise JSONReaderError('No outfits specified for style: %s!' % strID)

        self.item.outfits = self.__readOutfits(jsonOutfits)
        self.putItemToStorage(is3DStyle, strID)

g_jsonReaders = {
    'attachments': AttachmentsJSONReader,
    'camouflages': CamouflagesJSONReader,
    'decals': DecalsJSONReader,
    'insignias': InsigniasJSONReader,
    'fonts': FontsJSONReader,
    'paints': PaintsJSONReader,
    'personal_numbers': PersonalNumbersJSONReader,
    'projection_decals': ProjectionDecalsJSONReader,
    'sequences': SequencesJSONReader,
    'styles': StyleJSONReader}