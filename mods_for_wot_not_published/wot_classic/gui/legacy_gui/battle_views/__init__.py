from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates, ComponentSettings
from frameworks.wulf import WindowLayer

from LegacyBattleTimer import LegacyBattleTimer
from LegacyBattlePage import LegacyBattlePage
from LegacyFragCorrelationBar import LegacyFragCorrelationBar
from LegacyPreBattleTimer import LegacyPreBattleTimer


def getViewSettings():

    return [ViewSettings('LegacyBattlePageUI', LegacyBattlePage, 'legacyBattle.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            ComponentSettings('LegacyBattleTimerUI', LegacyBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
            ComponentSettings('LegacyPreBattleTimerUI', LegacyPreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
            ComponentSettings('LegacyFragCorrelationBarUI', LegacyFragCorrelationBar, ScopeTemplates.DEFAULT_SCOPE)]

for settings in getViewSettings():
    if settings is not None:
        g_entitiesFactories.addSettings(settings)

print '[OMNILAB R&D: battle_views.__init__] DONE!'