# Анонимизатор боя.

import BigWorld
from ClientArena import ClientArena
from random import randint
from gui.Scaleform.daapi.view.battle_results_window import BattleResultsWindow

PLACEHOLDER_NAME = 'BattleUnit'

def ClientArena__vehicleInfoAsDict(self, info):
    if info[2] != BigWorld.player().name:
        return
    info = list(info)
    info[2] = PLACEHOLDER_NAME + str(randint(0, 20000))
    info[8] = ''
    return base(self, tuple(info))

def BattleResultsWindow_as_setData(self, battleResultsVO):
    battleResultsVO['common']['playerVehicles'][0]['vehicleStateStr'] = ''
    battleResultsVO['common']['playerVehicles'][0]['killerID'] = 0
    
    def fakeBattleUnit(unit):
        
        fakePlayerName = PLACEHOLDER_NAME + str(randint(0, 20000))
        
        if unit['userVO']['userName'] != BigWorld.player().name:
            unit['userVO']['userName'] = fakePlayerName
            unit['userVO']['fullName'] = fakePlayerName
            unit['userVO']['fakeName'] = fakePlayerName
            unit['userVO']['clanAbbrev'] = ''

        unit['killerFakeNameStr'] = fakePlayerName
        unit['killerRealNameStr'] = fakePlayerName
        unit['killerFullNameStr'] = fakePlayerName
        unit['killerClanNameStr'] = ''

    for player in battleResultsVO['team1']:
        fakeBattleUnit(player)
    for player in battleResultsVO['team2']:
        fakeBattleUnit(player)

    base2(self, battleResultsVO)

base = ClientArena._ClientArena__vehicleInfoAsDict
base2 = BattleResultsWindow.as_setData
ClientArena._ClientArena__vehicleInfoAsDict = ClientArena__vehicleInfoAsDict
BattleResultsWindow.as_setData = BattleResultsWindow_as_setData