import BigWorld, json, os

from ResMgr import isDir
from gui.modsListApi import g_modsListApi
from gui.shared.utils.hangar_space_reloader import HangarSpaceReloader
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared.utils.hangar_space_reloader import HangarSpaceReloader
from gui import ClientHangarSpace, InputHandler, SystemMessages
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared.utils.key_mapping import getBigworldNameFromKey

class HookTestWindow(AbstractWindowView):

    def __init__(self):
        super(HookTestWindow, self).__init__()

    def _populate(self):
        super(HookTestWindow, self)._populate()

    def onWindowClose(self):
        self.destroy()
    
    def pyLog(self, msg):
        print msg

g_entitiesFactories.addSettings(ViewSettings('HookTestWindow', HookTestWindow, 'HookTestUI.swf', WindowLayer.WINDOW, None, ScopeTemplates.VIEW_SCOPE))


def onhandleKeyEvent(event):
    key = getBigworldNameFromKey(event.key)
    if key == 'KEY_F8':
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        app.loadView(SFViewLoadParams('HookTestWindow'))

InputHandler.g_instance.onKeyDown += onhandleKeyEvent