# Помощник для УГВ.

# Импорты модулей
import SoundGroups
import BigWorld
import nations
import WWISE

from gui import InputHandler
from gui import SystemMessages
from Avatar import PlayerAvatar
from PlayerEvents import g_playerEvents
from CurrentVehicle import g_currentVehicle
from gui.shared.personality import ServicesLocator
from skeletons.gui.app_loader import GuiGlobalSpaceID
from gui.shared.utils.key_mapping import getBigworldNameFromKey
from gui.IngameSoundNotifications import ComplexSoundNotifications
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AmmoPlugin
from gui.battle_control.battle_constants import VEHICLE_GUI_ITEMS, VEHICLE_VIEW_STATE


# Класс констант мода
class WTSM_CONSTS():

    IN_DEV = True
    BUILD = '1223/2'
    VERSION = 'Release 9'
    UPD_NAME = 'Точка кипения'
    DIST_VALUES = [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1100, 1200, 1300]
    A2H = {0: '12h', 30: '1h', 60: '2h', 90: '3h', 120: '4h', 150: '5h', 180: '6h', 210: '7h', 240: '8h', 270: '9h', 300: '10h', 330: '11h', 360: '12h'}

    VEH_STATES = [
        VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY,
        VEHICLE_VIEW_STATE.DEVICES,
        VEHICLE_VIEW_STATE.HEALTH,
        VEHICLE_VIEW_STATE.REPAIRING
    ]

    RTPCS = [
        'RTPC_WT_WoTA_shot_sideChain',
        'RTPC_WT_WoTA_expl_sideChain',
        'RTPC_WT_WoTA_horiz_sideChain',
        'RTPC_WT_WoTA_imp_pc_sideChain',
        'RTPC_WT_WoTA_hanmusic_sideChain'
    ]

    SWITCHES = {
        'nation': 'SWITCH_nationtype',
        'target_distance': 'SWITCH_target_distance',
        'target_hours': 'SWITCH_target_radial_hours',
        'battle_status': 'SWITCH_battle_status',
        'shell_loaded': 'SWITCH_shell_loaded'
    }


# Класс реализации дополнительных голосовых и звуковых уведомлений в очередь основных и прочего
class WTSoundsStuff():

    def __init__(self, name, chance='100', priority='50', predelay='0', lifetime='5'):
        self.name = name
        self.chance = chance
        self.predelay = predelay
        self.priority = priority
        self.lifetime = lifetime

    def addSoundNotification(self):
        wt_event = {
            'name': self.name,
            'infChance': self.chance,
            'predelay': self.predelay,
            'priority': self.priority,
            'lifetime': self.lifetime,
            'infEvent': 'vo_' + self.name,
            'queue': '1',
            'chance': '100',
            'interrupt': '0',
            'cooldownEvent': '0',
            'queueClearAtStart': '0'
        }
        BigWorld.player().soundNotifications._IngameSoundNotifications__events[wt_event['name']] = wt_event
        inDevLog('Event %s added to IngameSoundNotifications!' % wt_event['name'])

    @staticmethod
    def setVehicleNation():
        if isinstance(BigWorld.player(), PlayerAvatar):
            for nationName, nationID in nations.INDICES.items():
                if nationID == BigWorld.player().vehicle.typeDescriptor.type.id[0]:
                    playerNation = nationName
                    break
        else:
            vehicle = g_currentVehicle.item
            if vehicle is not None:
                playerNation = vehicle.nationName

        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['nation'], playerNation)

    @staticmethod
    def updateVehicleState(state, value):
        if state in WTSM_CONSTS.VEH_STATES:
            global cb_active, isLTrackDestroyed, isRTrackDestroyed

            if state == VEHICLE_VIEW_STATE.DEVICES and value[1] != 'normal':
                if value[0].startswith('wheel'):
                    BigWorld.player().soundNotifications.play('wt_wheelHit')
                elif value[0] in ('leftTrack0', 'leftTrack1') and not isLTrackDestroyed:
                    BigWorld.player().soundNotifications.play('wt_leftTrackHit')
                elif value[0] in ('rightTrack0', 'rightTrack1') and not isRTrackDestroyed:
                    BigWorld.player().soundNotifications.play('wt_rightTrackHit')
            elif state == VEHICLE_VIEW_STATE.DEVICES and value[1] == 'normal':
                if value[0].startswith('wheel'):
                    BigWorld.player().soundNotifications.play('wt_wheelRepaired')
                elif value[0] in ('leftTrack0', 'leftTrack1'):
                    isLTrackDestroyed = False
                elif value[0] in ('rightTrack0', 'rightTrack1'):
                    isRTrackDestroyed = False

            if state == VEHICLE_VIEW_STATE.REPAIRING:
                if value[0] in ('leftTrack0', 'leftTrack1'):
                    isLTrackDestroyed = True
                elif value[0] in ('rightTrack0', 'rightTrack1'):
                    isRTrackDestroyed = True

            if cb_active:
                return

            WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'combat')
            BigWorld.callback(30, WTSoundsStuff.setBattleStatusSwitch)
            cb_active = True

    @staticmethod
    def isLMBDown(event):
        if isinstance(BigWorld.player(), PlayerAvatar):
            key = getBigworldNameFromKey(event.key)
            if key == 'KEY_MOUSE0':
                reloadTimeLeft = BigWorld.player().guiSessionProvider.shared.ammo.getGunReloadingState().getTimeLeft()
                isReloading = BigWorld.player().guiSessionProvider.shared.ammo.getGunReloadingState().isReloading()
                if isReloading and reloadTimeLeft <= 1.0 and not BigWorld.player().soundNotifications.isPlaying('wt_shootVoice'):
                    BigWorld.player().soundNotifications.play('wt_shootVoice')

    @staticmethod
    def setBattleStatusSwitch():
        global cb_active

        if 100 * BigWorld.player().vehicle.health / BigWorld.player().vehicle.maxHealth > 35:
            WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'exploring')
            cb_active = False

    @staticmethod
    def playBattleMusic():
        SoundGroups.g_instance.playSound2D('wt_battle_music')

    @staticmethod
    def UPDVehState_init():
        ctrl = BigWorld.player().guiSessionProvider.shared.vehicleState
        ctrl.onVehicleStateUpdated += WTSoundsStuff.updateVehicleState

    # @staticmethod
    # def getHoursFromAngle(angle):
    #     return WTSM_CONSTS.A2H[min(sorted(WTSM_CONSTS.A2H.keys()), key=lambda x: abs(x-angle))]

    @staticmethod
    def setRTPC(name, value):
        WWISE.WW_setRTCPGlobal(name, value)
        inDevLog('Value of %s has been set to %s.' % (name, value))

    @staticmethod
    def setState(name, value):
        WWISE.WW_setState(name, '%s_%s' % (name, value))
        inDevLog('Value of %s has been set to %s.' % (name, value))

    @staticmethod
    def setSwitch(group, switch):
        WWISE.WW_setSwitch(group, '%s_%s' % (group, switch))
        inDevLog('Value of %s has been set to %s.' % (group, switch))


