from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates, ComponentSettings
from frameworks.wulf import WindowLayer

from .bonds_window import BondsWindowUI
from .legacy_ammopanel import LegacyAmmoPanel
from .legacy_hangar import LegacyHangar
from .legacy_lobbyheader import LegacyLobbyHeader
from .legacy_research_panel import LegacyResearchPanel
from .personal_reserves import PersonalReservesComponent
from .technical_maintenance import TechnicalMaintenance

def getViewSettings():
    return [ViewSettings('LegacyLobbyHeaderUI', LegacyLobbyHeader, 'legacyLobbyHeader.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            ViewSettings('LegacyHangarUI', LegacyHangar, 'legacyHangar.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            ViewSettings('TechnicalMaintenance', TechnicalMaintenance, 'techMain.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            #ViewSettings('BondsWindowUI', BondsWindowUI, 'BondsWindowUI.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            ComponentSettings('LegacyAmmoPanelUI', LegacyAmmoPanel, ScopeTemplates.DEFAULT_SCOPE),
            ComponentSettings('PersonalReservesComponentUI', PersonalReservesComponent, ScopeTemplates.DEFAULT_SCOPE),
            ComponentSettings('LegacyResearchPanelUI', LegacyResearchPanel, ScopeTemplates.DEFAULT_SCOPE)]

for settings in getViewSettings():
    g_entitiesFactories.addSettings(settings)

print '[OMNILAB R&D: views.__init__] DONE!'