import BigWorld, ResMgr, logging, json

from adisp import adisp_process

from CurrentVehicle import g_currentVehicle

from collections import defaultdict
from copy import deepcopy

from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import pushI18nMessage, SM_TYPE
from gui.game_loading.resources.consts import Milestones

from helpers import dependency, isPlayerAccount

from items.components.c11n_components import AttachmentItem, CamouflageItem, DecalItem, InsigniaItem, ModificationItem, PaintItem, PersonalNumberItem, ProjectionDecalItem, StyleItem, Font
from items.components.c11n_constants import EMPTY_ITEM_ID
from items.components.shared_components import ModelStatesPaths
from items.vehicles import g_cache, VehicleDescr, CompositeVehicleDescriptor

from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

from PlayerEvents import g_playerEvents

from time import sleep
from threading import Thread

from ._constants import GAME_CACHE_DUMMY, NOTIFICATION_HEADER, OUC_CACHE_DUMMY, FORBIDDEN_STYLES # <- Чуть позже внедрю.
from .utils import readUserCustomItem, loadOUCWindow
from .config import g_oucConfig

logger = logging.getLogger(__name__)

ITEMS_INJECT_MAP = {'attachments': (AttachmentItem, 'attachment'),
                    'camouflages': (CamouflageItem, 'camouflage'),
                    'decals': (DecalItem, 'decal'),
                    'insignias': (InsigniaItem, 'insignia'),
                    'modifications': (ModificationItem, 'modification'),
                    'paints': (PaintItem, 'paint'),
                    'personalnumbers': (PersonalNumberItem, 'personal_number'),
                    'fonts': (Font, 'fonts'),
                    'projectiondecals': (ProjectionDecalItem, 'projection_decal'),
                    'styles': (StyleItem, 'style')}

