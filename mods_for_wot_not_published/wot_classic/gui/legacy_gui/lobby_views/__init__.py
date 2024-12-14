import os, json

from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates, ComponentSettings
from frameworks.wulf import WindowLayer

def getGUIConfig(isEnabled=None):
    gui_config_file_path = 'mods/configs/wotclassic/gui_config.json'
    if os.path.isfile(gui_config_file_path):
        if isEnabled is not None:
            with open(gui_config_file_path, 'w') as f2w:
                gui_config['isLegacyLobbyHeaderEnabled'] = isEnabled
                json.dump(gui_config, f2w)
        else:
            with open(gui_config_file_path, 'r') as f2r:
                data = json.load(f2r)
                gui_config.update(data)
                return gui_config
    else:
        gui_config_folder_path = gui_config_file_path.replace('/gui_config.json', '')
        if not os.path.isdir(gui_config_folder_path):
            os.mkdir(gui_config_folder_path)
        gui_config_file = open(gui_config_file_path, 'w')
        json.dump(gui_config, gui_config_file)
        print '[OMNILAB R&D: views.__init__] GUI config file not found! Created and loaded default in "mods/configs/wotclassic".'
        return gui_config

gui_config = {
    'isLegacyLobbyHeaderEnabled': True
}

from .bonds_window import BondsWindowUI
from .legacy_ammopanel import LegacyAmmoPanel
from .legacy_hangar import LegacyHangar
from .legacy_research_panel import LegacyResearchPanel
from .personal_reserves import PersonalReservesComponent
from .technical_maintenance import TechnicalMaintenance

def getViewSettings():
    if getGUIConfig()['isLegacyLobbyHeaderEnabled']:
        from .legacy_lobbyheader import LegacyLobbyHeader
        legacyLobbyHeaderSettings = ViewSettings('LegacyLobbyHeaderUI', LegacyLobbyHeader, 'legacyLobbyHeader.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE)
    else: 
        legacyLobbyHeaderSettings = None

    return [ViewSettings('LegacyHangarUI', LegacyHangar, 'legacyHangar.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            ViewSettings('TechnicalMaintenance', TechnicalMaintenance, 'techMain.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            #ViewSettings('BondsWindowUI', BondsWindowUI, 'BondsWindowUI.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            ComponentSettings('LegacyAmmoPanelUI', LegacyAmmoPanel, ScopeTemplates.DEFAULT_SCOPE),
            ComponentSettings('PersonalReservesComponentUI', PersonalReservesComponent, ScopeTemplates.DEFAULT_SCOPE),
            ComponentSettings('LegacyResearchPanelUI', LegacyResearchPanel, ScopeTemplates.DEFAULT_SCOPE)] + [legacyLobbyHeaderSettings]

for settings in getViewSettings():
    if settings is not None:
        g_entitiesFactories.addSettings(settings)

print '[OMNILAB R&D: lobby_views.__init__] DONE!'