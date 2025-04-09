from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, GroupedViewSettings, ScopeTemplates
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.entities.abstract.AbstractPopOverView import AbstractPopOverView
from gui.shared.personality import ServicesLocator
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class OLPopOverTest(AbstractPopOverView):

    def _populate(self):
        super(OLPopOverTest, self)._populate()

    def _dispose(self):
        super(OLPopOverTest, self)._dispose()

popoverSettings = GroupedViewSettings('OLPopOverTest', OLPopOverTest, 'OLPopOverTest.swf',
    WindowLayer.WINDOW, 'OLPopOverTest', 'OLPopOverTest',
    ScopeTemplates.DEFAULT_SCOPE)

g_entitiesFactories.addSettings(popoverSettings)