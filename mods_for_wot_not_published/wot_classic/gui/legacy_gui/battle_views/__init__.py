from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates, ComponentSettings
from frameworks.wulf import WindowLayer

from LegacyPreBattleTimer import LegacyPreBattleTimer
from LegacyBattlePage import LegacyBattlePage

def getViewSettings():

    return [ViewSettings('LegacyBattlePageUI', LegacyBattlePage, 'legacyBattle.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
        ComponentSettings('LegacyPreBattleTimerUI', LegacyPreBattleTimer, ScopeTemplates.DEFAULT_SCOPE)]

for settings in getViewSettings():
    if settings is not None:
        g_entitiesFactories.addSettings(settings)

print '[OMNILAB R&D: battle_views.__init__] DONE!'