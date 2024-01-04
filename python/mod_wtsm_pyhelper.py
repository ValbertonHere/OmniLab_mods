# Помощник для УГВ.

# Импорты модулей
import SoundGroups
import BigWorld
import nations
import WWISE

from OpenModsCore import overrideMethod

from random import randint
from gui import InputHandler
from gui import SystemMessages
from Avatar import PlayerAvatar
from constants import ARENA_PERIOD
from PlayerEvents import g_playerEvents
from CurrentVehicle import g_currentVehicle
from gui.shared.personality import ServicesLocator
from skeletons.gui.app_loader import GuiGlobalSpaceID
from gui.shared.utils.key_mapping import getBigworldNameFromKey
from gui.IngameSoundNotifications import ComplexSoundNotifications
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AmmoPlugin

# Класс констант мода
class WTSM_CONSTS():

    IN_DEV = True
    BUILD = '0124/3'
    VERSION = 'Release 9'
    UPD_NAME = 'Точка кипения'
    DIST_VALUES = [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1100, 1200, 1300]
    A2H = {0: '12h', 30: '1h', 60: '2h', 90: '3h', 120: '4h', 150: '5h', 180: '6h', 210: '7h', 240: '8h', 270: '9h', 300: '10h', 330: '11h', 360: '12h'}

    DEVICE_CRIT_CODES = {
        'DEVICE_CRITICAL',
        'DEVICE_CRITICAL_AT_SHOT',
        'DEVICE_CRITICAL_AT_RAMMING',
        'DEVICE_CRITICAL_AT_FIRE',
        'DEVICE_CRITICAL_AT_WORLD_COLLISION',
        'DEVICE_CRITICAL_AT_DROWNING'
    }
       
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
        'shell_loaded': 'SWITCH_shell_loaded',
        'shell_prepared': 'SWITCH_shell_prepared',
        'team_correlation': 'SWITCH_team_correlation'
    }



# Класс реализации дополнительных голосовых и звуковых уведомлений в очередь основных и прочего
class WTSoundsStuff():
    
    def __init__(self, name, fxEvent='null', chance='100', priority='50', predelay='0', lifetime='5'):
        self.name = name
        self.chance = chance
        self.predelay = predelay
        self.priority = priority
        self.lifetime = lifetime
        self.fxEvent = fxEvent

    def addSoundNotification(self):
        wt_event = {
            'name': self.name,
            'infChance': self.chance,
            'predelay': self.predelay,
            'priority': self.priority,
            'lifetime': self.lifetime,
            'infEvent': 'vo_' + self.name,
            'fxEvent': self.fxEvent,
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
    def onHealthChanged(attackedID, *args, **kwargs):
        global cb_active

        if cb_active:
            return
        
        if attackedID == BigWorld.player():
            BigWorld.player().soundNotifications.play('wt_weveBeenHit')
            WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'combat')
            BigWorld.callback(30, WTSoundsStuff.setBattleStatusSwitch)
            cb_active = True
 
    @staticmethod
    def teamCorrelationVO():
        global alive_allies, aiive_enemies, tcvo_callback

        alive_allies = 0
        aiive_enemies = 0
        timer = randint(60, 300)
        player_name = BigWorld.player().team
        arena_vehicles = BigWorld.player().arena.vehicles
        
        for vehicle in arena_vehicles:
            if arena_vehicles[vehicle]['isAlive'] == 1 and arena_vehicles[vehicle]['team'] == player_name:
                alive_allies += 1
            elif arena_vehicles[vehicle]['isAlive'] == 1 and arena_vehicles[vehicle]['team'] != player_name:
                aiive_enemies += 1
        
        inDevLog('Alive allies: %s, alive enemies: %s' % (alive_allies, aiive_enemies))

        if alive_allies > aiive_enemies and aiive_enemies <= 3:
            BigWorld.player().soundNotifications.play('wt_allyDominating')
        elif  alive_allies < aiive_enemies and alive_allies <= 3:
            BigWorld.player().soundNotifications.play('wt_enemyDominating')
        elif alive_allies < aiive_enemies:
            BigWorld.player().soundNotifications.play('wt_enemyWinning')
        elif alive_allies > aiive_enemies:
            BigWorld.player().soundNotifications.play('wt_allyWinning')
        
        tcvo_callback = BigWorld.callback(timer, WTSoundsStuff.teamCorrelationVO)
        inDevLog('TeamCorrelationVO callback set to %s seconds. CallbackID is %s' % (timer, tcvo_callback))

    @staticmethod
    def shellChangeVO(shellID):
        nextShellKind = BigWorld.player().guiSessionProvider.shared.ammo.getGunSettings().getShellDescriptor(shellID).kind
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['shell_prepared'], nextShellKind)
        BigWorld.player().soundNotifications.play('wt_prepareShell')

    @staticmethod
    def lmbDownEvent(event):
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

        if isinstance(BigWorld.player(), PlayerAvatar):
            if 100 * BigWorld.player().vehicle.health / BigWorld.player().vehicle.maxHealth > 35:
                WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'exploring')
                cb_active = False
    
    @staticmethod
    def playBattleMusic():
        BigWorld.player().guiSessionProvider.shared.ammo.onNextShellChanged += WTSoundsStuff.shellChangeVO
        SoundGroups.g_instance.playSound2D('wt_battle_music')

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

