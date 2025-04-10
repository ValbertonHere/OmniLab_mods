from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _BattleSelectorItems

def init_battle_types(self, items, extraItems=None):
    base(self, items, extraItems)
    for i in items:
        i.isDisabled = lambda: False
        i.isLocked = lambda: False
        i.isVisible = lambda: True

base = _BattleSelectorItems.__init__
_BattleSelectorItems.__init__ = init_battle_types