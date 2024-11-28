from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

from .utils import override

@override(LobbyHeader, '_populate')
def _LobbyHeader_populate(base, self):
    base(self)
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    app.loadView(SFViewLoadParams('LegacyLobbyHeaderUI'))

@override(Hangar, '_populate')
def _Hangar__populate(base, self):
    base(self)
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    app.graphicsOptimizationManager.switchOptimizationEnabled(False)
    app.loadView(SFViewLoadParams('LegacyHangarUI'))