from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from PlayerEvents import g_playerEvents

def guiOptimizationDiactivating(*args, **kwargs):
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    app.graphicsOptimizationManager.switchOptimizationEnabled(False)

g_playerEvents.onAccountShowGUI += guiOptimizationDiactivating