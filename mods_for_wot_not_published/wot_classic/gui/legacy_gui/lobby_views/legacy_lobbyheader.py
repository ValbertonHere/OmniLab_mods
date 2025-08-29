import BigWorld
import constants
import th_async as future_async

from account_helpers.AccountSettings import ACTIVE_TEST_PARTICIPATION_CONFIRMED, AccountSettings
from adisp import adisp_process, adisp_async

from debug_utils import LOG_ERROR
from constants import PREBATTLE_TYPE
# from realm import CURRENT_REALM

from gui.impl import backport
from gui.impl.gen import R

from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader, HeaderMenuVisibilityState
from gui.Scaleform.framework.entities.View import View

from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.shared.formatters.currency import getBWFormatter
from gui.shared import event_dispatcher as shared_events, events
from gui.shared.money import Currency

from gui.ClientUpdateManager import g_clientUpdateManager
from gui.clans.clan_cache import g_clanCache
from gui.prb_control.dispatcher import EVENT_BUS_SCOPE
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import REQUEST_TYPE

from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IManualController, IPlatoonController, IServerStatsController, IGameSessionController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.web import IWebController
from skeletons.gui.impl import IGuiLoader

from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from helpers import i18n, time_utils, isPlayerAccount, dependency
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyGoldUrl, getBuyPremiumUrl
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

from gui.legacy_gui.lobby_views import getGUIConfig

from ..utils import restartAllView

