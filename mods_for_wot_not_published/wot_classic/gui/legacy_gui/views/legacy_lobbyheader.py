import BigWorld

from constants import PREBATTLE_TYPE
from realm import CURRENT_REALM

from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader, HeaderMenuVisibilityState
from gui.Scaleform.framework.entities.View import View

from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.shared.formatters.currency import getBWFormatter
from gui.shared import event_dispatcher as shared_events
from gui.shared.money import Currency

from gui.ClientUpdateManager import g_clientUpdateManager
from gui.clans.clan_cache import g_clanCache
from gui.prb_control.entities.listener import IGlobalListener
from gui.impl.gen import R
from gui.impl import backport

from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IManualController, IPlatoonController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.web import IWebController

from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from helpers import i18n, time_utils, isPlayerAccount, dependency
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowLayer

class LegacyLobbyHeader(View, ClanEmblemsHelper, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    manualController = dependency.descriptor(IManualController)
    platoonCtrl = dependency.descriptor(IPlatoonController)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    webCtrl = dependency.descriptor(IWebController)
    SWF = None

    def __init__(self):
        super(LegacyLobbyHeader, self).__init__()
        self.__clanIconID = None
        self.__lobbyHeaderSrc = None
        LegacyLobbyHeader.SWF = self
        return

    def _populate(self):
        super(LegacyLobbyHeader, self)._populate()
        
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        self.__lobbyHeaderSrc = app.containerManager.getContainer(WindowLayer.VIEW).getView().getComponent('lobbyHeader')
        self._addListeners()
        self.as_setServerNameS()
        self.as_setUserNicknameS(g_clanCache.clanInfo)
        self.__getFormattedCurrency()
        self.__onPremiumExpireTimeChanged(None)
        self.onVehicleChanged()
        self.as_setControlsEnabled()
        self.onPrbEntitySwitched()

    def _addListeners(self):
        self.startGlobalListening()
        g_currentVehicle.onChanged += self.onVehicleChanged
        g_currentPreviewVehicle.onChanged += self.onVehicleChanged
        g_playerEvents.onEnqueued += self.as_disableHeaderButtonsS
        g_playerEvents.onDequeued += self.as_disableHeaderButtonsS
        self.platoonCtrl.onMembersUpdate += self.as_disableHeaderButtonsS
        g_clientUpdateManager.addCurrencyCallback(Currency.CRYSTAL, self.as_setCrystalS)
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.as_setCreditsS)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.as_setGoldS)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.as_setFreeXPS,
                                            'stats.clanInfo': self.as_setUserNicknameS,
                                            'account.activePremiumExpiryTime': self.__onPremiumExpireTimeChanged})
    
    def _dispose(self):
        self.stopGlobalListening()
        g_currentVehicle.onChanged -= self.onVehicleChanged
        g_playerEvents.onEnqueued -= self.as_disableHeaderButtonsS
        g_playerEvents.onDequeued -= self.as_disableHeaderButtonsS
        self.platoonCtrl.onMembersUpdate -= self.as_disableHeaderButtonsS
        g_currentPreviewVehicle.onChanged -= self.onVehicleChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(LegacyLobbyHeader, self)._dispose()

    def onClanEmblem32x32Received(self, _, emblem):
        self.flashObject.as_setClanEmblem(self.getMemoryTexturePath(emblem))

    def onClose(self):
        self.destroy()
        
    def pyLog(self, msg):
        print '[OMNILAB: LegacyLobbyHeader] %s' % (msg)

    def __removeClanIconFromMemory(self):
        if self.__clanIconID is not None:
            self.removeTextureFromMemory(self.__clanIconID)
            self.__clanIconID = None
        return

    def as_setControlsEnabled(self):
        self.flashObject.as_disableHeaderButtons(False)
    
    def onPrbEntitySwitched(self):
        if not self.prbDispatcher:
            self.pyLog('onPrbEntitySwitched: prbDispatcher is None')
            return
        
        items = battle_selector_items.getItems()
        squadItems = battle_selector_items.getSquadItems()
        state = self.prbDispatcher.getFunctionalState()
        selected = items.update(state)
        squadSelected = squadItems.update(state)
        isSquad = self.prbDispatcher.getFunctionalState().isInUnit() and self.prbEntity.getEntityType() in PREBATTLE_TYPE.SQUAD_PREBATTLES
        battleType = '#menu:headerButtons/battle/types/%s' % squadSelected.getData() if isSquad else selected.getLabel()
        LegacyLobbyHeader.SWF.flashObject.as_setBattleType(i18n.makeString(battleType))

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
            
            self.flashObject.as_setVehInfo(vehName, vehType, getBWFormatter(Currency.FREE_XP)(xp), vehicle.isElite)

    def onResearchClick(self, _):
        shared_events.showResearchView(g_currentVehicle.item.intCD)

    def onMenuClick(self, _):
        self.__lobbyHeaderSrc.showLobbyMenu()
    
    def onCrystalClick(self, _):
        if CURRENT_REALM == 'RU':
            shared_events.showCrystalWindow(HeaderMenuVisibilityState.ALL)
        else: 
            shared_events.showCrystalWindow()
    
    def onGoldClick(self, _):
        self.__lobbyHeaderSrc.onPayment()
    
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

    def __onPremiumExpireTimeChanged(self, _):
        if self.itemsCache.items.stats.isPremium:
            premTime = self.itemsCache.items.stats.activePremiumExpiryTime
            deltaInSeconds = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(premTime)))
            timeLeft, timeMetric = self.__lobbyHeaderSrc._LobbyHeader__getPremiumExpiryTimeAttrs(deltaInSeconds)
            if timeMetric == backport.text(R.strings.menu.header.account.premium.days()):
                timeMetric = i18n.makeString('#wek:lobbyHeader/premiumAcc/days', days=int(timeLeft))
            else:
                timeMetric = i18n.makeString('#wek:lobbyHeader/premiumAcc/hours', hours=int(timeLeft))

            accountType = '<TEXTFORMAT INDENT="0" LEFTMARGIN="0" RIGHTMARGIN="0" LEADING="2"><P ALIGN="LEFT"><FONT FACE="$FieldFont" COLOR="#fffbce86" KERNING="0">#wek:lobbyHeader/premiumAcc/label</FONT></P><P ALIGN="LEFT"><FONT FACE="$FieldFont" COLOR="#ffced9d9" KERNING="0">%s</FONT></P></TEXTFORMAT>' % timeMetric
        else:
            accountType = '<TEXTFORMAT INDENT="0" LEFTMARGIN="0" RIGHTMARGIN="0" LEADING="2"><P ALIGN="LEFT"><FONT FACE="$FieldFont" COLOR="#ff7f7d6a" KERNING="0">#wek:lobbyHeader/baseAcc/label</FONT></P></TEXTFORMAT>'

        self.flashObject.as_setAccountType(accountType)

    def as_setServerNameS(self):
        serverName = '<TEXTFORMAT INDENT="0" LEFTMARGIN="0" RIGHTMARGIN="0" LEADING="2"><P ALIGN="CENTER"><FONT FACE="$FieldFont" COLOR="#ffced9d9" KERNING="0">#menu:header/serverInfo</FONT></P><P ALIGN="CENTER"><FONT FACE="$FieldFont" COLOR="#fffbce86" KERNING="0"> "%s"</FONT></P></TEXTFORMAT>' % self.connectionMgr.serverUserName
        self.flashObject.as_setServerName(serverName)

    def as_disableHeaderButtonsS(self, *args, **kwargs):
        if not self.prbDispatcher:
            self.pyLog('as_disableHeaderButtonsS: prbDispatcher is None')
            return
        else:
            self.flashObject.as_disableHeaderButtons(self.prbDispatcher.getFunctionalState().isNavigationDisabled())

    def as_setUserNicknameS(self, clanInfo, diff=None):
        if isPlayerAccount():
            fullUserName = self.lobbyContext.getPlayerFullName(BigWorld.player().name, clanInfo)
            isTeamKiller = self.itemsCache.items.stats.isTeamKiller
            if g_clanCache.clanDBID:
                self.__removeClanIconFromMemory()
                self.requestClanEmblem32x32(g_clanCache.clanDBID)
            self.flashObject.as_setUserNickname(fullUserName, isTeamKiller)

    def as_setCrystalS(self, value):
        self.flashObject.as_setCrystal(getBWFormatter(Currency.CRYSTAL)(value))

    def as_setGoldS(self, value):
        self.flashObject.as_setGold(getBWFormatter(Currency.GOLD)(value))

    def as_setCreditsS(self, value):
        self.flashObject.as_setCredits(getBWFormatter(Currency.CREDITS)(value))

    def as_setFreeXPS(self, value):
        self.flashObject.as_setFreeXP(getBWFormatter(Currency.FREE_XP)(value))

    def __getFormattedCurrency(self):
        money = self.itemsCache.items.stats.actualMoney
        freeXP = self.itemsCache.items.stats.actualFreeXP

        self.as_setCrystalS(money.crystal)
        self.as_setGoldS(money.gold)
        self.as_setCreditsS(money.credits)
        self.as_setFreeXPS(freeXP)

print '[OMNILAB R&D: views.LegacyLobbyHeader] INITIALIZED!'