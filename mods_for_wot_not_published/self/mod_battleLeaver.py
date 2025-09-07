import BigWorld, Keys

from gui import InputHandler
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency, isPlayerAvatar
from debug_utils import LOG_NOTE

class BattleLeaverWorker():
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        InputHandler.g_instance.onKeyDown += self._doLeaveBattle
        LOG_NOTE("Valberton's battle leaver - Leave from battle via hotkeys - Copyright (C) 2025 OmniLab R&D.")

    def _doLeaveBattle(self, event):
        if event.isKeyDown() and BigWorld.isKeyDown(Keys.KEY_NUMPAD5) and isPlayerAvatar():
            LOG_NOTE('Leaving from battle...')
            self.sessionProvider.exit()

g_battleLeaverWorker = BattleLeaverWorker()