# Вывод всяких сообщений в python.log для отладки
def inDevLog(message):
    if WTSM_CONSTS.IN_DEV:
        print '[OMNILAB: WTSM] %s' % (message)
    else: pass

# Добавление дополнительных звуковых уведомлений
def addSoundNotifications():
    WTSoundsStuff('wt_battleWon').addSoundNotification()
    WTSoundsStuff('wt_battleLose').addSoundNotification()
    WTSoundsStuff('wt_battleState').addSoundNotification()
    WTSoundsStuff('wt_leftTrackHit').addSoundNotification()
    WTSoundsStuff('wt_rightTrackHit').addSoundNotification()
    WTSoundsStuff('wt_wheelHit', lifetime='0.5').addSoundNotification()
    WTSoundsStuff('wt_shootVoice', lifetime='1.2').addSoundNotification()
    WTSoundsStuff('wt_wheelRepaired', lifetime='0.5').addSoundNotification()
    WTSoundsStuff('wt_gunReloaded', chance='5', lifetime='1').addSoundNotification()
    WTSoundsStuff('wt_weveBeenHit', chance='15', lifetime='1').addSoundNotification()
    WTSoundsStuff('wt_artWarning', predelay='0.5', lifetime='2').addSoundNotification()

# PLACEHOLDER: Получаем дистанции и угол до захваченной цели и переводим в смену свитчей в Wwise
# def wtGetDistanceAndAngle(self, target, magnetic, *args, **kwargs):
    # h_autoAim(self, target, magnetic)
    # if target is not None:
        # dist = avatar_getter.getDistanceToTarget(target)
        # if dist < WTSM_CONSTS.DIST_VALUES[0]:
            # corr_dist = 'near'
        # else:
            # corr_dist = min(WTSM_CONSTS.DIST_VALUES, key=lambda x: abs(x-dist))

        # angle = 'placeholder'

        # WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['target_distance'], corr_dist)
        # WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['target_hours'], WTSoundsStuff.getHoursFromAngle(angle))

# Реализация предупреждения огня арты на игрока
def wtVOArtWarning(self, distToTarget, shooterPosition):
    hookSPGnoti(self, distToTarget, shooterPosition)
    if isinstance(BigWorld.player(), PlayerAvatar):
        BigWorld.player().soundNotifications.play('wt_artWarning')