class UserCustomizationCacheCollector():
    c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self):
        self.prefabs = {}
        self.resetCache()
        self.injectUserCustomization()
        g_playerEvents.onLoadingMilestoneReached += self.onReadyToCollectData
        logger.info('Data collector initialized!')

    def onReadyToCollectData(self, milestone):
        if milestone == Milestones.HANGAR_SPACE_VEHICLE and not self.game_cache['styles']['2d']:
            self.collectData()

    def resetCache(self):
        self.mod_cache, self.game_cache = deepcopy(OUC_CACHE_DUMMY), deepcopy(GAME_CACHE_DUMMY)

    def collectData(self):
        for styleType, styleIDs in self.mod_cache['styles'].iteritems():
            for styleID in styleIDs.keys():
                self.mod_cache['styles'][styleType][styleID] = self.c11nService.getItemByID(32, styleID)
        
        for styleID, styleInfo in g_cache.customization20().styles.iteritems():
            if styleID == EMPTY_ITEM_ID or styleInfo.isHiddenInUI() or styleID in FORBIDDEN_STYLES:
                continue
            styleType = '2d' if not styleInfo.modelsSet else '3d'
            if styleID not in self.game_cache['styles'][styleType]:
                self.game_cache['styles'][styleType][styleID] = self.c11nService.getItemByID(32, styleID)

    def is3DStyleCustom(self, styleID):
        return styleID in self.mod_cache['styles']['3d']

    @adisp_process
    def __reloadCache(self):
        if isPlayerAccount():
            try:
                self.resetCache()

                itemsCache = dependency.instance(IItemsCache)
                
                g_cache._Cache__customization20 = None
                waitingView = Waiting.getWaitingView(True)

                pushI18nMessage('#userCustomization:notification/reloadCacheStarted', type=SM_TYPE.WarningHeader, messageData={'header': NOTIFICATION_HEADER})
                yield itemsCache.update(1, notify=False)
                waitingView.as_showWaitingS('#userCustomization:waiting/userCustomizationInject', False)
                self.injectUserCustomization()
                waitingView.as_showWaitingS('#userCustomization:waiting/stylesDataCollect', False)
                self.collectData()
                waitingView.as_showWaitingS('#userCustomization:waiting/itemsSync', False)
                itemsCache.onSyncCompleted(1, defaultdict(set))
                waitingView.as_hideWaitingS()
                g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
                sleep(0.1) # https://youtu.be/LZNw8t1k1rI?si=RKiYaxToafDS5Wap&t=27
                g_currentVehicle.refreshModel()
                sleep(0.2)
                loadOUCWindow()
            except:
                waitingView.as_hideWaitingS()
                pushI18nMessage('#userCustomization:notification/reloadCacheFailed', type=SM_TYPE.InformationHeader, messageData={'header': NOTIFICATION_HEADER})
                logger.exception('Failed to reload cache. See lines before. Restart client is recommended.')

    def doReloadCache(self):
        Thread(target=self.__reloadCache).start()
    
    def read3DStyleModels(self, vehicleName, modelsSet):
        self.prefabs[modelsSet] = {'guns': {}, 'turrets': {}, 'hull': {}, 'chassis': {}}
        vehicleGunsAndTurrets = {'guns': {}, 'turrets': {}}
        vehicle = VehicleDescr(typeName=vehicleName)

        if isinstance(vehicle, CompositeVehicleDescriptor):
            vehicle = vehicle.currentDescr

        styleModels = json.loads(ResMgr.openSection('valberton/user_customization/3Dst_json/%s.json' % modelsSet).asBinary)

        for gun in vehicle.getComponentsByType('vehicleGun')[1]:
            if g_oucConfig.getDevModeState():
                logger.debug('Reading gun in %s: %s' % (vehicleName, gun.name))
            vehicleGunsAndTurrets['guns'][gun.name] = gun

        for turret in vehicle.getComponentsByType('vehicleTurret')[1]:
            vehicleGunsAndTurrets['turrets'][turret.name] = turret

        for tankPartName, styleModels in styleModels.items():
            if tankPartName in ('gun', 'turret'):
                logger.critical('Use "guns" and "turrets" instead of "gun" and "turret" in %s.json!' % modelsSet)
                BigWorld.crash(1)
            elif tankPartName in vehicleGunsAndTurrets:
                for partSubName, models in styleModels.items():
                    vehicleGunsAndTurrets[tankPartName][partSubName].modelsSets[modelsSet] = ModelStatesPaths(models['undamaged'], models['destroyed'], models['exploded'])
                    if models.get('prefab', None) is not None:
                        self.prefabs[modelsSet][tankPartName][partSubName] = models['prefab']
            else:
                tankPart = getattr(vehicle, tankPartName)
                tankPart.modelsSets[modelsSet] = ModelStatesPaths(styleModels['undamaged'], styleModels['destroyed'], styleModels['exploded'])
                if styleModels.get('prefab', None) is not None:
                    self.prefabs[modelsSet][tankPartName] = styleModels['prefab']

    def injectUserCustomization(self):
        customizationCache = g_cache.customization20()

        def readUC(filename, dataSection):
            if '.xml' not in filename:
                return
            
            itemsTypeName = filename.split('_')[-1].replace('.xml', '')

            if itemsTypeName in ITEMS_INJECT_MAP:
                itemClass, itemType = ITEMS_INJECT_MAP[itemsTypeName]
                storage = getattr(customizationCache, itemType + 's', None)
            else:
                return
            
            for name, section in dataSection['itemGroup'].items():
                if name != itemType:
                    continue
                itemTypeCache = self.mod_cache[itemType + 's']
                itemID = section.readInt('id')
                styleType = '3d' if section.has_key('modelsSet') else '2d'
                
                if itemID in itemTypeCache: # <- Вот эту проблему нужно как-то решать. Как? Да чёрт его знает...
                    logger.warning("Duplicate ID in OUC cache, it will be overriden, change it in your XML's to a unique one! (itemID=%s, itemType=%s)" % (itemID, itemType))
                
                if itemType == 'style':
                    itemTypeCache[styleType][itemID] = None
                else:
                    itemTypeCache.append(itemID)
            
                if styleType == '3d':
                    self.read3DStyleModels(section.parentSection()['vehicleFilter/include'].readString('vehicles'), section.readString('modelsSet'))
                    
            readUserCustomItem(itemClass, itemType, filename, dataSection, customizationCache, storage)
            
            if g_oucConfig.getDevModeState():
                logger.info('Readed %s from valberton/user_customization/xml/%s!' % (itemsTypeName, filename))

        try:
            XMLSection = ResMgr.openSection('valberton/user_customization/xml')
            if XMLSection:
                for filename, dataSection in XMLSection.items():
                    readUC(filename, dataSection)
        except:
            logger.exception('Failed to inject user customization. See lines below')
            BigWorld.crash(1)

g_oucCache = UserCustomizationCacheCollector()