@overrideMethod(PlayerAvatar, 'onObservedByEnemy')
def onObservedByEnemy(base, self, vehicleID):
    base(self, vehicleID)
    global cb_active
    
    if cb_active:
        return
    
    WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'combat')
    BigWorld.callback(30, WTSoundsStuff.setBattleStatusSwitch)
    cb_active = True

@overrideMethod(PlayerAvatar, '__showDamageIconAndPlaySound')
def devicesVO(base, self, damageCode, extra, *args, **kwargs):
    base(self, damageCode, extra, *args, **kwargs)
    global cb_active

    if damageCode not in ('DEVICE_REPAIRED', 'DEVICE_REPAIRED_TO_CRITICAL'):
        BigWorld.player().soundNotifications.play('wt_weveBeenHit')
    if damageCode in WTSM_CONSTS.DEVICE_CRIT_CODES:
        if extra.name[:-len('Health')] in ('leftTrack0', 'leftTrack1'):
            BigWorld.player().soundNotifications.play('wt_leftTrackHit')
        elif extra.name[:-len('Health')] in ('rightTrack0', 'rightTrack1'):
            BigWorld.player().soundNotifications.play('wt_rightTrackHit')
        elif extra.name[:-len('Health')].startswith('wheel'):
            BigWorld.player().soundNotifications.play('wt_wheelHit')
    
    if damageCode == 'DEVICE_REPAIRED' and extra.name[:-len('Health')].startswith('wheel'):
        BigWorld.player().soundNotifications.play('wt_wheelRepaired')
    if cb_active:
        return
    
    WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'combat')
    BigWorld.callback(30, WTSoundsStuff.setBattleStatusSwitch)
    cb_active = True

# Реализация предупреждения огня арты на игрока
@overrideMethod(ComplexSoundNotifications, 'notifyEnemySPGShotSound')
def wtVOArtWarning(base, self, distToTarget, shooterPosition):
    base(self, distToTarget, shooterPosition)
    if isinstance(BigWorld.player(), PlayerAvatar):
        BigWorld.player().soundNotifications.play('wt_artWarning')

@overrideMethod(AmmoPlugin, '__onGunReloadTimeSet')
def wtVOGunReloaded(base, self, _, state, skipAutoLoader):
    base(self, _, state, skipAutoLoader)
    isAutoReload = self._AmmoPlugin__guiSettings.hasAutoReload
    isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
    timeLast = state.getActualValue()
    timeLeft = state.getTimeLeft()
    if timeLeft == 0.0 and not isAutoReload and not isInPostmortem and (timeLast != -1):
        shellKind = BigWorld.player().vehicle.typeDescriptor.getShot().shell.kind
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['shell_loaded'], shellKind)
        BigWorld.player().soundNotifications.play('wt_gunReloaded')

@overrideMethod(AmmoPlugin, '__onGunAutoReloadTimeSet')
def wtVOGunReloaded_auto(base, self, state, stunned):
    base(self, state, stunned)
    isAutoReload = self._AmmoPlugin__guiSettings.hasAutoReload
    isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
    timeLast = state.getActualValue()
    timeLeft = state.getTimeLeft()
    if timeLeft == 0.0 and not isAutoReload and not isInPostmortem and (timeLast != -1):
        shellKind = BigWorld.player().vehicle.typeDescriptor.getShot().shell.kind
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['shell_loaded'], shellKind)
        BigWorld.player().soundNotifications.play('wt_gunReloaded')

