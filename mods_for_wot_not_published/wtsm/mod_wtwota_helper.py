# Помощник для УГВ (устарело).

import BigWorld
import WWISE
import nations
from Account import Account
from gui import SystemMessages
from Avatar import PlayerAvatar
from constants import ARENA_PERIOD
from PlayerEvents import g_playerEvents
from CurrentVehicle import g_currentVehicle
from gui.shared.personality import ServicesLocator
from skeletons.gui.app_loader import GuiGlobalSpaceID

nationsDict = nations.INDICES.items()
isPreBattle = None
isBattle = None
h_onBecomePlayer = Account.onBecomePlayer
h_onAppearanceReady = PlayerAvatar.vehicle_onAppearanceReady
wtwota_version = 'Release 8'
wtwota_fullver = 'Вариативность бытия'
wtwota_build = 'Build 1022/4'


def wwSetRTPC(name, value):
    WWISE.WW_setRTCPGlobal(name, value)
    print '[VLBRTN] [WT_WOTA] Value of %s has been set to %s' % (name, value)


def wwSetState(name, value):
    WWISE.WW_setState(name, value)
    print '[VLBRTN] [WT_WOTA] Value of %s has been set to %s' % (name, value)


def wwSetSwitch(group, switch):
    WWISE.WW_setSwitch(group, switch)
    print '[VLBRTN] [WT_WOTA] Value of %s has been set to %s' % (group, switch)


def onVehicleChanged():
    vehicle = g_currentVehicle.item
    if vehicle is not None:
        print '[VLBRTN] [WT_WOTA] Vehicle nation detected - %s' % vehicle.nationName
        vehnation = vehicle.nationName
        wwSetSwitch('SWITCH_nationtype', 'SWITCH_nationtype_%s' % vehnation)


def setVehInBattleNation(playerNationID):
    for item in nationsDict:
        if item[1] == playerNationID:
            wwSetSwitch('SWITCH_nationtype', 'SWITCH_nationtype_%s' % item[0])


def getBattlePeriod(period, *args):
    global isBattle
    global isPreBattle
    if period == ARENA_PERIOD.PREBATTLE:
        isPreBattle = True
    elif period == ARENA_PERIOD.BATTLE:
        isBattle = True
    else:
        isPreBattle = False
        isBattle = False


def n_onAppearenceReady(self, appearence):
    h_onAppearanceReady(self, appearence)
    if isBattle or isPreBattle:
        vehID = appearence.id
        playerVehID = BigWorld.player().playerVehicleID
        playerNationID = BigWorld.player().vehicle.typeDescriptor.type.id[0]
        if vehID == playerVehID:
            setVehInBattleNation(playerNationID)


def onGUISpaceEntered(spaceID, *args, **kwargs):
    if spaceID != GuiGlobalSpaceID.LOBBY:
        return

    g_currentVehicle.onChanged += onVehicleChanged


def n_onBecomePlayer(self):
    h_onBecomePlayer(self)
    SystemMessages.pushMessage('Вспомогательный скрипт загружен.<br>Необходимые параметры были сброшены.<br><br>%s' % wtwota_build,
                               SystemMessages.SM_TYPE.InformationHeader,
                               priority=True,
                               messageData={'header': 'Унесённый громом войны<br>%s - "%s"' % (wtwota_version, wtwota_fullver)})
    Account.onBecomePlayer = h_onBecomePlayer


print '---------------------'
print '[VLBRTN] [WT_WOTA] Initialization successfull! War Thunder - World of Tanks Adaptation: %s (%s). Python Helper executed!' % (wtwota_version, wtwota_build)
print '[VLBRTN] [WT_WOTA] Copyright (C) VLBRTN Community.'
print '[VLBRTN] [WT_WOTA] Licensed by WTFPLv2 Public Licence.'
print '---------------------'

wwSetRTPC('RTPC_WT_WoTA_shot_sideChain', -48)
wwSetRTPC('RTPC_WT_WoTA_horiz_sideChain', -48)
wwSetRTPC('RTPC_WT_WoTA_expl_sideChain', -48)
wwSetRTPC('RTPC_WT_WoTA_hanmusic_sideChain', -48)
wwSetRTPC('RTPC_WT_WoTA_imp_pc_sideChain', -48)

PlayerAvatar.vehicle_onAppearanceReady = n_onAppearenceReady
Account.onBecomePlayer = n_onBecomePlayer
ServicesLocator.appLoader.onGUISpaceEntered += onGUISpaceEntered
g_playerEvents.onArenaPeriodChange += getBattlePeriod