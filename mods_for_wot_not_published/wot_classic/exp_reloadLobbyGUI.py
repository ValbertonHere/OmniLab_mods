from skeletons.gui.shared.utils import IHangarSpace
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.prb_control.events_dispatcher import g_eventDispatcher
from frameworks.wulf import WindowLayer
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

appLoader = dependency.instance(IAppLoader)
hangarSpace = dependency.instance(IHangarSpace)
if hangarSpace.inited:
    lobby = appLoader.getDefLobbyApp()
    if lobby and lobby.containerManager:
        view = lobby.containerManager.getView(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_HANGAR})
        if view is not None:
            view.destroy()
        g_eventDispatcher.loadHangar()