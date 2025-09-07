from helpers import dependency
# from realm import CURRENT_REALM
from PlayerEvents import g_playerEvents

from backports.functools_lru_cache import lru_cache

from goodies.goodie_constants import GOODIE_STATE

from gui.shared.event_dispatcher import showBoostersActivation
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.ClientUpdateManager import g_clientUpdateManager

from gui.Scaleform.framework.entities.View import View

from skeletons.gui.web import IWebController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.game_control import IBoostersController

class PersonalReservesComponent(View):
    _boosters = dependency.descriptor(IBoostersController)
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _webCtrl = dependency.descriptor(IWebController)
    SWF = None

    def __init__(self):
        super(PersonalReservesComponent, self).__init__()
        PersonalReservesComponent.SWF = self

    def _populate(self):
        super(PersonalReservesComponent, self)._populate()
        self.addListeners()
        self._update()

    def addListeners(self):
        g_clientUpdateManager.addCallbacks({'stats.clanInfo': self._update, 
           'cache.activeOrders': self._update})
        g_playerEvents.onClientUpdated += self._onClientUpdated
        self._boosters.onGameModeStatusChange += self._update
        self._boosters.onReserveTimerTick += self._update
        self._boosters.onBoosterChangeNotify += self._update
        # else: (for not RU realm)
        #     self._boosters.onPersonalReserveTick += self._update
        #     self._boosters.onClanReserveTick += self._update
        #     self._boosters.onBoostersDataUpdate += self._update

    
    def _dispose(self):
        self._boosters.onReserveTimerTick -= self._update
        self._boosters.onBoosterChangeNotify -= self._update
        # else: (for not RU realm)
        #     self._boosters.onPersonalReserveTick -= self._update
        #     self._boosters.onClanReserveTick -= self._update
        #     self._boosters.onBoostersDataUpdate -= self._update
        self._boosters.onGameModeStatusChange -= self._update
        g_playerEvents.onClientUpdated -= self._onClientUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(PersonalReservesComponent, self)._dispose()

    def showReservesWindow(self):
        from gui.prb_control.dispatcher import g_prbLoader

        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None and not prbDispatcher.getFunctionalState().isNavigationDisabled():
            showBoostersActivation()
        
    @lru_cache()
    def getAllBoosterIds(self):
        enabledBoosters = self._goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ENABLED)
        return set(enabledBoosters.keys())

    def boostersInClientUpdate(self, diff):
        return set(diff.get('goodies', {}).keys()).intersection(self.getAllBoosterIds()) or diff.get('cache', {}).get('activeOrders', {})

    def getActiveBoosters(self):
        storageBoostersCount = 0
        storageBoosters = self._goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IS_READY_TO_ACTIVATE).values()

        for storageBooster in storageBoosters:
            storageBoostersCount += storageBooster.count

        activeBoosters = self._goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values()
        activeClanBoosters = self.getActiveClanBoosters()
        activeBoostersPool = activeClanBoosters if len(activeClanBoosters) != 0 else activeBoosters
        minUsageTime = min(booster.getUsageLeftTime() for booster in activeBoostersPool) if bool(activeBoostersPool) else 0

        return {'personalCount': len(activeBoosters),
                'clanCount': len(activeClanBoosters),
                'personalStorageCount': storageBoostersCount,
                'usageTime': minUsageTime}
    
    def getActiveClanBoosters(self):
        if self._webCtrl.getAccountProfile().isInClan():
            clanBoosters = [clanBooster for clanBooster in self._goodiesCache.getClanReserves().values() if clanBooster.state == GOODIE_STATE.ACTIVE]
            return clanBoosters
        return []
    
    def _onClientUpdated(self, diff, *args, **kwargs):
        if self.boostersInClientUpdate(diff):
            self._update()

    def _update(self, *args, **kwargs):
        self.flashObject.as_setData(self.getActiveBoosters())

print '[OMNILAB R&D: views.PersonalReservesComponent] INITIALIZED!'