class LegacyLobbyHeader(View, ClanEmblemsHelper, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    gameSession = dependency.descriptor(IGameSessionController)
    manualController = dependency.descriptor(IManualController)
    guiLoader = dependency.descriptor(IGuiLoader)
    platoonCtrl = dependency.descriptor(IPlatoonController)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    webCtrl = dependency.descriptor(IWebController)
    serverStats = dependency.descriptor(IServerStatsController)

    appLoader = dependency.instance(IAppLoader)

    LEGACY_HEADER_TABS = (LobbyHeader.TABS.HANGAR, LobbyHeader.TABS.STORE, LobbyHeader.TABS.PROFILE, LobbyHeader.TABS.TECHTREE, LobbyHeader.TABS.BARRACKS, LobbyHeader.TABS.BROWSER, 
                        LobbyHeader.TABS.RESEARCH, LobbyHeader.TABS.PERSONAL_MISSIONS, LobbyHeader.TABS.PERSONAL_MISSIONS_PAGE)
    SWF = None

    def __init__(self):
        super(LegacyLobbyHeader, self).__init__()
        self.__clanIconID = None
        self.__lobbyHeaderSrc = None
        self.isCrystalPremium = getGUIConfig()['isCrystalPremium']
        self.showPersonalQuests = getGUIConfig()['showPersonalQuests']
        self.showPersonalReserves = getGUIConfig()['showPersonalReserves']
        self.showTasks = getGUIConfig()['showTasks']
        self.showTutorial = getGUIConfig()['showTutorial']
        return

    def _populate(self):
        super(LegacyLobbyHeader, self)._populate()
        app = self.appLoader.getApp()
        self.__lobbyHeaderSrc = app.containerManager.getContainer(WindowLayer.VIEW).getView().getComponent('lobbyHeader')
        self._addListeners()
        self.as_setInDevS(False)
        self.as_setServerNameS()
        self.as_setUserNicknameS(g_clanCache.clanInfo)
        self.__getFormattedCurrency()
        self.__onPremiumExpireTimeChanged(None)
        self.as_showPersonalQuestsS(self.showPersonalQuests)
        self.as_showPersonalReservesS(self.showPersonalReserves)
        self.as_showTasksS(self.showTasks)
        self.as_showTutorialS(self.showTutorial)
        self.onVehicleChanged()
        self.as_setControlsEnabled()
        self.onPrbEntitySwitched()

    def _addListeners(self):
        self.startGlobalListening()
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updateLobbyHeaderButtons, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentVehicle.onChanged += self.onVehicleChanged
        g_currentVehicle.onChanged += self.__updateLobbyHeaderButtons
        g_currentPreviewVehicle.onChanged += self.onVehicleChanged
        g_currentPreviewVehicle.onChanged += self.__updateLobbyHeaderButtons
        g_playerEvents.onEnqueued += self.__updateLobbyHeaderButtons
        g_playerEvents.onDequeued += self.__updateLobbyHeaderButtons
        self.gameSession.onPremiumNotify += self.onPremiumChanged
        self.platoonCtrl.onMembersUpdate += self.__updateLobbyHeaderButtons
        self.serverStats.onStatsReceived += self.__onStatsReceived
        self.__onStatsReceived()
        g_clientUpdateManager.addCurrencyCallback(Currency.CRYSTAL, self.as_setCrystalS)
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.as_setCreditsS)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.as_setGoldS)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.as_setFreeXPS,
                                            'stats.clanInfo': self.as_setUserNicknameS,
                                            'account.activePremiumExpiryTime': self.__onPremiumExpireTimeChanged})
    
    def _dispose(self):
        self.stopGlobalListening()
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updateLobbyHeaderButtons, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentVehicle.onChanged -= self.onVehicleChanged
        g_currentVehicle.onChanged -= self.__updateLobbyHeaderButtons
        g_playerEvents.onEnqueued -= self.__updateLobbyHeaderButtons
        g_playerEvents.onDequeued -= self.__updateLobbyHeaderButtons
        self.gameSession.onPremiumNotify -= self.onPremiumChanged
        self.platoonCtrl.onMembersUpdate -= self.__updateLobbyHeaderButtons
        self.serverStats.onStatsReceived -= self.__onStatsReceived
        g_currentPreviewVehicle.onChanged -= self.onVehicleChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(LegacyLobbyHeader, self)._dispose()

    @adisp_process
    def fightClick(self, mmData, actionName):
        navigationPossible = yield self.lobbyContext.isHeaderNavigationPossible()
        fightButtonPressPossible = yield self.lobbyContext.isFightButtonPressPossible()
        if navigationPossible and fightButtonPressPossible:
            if self.prbDispatcher:
                prbEntity = self.prbDispatcher.getEntity()
                result = yield self.platoonCtrl.processPlatoonActions(mmData, prbEntity, g_currentVehicle)
                if not result:
                    actionAllowed = yield self.__processMMActiveTestConfirm(prbEntity)
                else:
                    actionAllowed = False
                if actionAllowed:
                    self.prbDispatcher.doAction(PrbAction(actionName, mmData))
            else:
                LOG_ERROR('Prebattle dispatcher is not defined')

    def as_setCrystal2Premium(self, isCrystalPremium, isPremium):
        self.isCrystalPremium = isCrystalPremium

        if self._isDAAPIInited():
            self.flashObject.as_setCrystal2Premium(isCrystalPremium, isPremium)

    def as_setControlsEnabled(self):
        if self._isDAAPIInited():
            self.flashObject.as_disableHeaderButtons(False)

    def as_setInDevS(self, isInDev):
        if self._isDAAPIInited():
            self.flashObject.as_setInDev(isInDev)

    def as_setServerNameS(self):
        if self._isDAAPIInited():
            self.flashObject.as_setServerName(i18n.makeString('#wek:lobbyHeader/serverInfo', serverName='"%s"' % self.connectionMgr.serverUserName))

    def as_setUserNicknameS(self, clanInfo, diff=None):
        if isPlayerAccount():
            fullUserName = self.lobbyContext.getPlayerFullName(BigWorld.player().name, clanInfo)
            isTeamKiller = self.itemsCache.items.stats.isTeamKiller
            if g_clanCache.clanDBID:
                self.__removeClanIconFromMemory()
                self.requestClanEmblem32x32(g_clanCache.clanDBID)
            if self._isDAAPIInited():
                self.flashObject.as_setUserNickname(fullUserName, isTeamKiller)

    def as_setCrystalS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_setCrystal(getBWFormatter(Currency.CRYSTAL)(value))

    def as_setGoldS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_setGold(getBWFormatter(Currency.GOLD)(value))

    def as_setCreditsS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_setCredits(getBWFormatter(Currency.CREDITS)(value))

    def as_setFreeXPS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_setFreeXP(getBWFormatter(Currency.FREE_XP)(value))
    
    def as_showPersonalReservesS(self, showPR):
        self.showPersonalReserves = showPR

        if self._isDAAPIInited():
            self.flashObject.as_showPersonalReserves(showPR)
    
    def as_showPersonalQuestsS(self, showPQ):
        self.showPersonalQuests = showPQ

        if self._isDAAPIInited():
            self.flashObject.as_showPersonalQuests(showPQ)
    
    def as_showTasksS(self, showTasks):
        self.showTasks = showTasks

        if self._isDAAPIInited():
            self.flashObject.as_showTasks(showTasks)
    
    def as_showTutorialS(self, showTutorial):
        self.showTutorial = showTutorial

        if self._isDAAPIInited():
            self.flashObject.as_showTutorial(showTutorial)

    def onClanEmblem32x32Received(self, _, emblem):
        if self._isDAAPIInited():
            self.flashObject.as_setClanEmblem(self.getMemoryTexturePath(emblem))

    def onClose(self):
        self.destroy()

    def onPrbEntitySwitched(self):
        if not self.prbDispatcher:
            LOG_ERROR('onPrbEntitySwitched: prbDispatcher is None')
            return
        
        items = battle_selector_items.getItems()
        squadItems = battle_selector_items.getSquadItems()
        state = self.prbDispatcher.getFunctionalState()
        selected = items.update(state)
        squadSelected = squadItems.update(state)
        playerInfo = self.prbDispatcher.getPlayerInfo()
        isSquad = self.prbDispatcher.getFunctionalState().isInUnit() and self.prbEntity.getEntityType() in PREBATTLE_TYPE.SQUAD_PREBATTLES
        battleType = '#menu:headerButtons/battle/types/%s' % squadSelected.getData() if isSquad else selected.getLabel()

        if self._isDAAPIInited():
            self.flashObject.as_setFightButtonLabel(self.__getFightButtonLabel(state, playerInfo))
            self.flashObject.as_setBattleType(i18n.makeString(battleType))

    def onVehicleChanged(self):
        vehicle = g_currentVehicle.item
        vehicle_preview = g_currentPreviewVehicle.item

        if vehicle_preview is not None:
            vehicle = vehicle_preview

        if vehicle is not None:
            vehName = vehicle.userName
            vehType = i18n.makeString('#menu:tankmen/%s' % vehicle.type).upper()
            xps = self.itemsCache.items.stats.vehiclesXPs
            xp = xps.get(vehicle.intCD, 0)
            
            if self._isDAAPIInited():
                self.flashObject.as_setVehInfo(vehName, vehType, getBWFormatter(Currency.FREE_XP)(xp), vehicle.isElite)

    def onResearchClick(self, _):
        shared_events.showResearchView(g_currentVehicle.item.intCD)

    def onMenuClick(self, _):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)
    
    def onCrystalClick(self, _):
        if self.isCrystalPremium:
            self.__closeWindowsWithTopSubViewLayer()
            shared_events.showShop(getBuyPremiumUrl())
        else:
            #if CURRENT_REALM != 'RU':
            #   shared_events.showCrystalWindow()
            #   return
            shared_events.showCrystalWindow(HeaderMenuVisibilityState.ALL)
    
    def onGoldClick(self, _):
        self.__closeWindowsWithTopSubViewLayer()
        shared_events.showShop(getBuyGoldUrl())
    
    def onTutorialClick(self, _):
        if self.manualController.isActivated():
            view = self.manualController.getView()
            if view is not None:
                pass
            else:
                self.manualController.show()
        return
    
    def onCreditsClick(self, _):
        shared_events.showExchangeCurrencyWindow()
    
    def onFreeXPClick(self, _):
        shared_events.showExchangeXPWindow()
    
    def onTasksClick(self):
        self.__lobbyHeaderSrc.menuItemClick(LobbyHeader.TABS.MISSIONS)

    def onNickClick(self, _):
        self.__lobbyHeaderSrc.showDashboard()
    
    def onClanClicked(self, _):
        shared_events.showStrongholds()
    
    def onInDevRestartClick(self, _):
        restartAllView()

    def __getFightButtonLabel(self, state, playerInfo):
        label = '#wek:lobbyHeader/fightButton/battle'
        if not playerInfo.isCreator and state.isReadyActionSupported():
            label = '#wek:lobbyHeader/fightButton/notReady' if playerInfo.isReady else '#wek:lobbyHeader/fightButton/ready'
        return label
    
    def __closeWindowsWithTopSubViewLayer(self):
        windows = self.guiLoader.windowsManager.findWindows(lambda w: w.layer == WindowLayer.TOP_SUB_VIEW)
        for window in windows:
            window.destroy()

    def __handleSetPrebattleCoolDown(self, event):
        if not self.prbDispatcher:
            return
        playerInfo = self.prbDispatcher.getPlayerInfo()
        isCreator = playerInfo.isCreator
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE and not isCreator and self._isDAAPIInited():
            self.flashObject.as_setCoolDownForReady(event.coolDown)

    def __updateLobbyHeaderButtons(self, *args, **kwargs):
        if not self.prbDispatcher:
            LOG_ERROR('__updateLobbyHeaderButtons: prbDispatcher is None')
            return
        else:
            items = battle_selector_items.getItems()
            state = self.prbDispatcher.getFunctionalState()
            selected = items.update(state)
            canDo = self.prbEntity.canPlayerDoAction().isValid
            isSquad = self.prbDispatcher.getFunctionalState().isInUnit() and self.prbEntity.getEntityType() in PREBATTLE_TYPE.SQUAD_PREBATTLES
            playerInfo = self.prbDispatcher.getPlayerInfo()
            isFightDisabled = not canDo or selected.isLocked if not isSquad and not playerInfo.isCreator else False

            if self._isDAAPIInited():
                self.flashObject.as_setFightButtonLabel(self.__getFightButtonLabel(state, playerInfo))
                self.flashObject.as_setFightButtonDisabled(isFightDisabled)
                self.flashObject.as_disableHeaderButtons(self.prbDispatcher.getFunctionalState().isNavigationDisabled())

    def __getFormattedCurrency(self):
        money = self.itemsCache.items.stats.actualMoney
        freeXP = self.itemsCache.items.stats.actualFreeXP

        self.as_setCrystalS(money.crystal)
        self.as_setGoldS(money.gold)
        self.as_setCreditsS(money.credits)
        self.as_setFreeXPS(freeXP)
    
    def onPremiumChanged(self, isPremium, attrs, premiumExpiryTime):
        self.__setPremium(isPremium)

    def __onPremiumExpireTimeChanged(self, _):
        isPremium = self.itemsCache.items.stats.isPremium
        self.__setPremium(isPremium)

    def __setPremium(self, isPremium):
        accAttrs = self.itemsCache.items.stats.attributes
        battle_selector_items.getItems().validateAccountAttrs(accAttrs)
        if isPremium:
            premTime = self.itemsCache.items.stats.activePremiumExpiryTime
            deltaInSeconds = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(premTime)))
            timeLeft, timeMetric = self.__lobbyHeaderSrc._LobbyHeader__getPremiumExpiryTimeAttrs(deltaInSeconds)
            if timeMetric == backport.text(R.strings.menu.header.account.premium.days()):
                accountType = i18n.makeString('#wek:lobbyHeader/premiumAcc/labelDays', days=int(timeLeft))
            else:
                accountType = i18n.makeString('#wek:lobbyHeader/premiumAcc/labelHours', hours=int(timeLeft))
        else:
            accountType = '#wek:lobbyHeader/baseAcc/label'

        if self._isDAAPIInited():
            self.flashObject.as_setAccountType(accountType)
        self.as_setCrystal2Premium(self.isCrystalPremium, isPremium)

    @adisp_async
    @future_async.th_async
    def __processMMActiveTestConfirm(self, prbEntity, callback):
        config = self.lobbyContext.getServerSettings().getActiveTestConfirmationConfig()
        toShow = bool(not AccountSettings.getSessionSettings(ACTIVE_TEST_PARTICIPATION_CONFIRMED) and config.get('enabled') and prbEntity.getQueueType() == constants.QUEUE_TYPE.RANDOMS and g_currentVehicle.item.level == 10)
        if not self.connectionMgr.isStandalone():
            toShow = toShow and self.connectionMgr.peripheryID in config.get('peripheryIDs', ())
        if toShow:
            result = yield future_async.wg_await(shared_events.showActiveTestConfirmDialog(config.get('startTime', 0.0), config.get('finishTime', 0.0), config.get('link', '')))
            if result:
                AccountSettings.setSessionSettings(ACTIVE_TEST_PARTICIPATION_CONFIRMED, True)
            callback(result)
        callback(True)

    def __onStatsReceived(self):
        clusterUsers, regionUsers, _ = self.serverStats.getStats()
        clusterUsers = '%s / %s' % (clusterUsers, regionUsers)
        if self._isDAAPIInited():
            self.flashObject.as_setOnline(clusterUsers)

    def __removeClanIconFromMemory(self):
        if self.__clanIconID is not None:
            self.removeTextureFromMemory(self.__clanIconID)
            self.__clanIconID = None
        return

print '[OMNILAB R&D: views.LegacyLobbyHeader] INITIALIZED!'