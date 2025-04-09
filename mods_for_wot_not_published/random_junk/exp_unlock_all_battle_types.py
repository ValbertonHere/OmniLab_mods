
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

appLoader = dependency.instance(IAppLoader)
lobby = appLoader.getDefLobbyApp()
if lobby and lobby.containerManager:
    view = lobby.containerManager.getView(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: 'hangar'})

for i in battle_selector_items.getItems().allItems:
    i.isDisabled = lambda: False
    i.isLocked = lambda: False
    i.isVisible = lambda: True