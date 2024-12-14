from gui import InputHandler
from helpers import dependency

from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams

from gui.shared.utils.key_mapping import getBigworldNameFromKey

from skeletons.gui.app_loader import IAppLoader

class BondsWindowUI(AbstractWindowView):

    def __init__(self):
        super(BondsWindowUI, self).__init__()

    def _populate(self):
        super(BondsWindowUI, self)._populate()

    def onWindowClose(self):
        self.destroy()

def onhandleKeyEvent(event):
    key = getBigworldNameFromKey(event.key)
    if key == 'KEY_F8':
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        app.loadView(SFViewLoadParams('BondsWindowUI'))

InputHandler.g_instance.onKeyDown += onhandleKeyEvent

print '[OMNILAB R&D: views.BoundsWindowUI] INITIALIZED!'