import BigWorld

from adisp import adisp_process
from constants import PREBATTLE_TYPE
from realm import CURRENT_REALM

from gui.impl import backport
from gui.impl.gen import R

from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.lobby.header.BattleTypeSelectPopover import BattleTypeSelectPopover
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SquadItem, _R_BATTLE_TYPES
from gui.Scaleform.daapi.view.lobby.hangar.daily_quest_widget import DailyQuestWidget
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader, HeaderMenuVisibilityState
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shared.formatters import text_styles
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

from ..utils import override

class LegacyLobbyHeader(View, ClanEmblemsHelper, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    manualController = dependency.descriptor(IManualController)
    platoonCtrl = dependency.descriptor(IPlatoonController)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    webCtrl = dependency.descriptor(IWebController)

    appLoader = dependency.instance(IAppLoader)

    LEGACY_HEADER_TABS = (LobbyHeader.TABS.HANGAR, LobbyHeader.TABS.STORE, LobbyHeader.TABS.PROFILE, LobbyHeader.TABS.TECHTREE, LobbyHeader.TABS.BARRACKS, LobbyHeader.TABS.BROWSER, 
                        LobbyHeader.TABS.RESEARCH, LobbyHeader.TABS.PERSONAL_MISSIONS, LobbyHeader.TABS.PERSONAL_MISSIONS_PAGE)
    SWF = None

    def __init__(self):
        super(LegacyLobbyHeader, self).__init__()
        self.__clanIconID = None
        self.__lobbyHeaderSrc = None
        LegacyLobbyHeader.SWF = self

        override(BattleTypeSelectPopover, 'as_updateS', self._BattleTypeSelectPopover_as_updateS)
        override(BattleTypeSelectPopover, '_BattleTypeSelectPopover__selectFight', self._BattleTypeSelectPopover__selectFight)
        override(CachedBlur, 'enable', self._CachedBlur_enable)
        override(DailyQuestWidget, '_DailyQuestWidget__show', self._DailyQuestWidget__show)
        override(LobbyHeader, '_populateButtons', self._LobbyHeader_populateButtons)
        override(LobbyHeader, '_LobbyHeader__setCounter', self._LobbyHeader__setCounter)
        override(LobbyHeader, '_LobbyHeader__hideCounter', self._LobbyHeader__hideCounter)
        override(LobbyHeader, 'as_updateOnlineCounterS', self._LobbyHeader_as_updateOnlineCounterS)
        override(LobbyHeader, '_getHangarMenuItemDataProvider', self._LobbyHeader_getHangarMenuItemDataProvider)
        return

    def _populate(self):
        super(LegacyLobbyHeader, self)._populate()
        
        app = self.appLoader.getApp()
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


    def _BattleTypeSelectPopover_as_updateS(self, base, baseSelf, items, extraItems, isShowDemonstrator, demonstratorEnabled):
        squad = _SquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.simpleSquad())), PREBATTLE_ACTION_NAME.SQUAD, 0)
        items.insert(1, squad.getVO())
        base(baseSelf, items, extraItems, isShowDemonstrator, demonstratorEnabled)

    @adisp_process
    def _BattleTypeSelectPopover__selectFight(self, base, baseSelf, actionName):
        if actionName == 'squad':
            prbDispatcher = g_prbLoader.getDispatcher()
            yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.SQUAD))
        else:
            base(baseSelf, actionName)

    def _LobbyHeader__setCounter(self, base, baseSelf, alias, counter=None):
        if alias in self.LEGACY_HEADER_TABS:
            base(baseSelf, alias, counter)
        else: pass

    def _LobbyHeader__hideCounter(self, base, baseSelf, alias):
        if alias in self.LEGACY_HEADER_TABS:
            base(baseSelf, alias)
        else: pass

    def _LobbyHeader_getHangarMenuItemDataProvider(self, base, baseSelf):
        buttonsToExclude = [i for i in baseSelf.BUTTONS.ALL()]
        baseSelf.as_setHeaderButtonsS(baseSelf._getAvailableButtons(buttonsToExclude))
        tabDataProvider = [
        {'label': MENU.HEADERBUTTONS_HANGAR, 
            'value': baseSelf.TABS.HANGAR, 
            'textColor': 16764006,
            'textColorOver': 16768409, 
            'tooltip': TOOLTIPS.HEADER_BUTTONS_HANGAR},
        {'label': MENU.HEADERBUTTONS_STORAGE, 
            'value': baseSelf.TABS.STORAGE, 
            'tooltip': TOOLTIPS.HEADER_BUTTONS_STORAGE},
        {'label': MENU.HEADERBUTTONS_SHOP, 
            'value': baseSelf.TABS.STORE, 
            'tooltip': TOOLTIPS.HEADER_BUTTONS_SHOP},
        baseSelf._getPersonalMissionSelectorTabData()]
        tabDataProvider.append({'label': MENU.HEADERBUTTONS_PROFILE, 
        'value': baseSelf.TABS.PROFILE, 
        'tooltip': TOOLTIPS.HEADER_BUTTONS_PROFILE})
        techTreeData = {'label': MENU.HEADERBUTTONS_TECHTREE, 
        'value': baseSelf.TABS.TECHTREE, 
        'tooltip': TOOLTIPS.HEADER_BUTTONS_TECHTREE, 
        'isTooltipSpecial': False, 
        'subValues': [baseSelf.TABS.RESEARCH]}
        if baseSelf.techTreeEventsListener.actions:
            techTreeData['tooltip'] = TOOLTIPS_CONSTANTS.TECHTREE_DISCOUNT_INFO
            techTreeData['isTooltipSpecial'] = True
            if baseSelf.techTreeEventsListener.getNations(unviewed=True):
                techTreeData['actionIcon'] = backport.image(R.images.gui.maps.icons.library.discountIndicator())
        tabDataProvider.extend([techTreeData])
        tabDataProvider.extend([
        {'label': MENU.HEADERBUTTONS_BARRACKS, 
            'value': baseSelf.TABS.BARRACKS, 
            'tooltip': TOOLTIPS.HEADER_BUTTONS_BARRACKS}])
        tournamentsData = baseSelf._getTournamentsSelectorData()
        tournamentsData = None
        if tournamentsData is not None:
            tabDataProvider.append(tournamentsData)
        if CURRENT_REALM == 'RU':
            override = baseSelf._tutorialLoader.gui.lastHangarMenuButtonsOverride
            if override is not None:
                tabDataProvider[:] = filter(lambda item: item['value'] in override, tabDataProvider)
        return tabDataProvider

    def _DailyQuestWidget__show(self, base, baseSelf):
        base(baseSelf)
        baseSelf._DailyQuestWidget__hide()

    def _CachedBlur_enable(self, base, baseSelf):
        baseSelf._switchEnabled(False)

    def _LobbyHeader_as_updateOnlineCounterS(self, base, baseSelf, clusterStats, regionStats, tooltip, isAvailable):
        clusterUsers, regionUsers, _ = baseSelf.serverStats.getStats()
        clusterUsers = '%s / %s' % (clusterUsers, regionUsers)
        base(baseSelf, clusterUsers, '', None, isAvailable)

    def _LobbyHeader_populateButtons(self, base, baseSelf):
        if CURRENT_REALM == 'RU' and hasattr(self, '_tutorialLoader'):
            if baseSelf._tutorialLoader.gui.lastHeaderMenuButtonsOverride is not None:
                baseSelf._LobbyHeader__onOverrideHeaderMenuButtons()
                return
        else: pass

    def __removeClanIconFromMemory(self):
        if self.__clanIconID is not None:
            self.removeTextureFromMemory(self.__clanIconID)
            self.__clanIconID = None
        return

    def onClanEmblem32x32Received(self, _, emblem):
        self.flashObject.as_setClanEmblem(self.getMemoryTexturePath(emblem))

    def onClose(self):
        self.destroy()
        
    def pyLog(self, msg):
        print '[OMNILAB: LegacyLobbyHeader] %s' % (msg)

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