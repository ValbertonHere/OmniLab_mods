# Скрытие сервера.

from gui.Scaleform.daapi.view.meta.LobbyHeaderMeta import LobbyHeaderMeta
from gui.Scaleform.daapi.view.meta.IngameMenuMeta import IngameMenuMeta
from gui.shared.utils.functions import makeTooltip

def LobbyHeaderMeta_as_updateOnlineCounterS(self, clusterStats, regionStats, tooltip, isAvailable):
    base(self, 'No Server Info | © 2024 OmniLab R&D', '', makeTooltip('Я знал, что ты умудришься спалить сервер.', 'Именно поэтому я сделал эту подсказку.'), True)

def IngameMenu_as_setServerSettingS(self, serverName, tooltipFullData, state):
    base2(self, 'No Server Info | © 2024 OmniLab R&D', '', '')

def IngameMenu_as_setServerStatsS(self, stats, tooltipType):
    base3(self, 'No Server Info | © 2024 OmniLab R&D', 'unavailable')

base = LobbyHeaderMeta.as_updateOnlineCounterS
LobbyHeaderMeta.as_updateOnlineCounterS = LobbyHeaderMeta_as_updateOnlineCounterS
base2 = IngameMenuMeta.as_setServerSettingS
IngameMenuMeta.as_setServerSettingS = IngameMenu_as_setServerSettingS
base3 = IngameMenuMeta.as_setServerStatsS
IngameMenuMeta.as_setServerStatsS = IngameMenu_as_setServerStatsS