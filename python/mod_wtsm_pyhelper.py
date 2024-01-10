# Помощник для УГВ.

# Импорты модулей
import SoundGroups
import BigWorld
import nations
import WWISE

from OpenModsCore import overrideMethod

from Math import Matrix
from gui import InputHandler
from gui import SystemMessages
from Avatar import PlayerAvatar
from random import randint, choice
from constants import ARENA_PERIOD
from PlayerEvents import g_playerEvents
from CurrentVehicle import g_currentVehicle
from gui.battle_control import avatar_getter
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
    UPD_NAME = 'Эпицентр'
    DIST_VALUES = [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1100, 1200]
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
        'team_correlation': 'SWITCH_team_correlation',
        'engine_event': 'SWITCH_engine_event',
        'crew_voice': 'SWITCH_crew_voice'
    }

    CREW_VOICELINES = {
        'vo_ammo_bay_damaged': 'loader',
        'vo_commander_killed': ('driver', 'gunner', 'loader'),
        'vo_driver_killed': ('gunner', 'loader'),
        'vo_enemy_hp_damaged_by_explosion_at_direct_hit_by_player': 'driver',
        'vo_enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player': 'driver',
        'vo_enemy_hp_damaged_by_projectile_and_gun_damaged_by_player': 'driver',
        'vo_enemy_hp_damaged_by_projectile_by_player': 'driver',
        'vo_enemy_killed_by_player': 'driver',
        'vo_engine_damaged': 'driver',
        'vo_engine_destroyed': 'driver',
        'vo_engine_functional': 'driver',
        'vo_fire_started': ('driver', 'gunner', 'loader'),
        'vo_fire_stopped': ('driver', 'gunner', 'loader'),
        'vo_fuel_tank_damaged': 'driver',
        'vo_gun_damaged': 'gunner',
        'vo_gun_destroyed': 'gunner',
        'vo_gun_functional': 'gunner',
        'vo_gunner_killed': ('driver', 'loader'),
        'vo_loader_killed': ('driver', 'gunner'),
        'vo_radio_damaged': 'driver',
        'vo_radioman_killed': 'gunner',
        'vo_track_destroyed': 'driver',
        'vo_track_functional': 'driver',
        'vo_track_functional_can_move': 'driver',
        'vo_turret_rotator_damaged': 'gunner',
        'vo_turret_rotator_destroyed': 'gunner',
        'vo_turret_rotator_functional': 'gunner',
        'vo_wt_artWarning': 'chief_m',
        'vo_wt_battleLose': 'chief_m',
        'vo_wt_battleWon': 'chief_m',
        'vo_wt_gunReloaded': 'loader',
        'vo_wt_leftTrackHit': 'driver',
        'vo_wt_prepareShell': 'commander',
        'vo_wt_rightTrackHit': 'driver',
        'vo_wt_shootVoice': ('commander', 'loader'),
        'vo_wt_targetLockedFar': 'commander',
        'vo_wt_targetLockedNear': 'commander',
        'vo_wt_weveBeenHit': ('driver', 'gunner', 'loader'),
        'vo_wt_wheelHit': 'driver',
        'vo_wt_wheelRepaired': 'driver'
    }

