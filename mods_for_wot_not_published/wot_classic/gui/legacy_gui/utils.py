import types
from helpers import dependency
from frameworks.wulf import WindowLayer

from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.prb_control.events_dispatcher import g_eventDispatcher

from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams

from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace


def override(holder, name, wrapper=None, setter=None):
    if wrapper is None:
        return lambda wrapper, setter=None: override(holder, name, wrapper, setter)
    target = getattr(holder, name)
    wrapped = lambda *a, **kw: wrapper(target, *a, **kw)
    if not isinstance(holder, types.ModuleType) and isinstance(target, types.FunctionType):
        setattr(holder, name, staticmethod(wrapped))
    elif isinstance(target, property):
        prop_getter = lambda *a, **kw: wrapper(target.fget, *a, **kw)
        prop_setter = target.fset if not setter else lambda *a, **kw: setter(target.fset, *a, **kw)
        setattr(holder, name, property(prop_getter, prop_setter, target.fdel))
    else:
        setattr(holder, name, wrapped)

def restartAllView():
    
    def __onLobbyLoaded(event):
        g_eventDispatcher.loadHangar()
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, __onLobbyLoaded)

    appLoader = dependency.instance(IAppLoader)
    lobby = appLoader.getDefLobbyApp()
    if lobby and lobby.containerManager:
        view = lobby.containerManager.getView(WindowLayer.VIEW)
        view.destroy()
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY)), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, __onLobbyLoaded)

def restartOnlyHangar():
    appLoader = dependency.instance(IAppLoader)
    hangarSpace = dependency.instance(IHangarSpace)
    if hangarSpace.inited:
        lobby = appLoader.getDefLobbyApp()
        if lobby and lobby.containerManager:
            view = lobby.containerManager.getView(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_HANGAR})
            if view is not None:
                view.destroy()
            g_eventDispatcher.loadHangar()
