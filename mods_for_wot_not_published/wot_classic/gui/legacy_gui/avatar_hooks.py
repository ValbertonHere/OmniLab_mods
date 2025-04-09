from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from battle_royale.gui.Scaleform.daapi.view.battle.respawn_message_panel import RespawnMessagePanel
from .utils import override

class PreBattleTimerHooks():
    appLoader = dependency.instance(IAppLoader)

    def __init__(self):
        override(SharedPage, '_populate', self._SharedPage__populate)
        override(SharedPage, '_onRegisterFlashComponent', self._SharedPage__onRegisterFlashComponent)
        
    def _SharedPage__populate(self, base, baseSelf):
        base(baseSelf)

        app = self.appLoader.getApp()
        app.loadView(SFViewLoadParams('LegacyBattlePageUI'))

    def _SharedPage__onRegisterFlashComponent(self, base, baseSelf, viewPy, alias):
        if alias in (BATTLE_VIEW_ALIASES.BATTLE_TIMER, BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR):
            viewPy.flashObject.visible = False
        base(baseSelf, viewPy, alias)
    
g_prbTimerHooks = PreBattleTimerHooks()