# Класс реализации дополнительных голосовых и звуковых уведомлений в очередь основных и прочего
class WTSoundsStuff():

    @staticmethod
    def addEvent(name, fxEvent='null', chance='100', priority='50', predelay='0', lifetime='5'):
        wt_event = {
            'name': name,
            'fxEvent': fxEvent,
            'infChance': chance,
            'predelay': predelay,
            'priority': priority,
            'lifetime': lifetime,
            'infEvent': 'vo_%s' % name,
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
            eng_event = BigWorld.player().vehicle.typeDescriptor.engine.sounds.getEvents()[0].split('eng_')[-1].split('_pc')[0]
            WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['engine_event'], eng_event)
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
        global combat_callbacks
        
        if attackedID == BigWorld.player():
            BigWorld.player().soundNotifications.play('wt_weveBeenHit')
            WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'combat')
            WTSoundsStuff.clearAllCallbacks()
            combat_callbacks.append(BigWorld.callback(30, WTSoundsStuff.setBattleStatusSwitch))
 
    @staticmethod
    def teamCorrelationVO():
        global tcvo_callbacks, tcvo_first

        alive_allies = 0
        aiive_enemies = 0
        cooldown = randint(60, 300)
        player_name = BigWorld.player().team
        arena_vehicles = BigWorld.player().arena.vehicles

        if tcvo_first:
            tcvo_first = False
            tcvo_callbacks.append(BigWorld.callback(cooldown, WTSoundsStuff.teamCorrelationVO))
            return
        
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
        
        tcvo_callbacks.append(BigWorld.callback(cooldown, WTSoundsStuff.teamCorrelationVO))

    @staticmethod
    def shellChangeVO(shellID):
        global shell_change_first

        if shell_change_first:
            shell_change_first = False
            return
        
        nextShellKind = BigWorld.player().guiSessionProvider.shared.ammo.getGunSettings().getShellDescriptor(shellID).kind
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['shell_prepared'], nextShellKind)
        BigWorld.player().soundNotifications.play('wt_prepareShell')
        
    @staticmethod
    def lmbDownEvent(event):
        if isinstance(BigWorld.player(), PlayerAvatar) and BigWorld.player().arena.period == ARENA_PERIOD.BATTLE:
            key = getBigworldNameFromKey(event.key)
            if key == 'KEY_MOUSE0':
                reloadTimeLeft = BigWorld.player().guiSessionProvider.shared.ammo.getGunReloadingState().getTimeLeft()
                isReloading = BigWorld.player().guiSessionProvider.shared.ammo.getGunReloadingState().isReloading()
                if isReloading and reloadTimeLeft <= 1.0 and not BigWorld.player().soundNotifications.isPlaying('wt_shootVoice'):
                    BigWorld.player().soundNotifications.play('wt_shootVoice')

    @staticmethod
    def setBattleStatusSwitch():
        if isinstance(BigWorld.player(), PlayerAvatar):
            if 100 * BigWorld.player().vehicle.health / BigWorld.player().vehicle.maxHealth > 35:
                WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'exploring')
                WTSoundsStuff.clearAllCallbacks()
    
    @staticmethod
    def clearAllCallbacks(tcvo=False):
        global combat_callbacks, tcvo_callbacks

        for cb in combat_callbacks:
            try:
                combat_callbacks.remove(cb)
                BigWorld.cancelCallback(cb)
            except: inDevLog('No Callbacks found. First time, huh?')
            else: inDevLog('Callback removed - %s' % cb)
        
        if tcvo:
            for cb in tcvo_callbacks:
                try:
                    tcvo_callbacks.remove(cb)
                    BigWorld.cancelCallback(cb)
                except: inDevLog('No Callbacks found. First time, huh?')
                else: inDevLog('Callback removed - %s' % cb)

    @staticmethod
    def onGUISpaceEntered(spaceID, *args, **kwargs):
        if spaceID != GuiGlobalSpaceID.LOBBY:
            return
        
        global welcomeMessageSeen, shell_change_first, tcvo_first

        g_currentVehicle.onChanged += WTSoundsStuff.setVehicleNation
        
        if not welcomeMessageSeen:
            SystemMessages.pushMessage('Вспомогательный скрипт загружен.<br>Необходимые параметры были применены.<br><br>Build %s' % WTSM_CONSTS.BUILD,
                SystemMessages.SM_TYPE.InformationHeader,
                priority=True,
                messageData={'header': 'Унесённый громом войны<br>%s - "%s"' % (WTSM_CONSTS.VERSION, WTSM_CONSTS.UPD_NAME)})
            welcomeMessageSeen = True
        
        tcvo_first = True
        shell_change_first = True

        WTSoundsStuff.clearAllCallbacks(True)
        SoundGroups.g_instance.playSound2D('wt_hangar_music')
        SoundGroups.g_instance.playSound2D('mt_hangar_music_stop')
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'exploring')

    @staticmethod
    def afterArenaLoad():
        WTSoundsStuff.addEvent('wt_battleWon')
        WTSoundsStuff.addEvent('wt_battleLose')
        WTSoundsStuff.addEvent('wt_allyWinning')
        WTSoundsStuff.addEvent('wt_enemyWinning')
        WTSoundsStuff.addEvent('wt_leftTrackHit')
        WTSoundsStuff.addEvent('wt_rightTrackHit')
        WTSoundsStuff.addEvent('wt_allyDominating')
        WTSoundsStuff.addEvent('wt_enemyDominating')
        WTSoundsStuff.addEvent('wt_wheelHit', lifetime='0.5')
        WTSoundsStuff.addEvent('wt_shootVoice', lifetime='0.2')
        WTSoundsStuff.addEvent('wt_wheelRepaired', lifetime='0.5')
        WTSoundsStuff.addEvent('wt_targetLockedFar', lifetime='1')
        WTSoundsStuff.addEvent('wt_targetLockedNear', lifetime='1')
        WTSoundsStuff.addEvent('wt_gunReloaded', chance='5', lifetime='0')
        WTSoundsStuff.addEvent('wt_weveBeenHit', chance='10', lifetime='0')
        WTSoundsStuff.addEvent('wt_artWarning', predelay='0.5', lifetime='1.5')
        WTSoundsStuff.addEvent('wt_prepareShell', fxEvent='load_shell_fx', lifetime='0')
        
        WTSoundsStuff.teamCorrelationVO()
        SoundGroups.g_instance.playSound2D('wt_battle_music')

        BigWorld.player().arena.onVehicleHealthChanged += WTSoundsStuff.onHealthChanged
        BigWorld.player().guiSessionProvider.shared.ammo.onNextShellChanged += WTSoundsStuff.shellChangeVO

    @staticmethod
    def onBattleFinished(winnerTeam, *args, **kwargs):
        WTSoundsStuff.clearAllCallbacks(True)
        SoundGroups.g_instance.playSound2D('wt_battle_end')
        if winnerTeam == BigWorld.player().team:
            SoundGroups.g_instance.playSound2D('wt_win_music')
            BigWorld.player().soundNotifications.play('wt_battleWon')
        else:
            SoundGroups.g_instance.playSound2D('wt_lose_music')
            BigWorld.player().soundNotifications.play('wt_battleLose')

    @staticmethod
    def getHoursFromAngle(target):
        tgPos = target.position
        playerPos = BigWorld.player().getOwnVehiclePosition()
        playerMatrix = Matrix(BigWorld.player().getOwnVehicleMatrix())
        pointDir = tgPos - playerPos
        pointDir.normalise()
        yawAngleRad = pointDir.yaw - playerMatrix.yaw
        yawAngleDeg = yawAngleRad * 180/3.14
        if yawAngleDeg < 0:
            yawAngleDeg = 360 - abs(yawAngleDeg)

        return WTSM_CONSTS.A2H[min(sorted(WTSM_CONSTS.A2H.keys()), key=lambda x: abs(x-yawAngleDeg))]

    @staticmethod
    def onCrewVoiceEnded(*args, **kwargs):
        SoundGroups.g_instance.playSound2D('wt_static_stop')
        SoundGroups.g_instance.playSound2D('wt_end_click')

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
    global combat_callbacks
    
    WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'combat')
    WTSoundsStuff.clearAllCallbacks()
    combat_callbacks.append(BigWorld.callback(30, WTSoundsStuff.setBattleStatusSwitch))

