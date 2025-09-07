from frameworks.wulf import WindowLayer
from gui import InputHandler
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.shared.utils.key_mapping import getBigworldNameFromKey
from gui.shared.personality import ServicesLocator
from gui.app_loader.settings import APP_NAME_SPACE

class TestWindow(AbstractWindowView):

    def __init__(self):
        super(TestWindow, self).__init__()

    def _populate(self):
        super(TestWindow, self)._populate()

    def onWindowClose(self):
        self.destroy()
    
    def onClicked(self):
        app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
        app.loadView(SFViewLoadParams("OmniSessionStatsPopoverUI"))

g_entitiesFactories.addSettings(ViewSettings('TestWindow', TestWindow, 'TestWindowUI.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE))

def onhandleKeyEvent(event):
    key = getBigworldNameFromKey(event.key)
    if key == 'KEY_F9':
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        app.loadView(SFViewLoadParams('TestWindow'))

InputHandler.g_instance.onKeyDown += onhandleKeyEvent