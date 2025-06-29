import game_loading_bindings, WWISE
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.login.LoginView import LoginView
from .wotc_legacyGLFlash import GameLoading

from gui.game_loading.state_machine.machine import GameLoadingStateMachine

class LegacyStateMachine(GameLoadingStateMachine):
    def configure(self, preferences, settings):
        super(LegacyStateMachine, self).configure(preferences, settings)
        print preferences, settings
        print '-------------------'


from gui.sounds.sound import Sound
from gui.game_loading.loading import *
_g_Loader = LegacyStateMachine()
from gui.game_loading.resources.cdn.cache import GameLoadingCdnCache
from gui.game_loading.resources.consts import Milestones
from gui.game_loading.state_machine.states.client_loading import ClientLoadingState, ClientLoadingProgressStateComponent
from gui.game_loading.state_machine.states.login_screen import LoginScreenState
from gui.game_loading.state_machine.states.player_loading import PlayerLoadingState

gameLoading = None
loginMusic = Sound('login_music_start')

def destroyLoadingView(milestone):
    if milestone == Milestones.HANGAR_SPACE and game_loading_bindings.isViewOpened():
        game_loading_bindings.destroyLoadingView(0.0)
        WWISE.WW_eventGlobal('login_music_stop')

def ClientLoadingState_onEntered(self):
    super(ClientLoadingState, self)._onEntered()
    global gameLoading

    gameLoading = GameLoading()
    game_loading_bindings.bringLoadingViewToBottom()

def ClientLoadingState_onExited(self):
    super(ClientLoadingState, self)._onExited()
    global gameLoading

    gameLoading.close()
    gameLoading = None

def LoginScreenState_onEntered(self):
    super(LoginScreenState, self)._onEntered()
    loginMusic.play()

def PlayerLoadingState_onEntered(self):
    super(PlayerLoadingState, self)._onEntered()
    game_loading_bindings.bringLoadingViewToBottom()
    if not loginMusic.isPlaying:
        loginMusic.play()

def ClientLoadingProgressStateComponent_setProgress(self, progress):
    CLPSC_base(self, progress)
    global gameLoading

    if gameLoading is not None:
        if round(progress/1024, 2) <= 0.93:
            gameLoading.setProgress(round(progress/1024, 2))

def LoginView_setVersionS(self, version):
    LVSVS_base(self, '#wek_gameLoading:game_version')

def GameLoadingStateMachine_configure(self, preferences, settings):
    GLSM_base(self, preferences, settings)
    

GLSM_base = getLoader().configure
CLPSC_base = ClientLoadingProgressStateComponent._setProgress
LVSVS_base = LoginView.as_setVersionS

ClientLoadingProgressStateComponent._setProgress = ClientLoadingProgressStateComponent_setProgress
LoginView.as_setVersionS = LoginView_setVersionS

ClientLoadingState._onEntered = ClientLoadingState_onEntered
ClientLoadingState._onExited = ClientLoadingState_onExited
LoginScreenState._onEntered = LoginScreenState_onEntered
PlayerLoadingState._onEntered = PlayerLoadingState_onEntered

def GameLoadingCdnCache__init__(self, defaults, externalConfigUrl=None, cohort=None):
    GameLoadingCdnCache._CACHE_DIR_NAME = 'wot_classic_game_loading_cache_mt'
    GLCC_base(self, defaults, 'https://raw.githubusercontent.com/FindMuck/WoT_Classic_config/main/config.json', cohort)

GLCC_base = GameLoadingCdnCache.__init__
GameLoadingCdnCache.__init__ = GameLoadingCdnCache__init__

g_playerEvents.onLoadingMilestoneReached += destroyLoadingView