@overrideMethod(PlayerAvatar, '__showDamageIconAndPlaySound')
def devicesVO(base, self, damageCode, extra, *args, **kwargs):
    base(self, damageCode, extra, *args, **kwargs)
    global combat_callbacks

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
    
    WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'combat')
    WTSoundsStuff.clearAllCallbacks()
    combat_callbacks.append(BigWorld.callback(30, WTSoundsStuff.setBattleStatusSwitch))

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

@overrideMethod(PlayerAvatar, 'autoAim')
def wtAutoAim(base, self, target=None, magnetic=False):
  base(self, target, magnetic)

  if target is not None and target.isAlive() and target.publicInfo['team'] != self.team and self._PlayerAvatar__autoAimVehID == target.id:
    dist = avatar_getter.getDistanceToTarget(target)
    corr_angle = WTSoundsStuff.getHoursFromAngle(target)
    WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['target_hours'], corr_angle)

    if dist < WTSM_CONSTS.DIST_VALUES[0]:
        BigWorld.player().soundNotifications.play('wt_targetLockedNear')
    else:
        corr_dist = min(WTSM_CONSTS.DIST_VALUES, key=lambda x: abs(x-dist))
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['target_distance'], corr_dist)
        BigWorld.player().soundNotifications.play('wt_targetLockedFar')

