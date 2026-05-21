import BigWorld, ResMgr, logging, json, os
from collections import defaultdict
from copy import deepcopy
from itertools import chain
from time import sleep
from threading import Thread

from CurrentVehicle import g_currentVehicle

from gui.game_loading.resources.consts import Milestones
from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import pushI18nMessage, SM_TYPE

from helpers import dependency, isPlayerAccount

from items.components.c11n_constants import EMPTY_ITEM_ID
from items.vehicles import g_cache

from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

from th_async import th_async, await_callback

from PlayerEvents import g_playerEvents

from ._constants import ITEMS_CACHE_UPDATE_POOL, GAME_CACHE_DUMMY, NOTIFICATION_HEADER, UC_CACHE_DUMMY, USER_CUSTOMIZATION_CACHE, SERVER_FORBIDDEN_CONTENT_GIT, SERVER_FORBIDDEN_CONTENT_VALSPACE, CLIENT_FORBIDDEN_CONTENT, FORBIDDEN_CONTENT_FILE, SUCCESS_STATUSES
from .json_reader import g_jsonReaders
from .utils import loadUCWindow, getDevModeState

logger = logging.getLogger(__name__)

class UserCustomizationCacheCollector():
    c11nService = dependency.descriptor(ICustomizationService)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.prefabs = {}
        self.allUserStylesPool = {}
        self.forbiddenContent = json.load(open(FORBIDDEN_CONTENT_FILE, 'r')) if os.path.exists(FORBIDDEN_CONTENT_FILE) else CLIENT_FORBIDDEN_CONTENT
        self.serversFetchAttempts = 0
        self.isGameStylesCollected = False
        self.resetCache()
        self.injectUserCustomization()
        self.__getForbiddenContent()
        logger.info('Data collector initialized!')

    def onReadyToCollectData(self, milestone):
        if milestone == Milestones.HANGAR_SPACE_VEHICLE and not self.isGameStylesCollected:
            g_playerEvents.onLoadingMilestoneReached -= self.onReadyToCollectData
            self.collectGameStylesData()

    def resetCache(self):
        g_playerEvents.onLoadingMilestoneReached += self.onReadyToCollectData
        self.mod_cache, self.game_cache = deepcopy(UC_CACHE_DUMMY), deepcopy(GAME_CACHE_DUMMY)
        self.isGameStylesCollected = False

    def collectGameStylesData(self):
        for styleID, styleInfo in g_cache.customization20().styles.iteritems():
            if styleID == EMPTY_ITEM_ID or styleInfo.isHiddenInUI() or styleID in self.forbiddenContent['styles']:
                continue
            styleType = '2d' if not styleInfo.modelsSet else '3d'
            if styleID not in self.game_cache['styles'][styleType]:
                self.game_cache['styles'][styleType][styleID] = self.c11nService.getItemByID(32, styleID)
        self.isGameStylesCollected = True

    def isCustomStyle3D(self, styleID):
        return styleID in self.mod_cache['styles']['3d']
    
    def getComponentStrIDFromIntID(self, componentType, intID):
        if componentType == 'styles':
            for k, v in self.allUserStylesPool.items():
                if v[0] == intID:
                    return k
        else:
            for k, v in self.mod_cache[componentType].items():
                if v == intID:
                    return k

    def getComponentIntIDFromStrID(self, componentType, strID):
        if componentType == 'styles':
            return self.mod_cache[componentType]['3d'].get(strID, (None, ))[0] or self.mod_cache[componentType]['2d'].get(strID, (None, ))[0]
        else:
            return self.mod_cache[componentType][strID]

    def injectUserCustomization(self):
        try:
            JSONSection = ResMgr.openSection('valberton/user_customization/json')
            if JSONSection:
                for filename, dataSection in JSONSection.items():
                    if filename.endswith('.json'):
                        self.readUserCustomization(filename, json.loads(dataSection.asString))
            
            self.allUserStylesPool = dict(chain(self.mod_cache['styles']['2d'].items(), self.mod_cache['styles']['3d'].items()))
        except:
            logger.exception('Failed to inject user customization. See lines below')
            BigWorld.crash(1)

    def readUserCustomization(self, filename, jsonParent):
        if getDevModeState():
            logger.info('Start reading valberton/user_customization/json/%s readed successfully!' % (filename))

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

    def doReloadCache(self):
        Thread(target=self.__reloadCache).start()

    @th_async
    def __getForbiddenContent(self):
        if not os.path.exists(USER_CUSTOMIZATION_CACHE):
            os.makedirs(USER_CUSTOMIZATION_CACHE)
        
        # Заправшиваем данные с файла на github.
        logger.info('Fetching main forbidden content data server origins for recieving actual data...')
        response = yield await_callback(BigWorld.fetchURL)(url=SERVER_FORBIDDEN_CONTENT_GIT, method='GET', headers='Content-Type: application/json', timeout=10.0, body='')

        # Если github лежит/забанен/на него упал метеорит - заправшиваем данные с файла на моём сервере.
        if response.responseCode not in SUCCESS_STATUSES:
            logger.warning('Unable to recieve actual forbidden content data from main origin. Trying to use second server.')
            response = yield await_callback(BigWorld.fetchURL)(url=SERVER_FORBIDDEN_CONTENT_VALSPACE, method='GET', headers='Content-Type: application/json', timeout=10.0, body='')

        # Условия для обоих ответов серверов.
        if response.responseCode in SUCCESS_STATUSES:
            self.forbiddenContent = json.loads(response.body)
            json.dump(self.forbiddenContent, open(FORBIDDEN_CONTENT_FILE, 'wb'))
            logger.info('Actual forbidden content data recieved successfully.')
        else:
            logger.warning('Unable to recieve actual forbidden content data. Using client-side data.')

    def __reloadCache(self):
        if isPlayerAccount():
            invalidateItems = defaultdict(set)

            try:
                self.resetCache()
                
                waitingView = Waiting.getWaitingView(True)
                pushI18nMessage('#userCustomization:notification/reloadCacheStarted', type=SM_TYPE.WarningHeader, messageData=NOTIFICATION_HEADER)

                waitingView.as_showWaitingS('#userCustomization:waiting/recreateGameC11n20Cache', False)

                # Очищаем глобальный кэш кастомизации игры и заполняем его стандартными элементами кастомизации игры.
                g_cache._Cache__customization20 = None
                g_cache.customization20()
                
                # Очищаем кэш кастомизации игры в кэше предметов.
                for itemTypeID in ITEMS_CACHE_UPDATE_POOL:
                    self.itemsCache.items._ItemsRequester__itemsCache[itemTypeID].clear()
                
                # Заполняем его стандартными предметами игры.
                self.itemsCache.items.inventory.initC11nItemsNoveltyData()
                self.itemsCache.compatVehiclesCache.invalidateData(self.itemsCache, invalidateItems)
                self.itemsCache.onSyncCompleted(1, invalidateItems)

                waitingView.as_showWaitingS('#userCustomization:waiting/userCustomizationInject', False)

                # Внедряем свои элементы кастомизации.
                self.injectUserCustomization()

                waitingView.as_showWaitingS('#userCustomization:waiting/stylesDataCollect', False)
                
                # Собираем данные об пользовательских элементах кастомизации.
                self.collectGameStylesData()

                # Полностью обновляем модель.
                g_currentVehicle.refreshModel(self.c11nService.getEmptyOutfit())
                sleep(0.1) # https://youtu.be/LZNw8t1k1rI?si=RKiYaxToafDS5Wap&t=27
                g_currentVehicle.refreshModel()
                sleep(0.2)
                waitingView.as_hideWaitingS()
                loadUCWindow()
            except:
                waitingView.as_hideWaitingS()
                pushI18nMessage('#userCustomization:notification/reloadCacheFailed', type=SM_TYPE.InformationHeader, messageData=NOTIFICATION_HEADER)
                logger.exception('Failed to reload cache. See lines before. Restart client is recommended.')

g_ucCache = UserCustomizationCacheCollector()