def onGunReloadTimeSet(self, _, state, skipAutoLoader):
    h_onGunReloadTimeSet(self, _, state, skipAutoLoader)
    isAutoReload = self._AmmoPlugin__guiSettings.hasAutoReload
    isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
    timeLast = state.getActualValue()
    timeLeft = state.getTimeLeft()
    if timeLeft == 0.0 and not isAutoReload and not isInPostmortem and (timeLast != -1):
        shellKind = BigWorld.player().vehicle.typeDescriptor.getShot().shell.kind
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['shell_loaded'], shellKind)
        BigWorld.player().soundNotifications.play('wt_gunReloaded')

def onGunAutoReloadTimeSet(self, state, stunned):
    h_onGunAutoReloadTimeSet(self, state, stunned)
    isAutoReload = self._AmmoPlugin__guiSettings.hasAutoReload
    isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
    timeLast = state.getActualValue()
    timeLeft = state.getTimeLeft()
    if timeLeft == 0.0 and not isAutoReload and not isInPostmortem and (timeLast != -1):
        shellKind = BigWorld.player().vehicle.typeDescriptor.getShot().shell.kind
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['shell_loaded'], shellKind)
        BigWorld.player().soundNotifications.play('wt_gunReloaded')

# Реализация вызова музыки победы/поражения в конце боя (при появлении надписи "ПОБЕДА" или "ПОРАЖЕНИЕ")
def wtWinLoseMusic(winnerTeam, *args, **kwargs):
    if winnerTeam == BigWorld.player().team:
        SoundGroups.g_instance.playSound2D('wt_win_music')
        BigWorld.player().soundNotifications.play('wt_battleWon')
    else:
        SoundGroups.g_instance.playSound2D('wt_lose_music')
        BigWorld.player().soundNotifications.play('wt_battleLose')

def onGUISpaceEntered(spaceID, *args, **kwargs):
    if spaceID != GuiGlobalSpaceID.LOBBY:
        return
    
    global welcomeMessageSeen
    
    g_currentVehicle.onChanged += WTSoundsStuff.setVehicleNation
    if not welcomeMessageSeen:
        SystemMessages.pushMessage('Вспомогательный скрипт загружен.<br>Необходимые параметры были применены.<br><br>Build %s' % WTSM_CONSTS.BUILD,
            SystemMessages.SM_TYPE.InformationHeader,
            priority=True,
            messageData={'header': 'Унесённый громом войны<br>%s - "%s"' % (WTSM_CONSTS.VERSION, WTSM_CONSTS.UPD_NAME)})
        welcomeMessageSeen = True

welcomeMessageSeen = False
isLTrackDestroyed = False
isRTrackDestroyed = False
cb_active = False

print '[OMNILAB: WTSM] INIT START!'

# Сброс параметров сайдчейнов Wwise
inDevLog('Reset RTPCs - Start')

for rtpc in WTSM_CONSTS.RTPCS:
    WTSoundsStuff.setRTPC(rtpc, -48)

inDevLog('Reset RTPCs - End')

# Хуки функций
inDevLog('Hook functions - Start')

hookSPGnoti = ComplexSoundNotifications.notifyEnemySPGShotSound
ComplexSoundNotifications.notifyEnemySPGShotSound = wtVOArtWarning

h_onGunReloadTimeSet = AmmoPlugin._AmmoPlugin__onGunReloadTimeSet
AmmoPlugin._AmmoPlugin__onGunReloadTimeSet = onGunReloadTimeSet

h_onGunAutoReloadTimeSet = AmmoPlugin._AmmoPlugin__onGunAutoReloadTimeSet
AmmoPlugin._AmmoPlugin__onGunAutoReloadTimeSet = onGunAutoReloadTimeSet

inDevLog('Hook functions - End')

# Привязка к ивентам клиента
inDevLog('Add to game events - Start')

g_playerEvents.onRoundFinished += wtWinLoseMusic
g_playerEvents.onAvatarObserverVehicleChanged += WTSoundsStuff.setVehicleNation
g_playerEvents.onAvatarReady += addSoundNotifications
g_playerEvents.onAvatarReady += WTSoundsStuff.setVehicleNation
g_playerEvents.onAvatarReady += WTSoundsStuff.setBattleStatusSwitch
g_playerEvents.onAvatarReady += WTSoundsStuff.UPDVehState_init
g_playerEvents.onAvatarReady += WTSoundsStuff.playBattleMusic
ServicesLocator.appLoader.onGUISpaceEntered += onGUISpaceEntered
InputHandler.g_instance.onKeyDown += WTSoundsStuff.isLMBDown

inDevLog('Add to game events - End')


print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'
print 'War Thunder Sound Mod for World of Tanks/Mir Tankov: %s (Build %s). Python Helper executed!' % (WTSM_CONSTS.VERSION, WTSM_CONSTS.BUILD)
print 'Copyright (C) 2023 OmniLab R&D.'
print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'