import BigWorld, ResMgr, logging, json

from adisp import adisp_process

from CurrentVehicle import g_currentVehicle

from collections import defaultdict
from copy import deepcopy
from itertools import chain

from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import pushI18nMessage, SM_TYPE
from gui.game_loading.resources.consts import Milestones

from helpers import dependency, isPlayerAccount

from items.components.c11n_constants import EMPTY_ITEM_ID
from items.vehicles import g_cache

from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

from PlayerEvents import g_playerEvents

from time import sleep
from threading import Thread

from ._constants import GAME_CACHE_DUMMY, NOTIFICATION_HEADER, OUC_CACHE_DUMMY, FORBIDDEN_STYLES # <- Чуть позже внедрю.
from .json_reader import g_jsonReaders
from .utils import loadOUCWindow, getDevModeState

logger = logging.getLogger(__name__)

class UserCustomizationCacheCollector():
    c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self):
        self.prefabs = {}
        self.allUserStylesPool = {}
        self.resetCache()
        self.injectUserCustomization()
        g_playerEvents.onLoadingMilestoneReached += self.onReadyToCollectData
        logger.info('Data collector initialized!')

    def onReadyToCollectData(self, milestone):
        if milestone == Milestones.HANGAR_SPACE_VEHICLE and not self.game_cache['styles']['2d']:
            self.collectGameStylesData()

    def resetCache(self):
        self.mod_cache, self.game_cache = deepcopy(OUC_CACHE_DUMMY), deepcopy(GAME_CACHE_DUMMY)

    def collectGameStylesData(self):
        for styleID, styleInfo in g_cache.customization20().styles.iteritems():
            if styleID == EMPTY_ITEM_ID or styleInfo.isHiddenInUI() or styleID in FORBIDDEN_STYLES:
                continue
            styleType = '2d' if not styleInfo.modelsSet else '3d'
            if styleID not in self.game_cache['styles'][styleType]:
                self.game_cache['styles'][styleType][styleID] = self.c11nService.getItemByID(32, styleID)

    def isCustomStyle3D(self, styleID):
        return styleID in self.mod_cache['styles']['3d']
    
    def getComponentStrIDFromIntID(self, componentType, intID):
        if componentType == 'styles':
            for k, v in self.allUserStylesPool.items():
                if v[0] == intID:
                    return k
        else:
            for k, v in g_oucCache.mod_cache[componentType].items():
                if v == intID:
                    return k

    def getComponentIntIDFromStrID(self, componentType, strID):
        if componentType == 'styles':
            return self.mod_cache[componentType]['3d'].get(strID, (None, ))[0] or self.mod_cache[componentType]['2d'].get(strID, (None, ))[0]
        else:
            return self.mod_cache[componentType][strID]

    def doReloadCache(self):
        Thread(target=self.__reloadCache).start()

    def injectUserCustomization(self):
        try:
            JSONSection = ResMgr.openSection('valberton/user_customization/json')
            if JSONSection:
                for filename, dataSection in JSONSection.items():
                    self.readUserCustomization(filename, json.loads(dataSection.asString))
            
            self.allUserStylesPool = dict(chain(self.mod_cache['styles']['2d'].items(), self.mod_cache['styles']['3d'].items()))
        except:
            logger.exception('Failed to inject user customization. See lines below')
            BigWorld.crash(1)

    def readUserCustomization(self, filename, jsonParent):
        # Сначала грузим шрифты и секвенсы, так как это - зависимость персональных номеров и аттачментов соответственно.
        for itemType, jsonChild in jsonParent.items():
            if itemType in ('sequences', 'fonts'):
                    reader = g_jsonReaders[itemType](self)
                    reader.readItems(jsonChild)

        # Потом грузим остальные элементы, чтобы выдать им уникальные ID.
        for itemType, jsonChild in jsonParent.items():
            if itemType not in ('styles', 'sequences', 'fonts'):
                    reader = g_jsonReaders[itemType](self)
                    reader.readItems(jsonChild)
        
        # Теперь грузим стили, чтобы эти уникальные ID применились к стилям.
        for itemStrID, styleJSONData in jsonParent['styles'].items():
            reader = g_jsonReaders['styles'](self)
            reader.readItems(itemStrID, styleJSONData)

        if getDevModeState():
            logger.info('valberton/user_customization/json/%s readed successfully!' % (filename))

    @adisp_process
    def __reloadCache(self):
        if isPlayerAccount():
            try:
                self.resetCache()

                itemsCache = dependency.instance(IItemsCache)
                
                g_cache._Cache__customization20 = None
                waitingView = Waiting.getWaitingView(True)

                pushI18nMessage('#userCustomization:notification/reloadCacheStarted', type=SM_TYPE.WarningHeader, messageData=NOTIFICATION_HEADER)
                yield itemsCache.update(1, notify=False)
                waitingView.as_showWaitingS('#userCustomization:waiting/userCustomizationInject', False)
                self.injectUserCustomization()
                waitingView.as_showWaitingS('#userCustomization:waiting/stylesDataCollect', False)
                self.collectGameStylesData()
                waitingView.as_showWaitingS('#userCustomization:waiting/itemsSync', False)
                itemsCache.onSyncCompleted(1, defaultdict(set))
                g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
                sleep(0.1) # https://youtu.be/LZNw8t1k1rI?si=RKiYaxToafDS5Wap&t=27
                g_currentVehicle.refreshModel()
                sleep(0.2)
                waitingView.as_hideWaitingS()
                loadOUCWindow()
            except:
                waitingView.as_hideWaitingS()
                pushI18nMessage('#userCustomization:notification/reloadCacheFailed', type=SM_TYPE.InformationHeader, messageData=NOTIFICATION_HEADER)
                logger.exception('Failed to reload cache. See lines before. Restart client is recommended.')

g_oucCache = UserCustomizationCacheCollector()