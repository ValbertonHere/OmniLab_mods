from cosmic_event.gui.Scaleform.daapi.view.battle.cosmic.battle_loading import CosmicBattleLoading
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from cosmic_event.gui.Scaleform.daapi.view.battle.cosmic.battle_loading import CosmicBattleLoading
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings

from cosmic_event.gui.Scaleform.daapi.view.battle import cosmic

from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

def _addEquipmentSlot(self, idx, intCD, item):
    base(self, idx, intCD, item)
    print idx, intCD, item

base = ConsumablesPanel._addEquipmentSlot
ConsumablesPanel._addEquipmentSlot = _addEquipmentSlot
ConsumablesPanel._getEquipmentIcon = lambda self, idx, item, icon: 'gui/maps/icons/artefacts/%s' % icon


def getViewSettings():
    from cosmic_event.gui.Scaleform.daapi.view.battle.cosmic import cosmic_hud
    from gui.Scaleform.daapi.view.battle.shared import battle_loading
    return (
     ViewSettings(VIEW_ALIAS.COSMIC_BATTLE_PAGE, ClassicPage, 'battlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.BattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.COSMIC_HUD, cosmic_hud.CosmicHud, ScopeTemplates.DEFAULT_SCOPE))

cosmic.getViewSettings = getViewSettings