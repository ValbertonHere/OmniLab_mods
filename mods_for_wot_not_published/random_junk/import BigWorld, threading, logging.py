import BigWorld, threading, logging
from gui.Scaleform.framework import g_entitiesFactories
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
_logger = logging.getLogger(__name__)
_COSMIC_COMPONENTS_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.COSMIC_HUD,)), (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)), (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.COSMIC_HUD,))))

class ClassicCosmicPage(ClassicPage):

    def __init__(self):
        _logger.debug('CosmicPage.__init__')
        super(ClassicCosmicPage, self).__init__(components=_COSMIC_COMPONENTS_CONFIG, external=())

    def _onBattleLoadingStart(self):
        _logger.debug('CosmicPage._onBattleLoadingStart')

    def _addDefaultHitDirectionController(self, controllers):
        return controllers

    def _handleToggleFullStats(self, event):
        pass

    def _handleToggleFullStatsQuestProgress(self, event):
        pass

    def _handleToggleFullStatsPersonalReserves(self, event):
        pass

    def _handleRadialMenuCmd(self, event):
        pass

    def _changeCtrlMode(self, ctrlMode):
        _logger.info('CosmicPage._changeCtrlMode: %s', str(ctrlMode))

    def _canShowPostmortemTips(self):
        return False

    def _switchToPostmortem(self):
        pass

    def as_setPostmortemTipsVisibleS(self, value):
        pass

def checkSet():
    while g_entitiesFactories.getSettings(VIEW_ALIAS.COSMIC_BATTLE_PAGE) is None:
        continue
    else:
        replaceSet()

def replaceSet():
    replacedSet = g_entitiesFactories.getSettings(VIEW_ALIAS.COSMIC_BATTLE_PAGE).replaceSettings({'clazz': ClassicCosmicPage})
    g_entitiesFactories.removeSettings(VIEW_ALIAS.COSMIC_BATTLE_PAGE)
    g_entitiesFactories.addSettings(replacedSet)

thread = threading.Thread(target=checkSet)
thread.start()