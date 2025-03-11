from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, GroupedViewSettings, ScopeTemplates
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.entities.abstract.AbstractPopOverView import AbstractPopOverView

class OmniSessionStatsPopover(AbstractPopOverView):

    def __init__(self, ctx=None):
        super(OmniSessionStatsPopover, self).__init__(ctx)
        return

popoverSettings = GroupedViewSettings('OmniSessionStatsPopoverUI', OmniSessionStatsPopover, 'omniSessionStats.swf', WindowLayer.WINDOW, 'OmniSessionStatsPopoverUI', 
                                      'OmniSessionStatsPopoverUI', ScopeTemplates.DEFAULT_SCOPE)

g_entitiesFactories.addSettings(popoverSettings)