# Реализация вызова музыки победы/поражения в конце боя (при появлении надписи "ПОБЕДА" или "ПОРАЖЕНИЕ")
def wtBattleResult(winnerTeam, *args, **kwargs):
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
    
    try:
        BigWorld.cancelCallback(tcvo_callback)
    except:
        inDevLog('No Callback found')
    
    SoundGroups.g_instance.playSound2D('mt_hangar_music_stop')
    SoundGroups.g_instance.playSound2D('wt_hangar_music')

# Добавление дополнительных звуковых уведомлений
def addSoundNotifications():
    WTSoundsStuff('wt_battleWon').addSoundNotification()
    WTSoundsStuff('wt_battleLose').addSoundNotification()
    WTSoundsStuff('wt_battleState').addSoundNotification()
    WTSoundsStuff('wt_allyWinning').addSoundNotification()
    WTSoundsStuff('wt_enemyWinning').addSoundNotification()
    WTSoundsStuff('wt_leftTrackHit').addSoundNotification()
    WTSoundsStuff('wt_rightTrackHit').addSoundNotification()
    WTSoundsStuff('wt_allyDominating').addSoundNotification()
    WTSoundsStuff('wt_enemyDominating').addSoundNotification()
    WTSoundsStuff('wt_wheelHit', lifetime='0.5').addSoundNotification()
    WTSoundsStuff('wt_shootVoice', lifetime='1.2').addSoundNotification()
    WTSoundsStuff('wt_wheelRepaired', lifetime='0.5').addSoundNotification()
    WTSoundsStuff('wt_gunReloaded', chance='5', lifetime='0').addSoundNotification()
    WTSoundsStuff('wt_weveBeenHit', chance='10', lifetime='0').addSoundNotification()
    WTSoundsStuff('wt_artWarning', predelay='0.5', lifetime='2').addSoundNotification()
    WTSoundsStuff('wt_prepareShell', fxEvent='load_shell_fx', lifetime='0').addSoundNotification()


ally_frags = 0
enemy_frags = 0
ally_vehicles = 0
enemy_vehicles = 0
cb_active = False
tcvo_callback = None
isLTrackDestroyed = False
isRTrackDestroyed = False
welcomeMessageSeen = False


print '[OMNILAB: WTSM] INIT START!'

# Сброс параметров сайдчейнов Wwise
inDevLog('Reset RTPCs - Start')

for rtpc in WTSM_CONSTS.RTPCS:
    WTSoundsStuff.setRTPC(rtpc, -48)

inDevLog('Reset RTPCs - End')

# Привязка к ивентам клиента
inDevLog('Add to game events - Start')

g_playerEvents.onRoundFinished += wtBattleResult
g_playerEvents.onAvatarObserverVehicleChanged += WTSoundsStuff.setVehicleNation
g_playerEvents.onAvatarReady += addSoundNotifications
g_playerEvents.onAvatarReady += WTSoundsStuff.setVehicleNation
g_playerEvents.onAvatarReady += WTSoundsStuff.setBattleStatusSwitch
g_playerEvents.onAvatarReady += WTSoundsStuff.teamCorrelationVO
g_playerEvents.onAvatarReady += WTSoundsStuff.playBattleMusic
ServicesLocator.appLoader.onGUISpaceEntered += onGUISpaceEntered
InputHandler.g_instance.onKeyDown += WTSoundsStuff.lmbDownEvent

inDevLog('Add to game events - End')

print '[OMNILAB: WTSM] INIT END!'

print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'
print 'War Thunder Sound Mod for World of Tanks/Mir Tankov: %s (Build %s). Python Helper executed!' % (WTSM_CONSTS.VERSION, WTSM_CONSTS.BUILD)
print 'Copyright (C) 2023 OmniLab R&D.'
print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'

if WTSM_CONSTS.IN_DEV:
    import GUI

    t_gui = GUI.Text('War Thunder Sound Mod\ninDev 9\n\nBuild 0124/3')
    t_gui.multiline = True
    t_gui.position = (-0.982, -0.91, 0)
    t_gui.font = 'system_medium.font'
    t_gui.horizontalAnchor = GUI.Text.eHAnchor.LEFT
    GUI.addRoot(t_gui)

# ----------------------------------------------------------------------------------------------------------------------------------------------

# Неиспользуемые функции, которые сейчас доделать не представляется возможным.

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

# @staticmethod
# def getHoursFromAngle(angle):
#     return WTSM_CONSTS.A2H[min(sorted(WTSM_CONSTS.A2H.keys()), key=lambda x: abs(x-angle))]