@overrideMethod(SoundGroups.g_instance, 'WWgetSound')
def wtVoiceCallback(base, eventName, objectName, matrix, local=(0.0, 0.0, 0.0)):
    global sound
    if eventName in WTSM_CONSTS.CREW_VOICELINES:
        if type(WTSM_CONSTS.CREW_VOICELINES[eventName]) == tuple:
            crew_voice = choice(WTSM_CONSTS.CREW_VOICELINES[eventName])
        else:
            crew_voice = WTSM_CONSTS.CREW_VOICELINES[eventName]
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['crew_voice'], crew_voice)
        sound = WWISE.WW_getSound(eventName, objectName, matrix, local)
        sound.setCallback(WTSoundsStuff.onCrewVoiceEnded)
        sound.play()
        return base('wt_static', objectName, matrix, local)
    else:
        return base(eventName, objectName, matrix, local)

tcvo_first = True
tcvo_callbacks = []
combat_callbacks = []
shell_change_first = True
welcomeMessageSeen = False

print '[OMNILAB: WTSM] INIT START!'

# Сброс параметров сайдчейнов Wwise
inDevLog('Reset RTPCs - Start')

for rtpc in WTSM_CONSTS.RTPCS:
    WTSoundsStuff.setRTPC(rtpc, -48)

inDevLog('Reset RTPCs - End')

# Привязка к ивентам клиента
inDevLog('Add to game events - Start')

g_playerEvents.onAvatarReady += WTSoundsStuff.afterArenaLoad
g_playerEvents.onAvatarReady += WTSoundsStuff.setVehicleNation
g_playerEvents.onRoundFinished += WTSoundsStuff.onBattleFinished
g_playerEvents.onAvatarObserverVehicleChanged += WTSoundsStuff.setVehicleNation

InputHandler.g_instance.onKeyDown += WTSoundsStuff.lmbDownEvent
ServicesLocator.appLoader.onGUISpaceEntered += WTSoundsStuff.onGUISpaceEntered

inDevLog('Add to game events - End')

print '[OMNILAB: WTSM] INIT END!'

print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'
print 'War Thunder Sound Mod for World of Tanks/Mir Tankov: %s (Build %s). Python Helper executed!' % (WTSM_CONSTS.VERSION, WTSM_CONSTS.BUILD)
print 'Copyright (C) 2023 OmniLab R&D.'
print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'

if WTSM_CONSTS.IN_DEV:
    import GUI

    t_gui = GUI.Text('War Thunder Sound Mod\ninDev 9\n\n%s' % WTSM_CONSTS.BUILD)
    t_gui.multiline = True
    t_gui.position = (-0.982, -0.91, 0)
    t_gui.font = 'system_medium.font'
    t_gui.horizontalAnchor = GUI.Text.eHAnchor.LEFT
    GUI.addRoot(t_gui)