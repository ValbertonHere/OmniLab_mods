from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates, ComponentSettings
from frameworks.wulf import WindowLayer

from .userCustomizationSerialNumberView import UserCustomizationSerialNumberView
from .userCustomizationWindow import UserCustomizationWindow
from .userCustomizationView import UserCustomizationView

def getViewSettings():
    return [ViewSettings('UserCustomizationWindowUI', UserCustomizationWindow, 'userCustomizationWindow.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            ViewSettings('UserCustomizationSerialNumberViewUI', UserCustomizationSerialNumberView, 'userCustomizationSerialNumberView.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.VIEW_SCOPE),
            ComponentSettings('UserCustomizationViewUI', UserCustomizationView, ScopeTemplates.DEFAULT_SCOPE),]

for settings in getViewSettings():
    if settings is not None:
        g_entitiesFactories.addSettings(settings)