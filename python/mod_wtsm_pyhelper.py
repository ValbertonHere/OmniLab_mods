# Помощник для УГВ.

# Импорты модулей
import SoundGroups
import BigWorld
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
from gui.game_loading.resources.cdn.cache import GameLoadingCdnCache
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AmmoPlugin

# Класс констант мода
class WTSM_CONSTS():

    IN_DEV = False
    BUILD = '0124/7'
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
        'vo_wt_art_warning': 'chief_m',
        'vo_wt_battle_lose': 'chief_m',
        'vo_wt_battle_won': 'chief_m',
        'vo_wt_gun_reloaded': 'loader',
        'vo_wt_left_track_hit': 'driver',
        'vo_wt_prepare_shell': 'commander',
        'vo_wt_right_track_hit': 'driver',
        'vo_wt_shoot_voice': ('commander', 'loader'),
        'vo_wt_target_locked_far': 'commander',
        'vo_wt_target_locked_near': 'commander',
        'vo_wt_weve_been_hit': ('driver', 'gunner', 'loader'),
        'vo_wt_wheel_hit': 'driver',
        'vo_wt_wheel_repaired': 'driver',
        'vo_wt_chief_battle_start': 'chief_m',
        'vo_wt_comm_battle_start': 'commander',
        'vo_wt_driver_ready': 'driver',
        'vo_wt_gunner_ready': 'gunner',
        'vo_wt_loader_ready': 'loader'
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
        vehicle = g_currentVehicle.item
        if vehicle is not None:
            playerNation = vehicle.nationName
            WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['nation'], playerNation)

    @staticmethod
    def onHealthChanged(attackedID, *args, **kwargs):
        global combat_callbacks

        if attackedID == BigWorld.player().playerVehicleID:
            BigWorld.player().soundNotifications.play('wt_weve_been_hit')
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
            BigWorld.player().soundNotifications.play('wt_ally_dominating')
        elif  alive_allies < aiive_enemies and alive_allies <= 3:
            BigWorld.player().soundNotifications.play('wt_enemy_dominating')
        elif alive_allies < aiive_enemies:
            BigWorld.player().soundNotifications.play('wt_enemy_winning')
        elif alive_allies > aiive_enemies:
            BigWorld.player().soundNotifications.play('wt_ally_winning')
        
        tcvo_callbacks.append(BigWorld.callback(cooldown, WTSoundsStuff.teamCorrelationVO))

    @staticmethod
    def shellChangeVO(shellID):
        global shell_change_first

        if shell_change_first:
            shell_change_first = False
            return
        
        nextShellKind = BigWorld.player().guiSessionProvider.shared.ammo.getGunSettings().getShellDescriptor(shellID).kind
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['shell_prepared'], nextShellKind)
        BigWorld.player().soundNotifications.play('wt_prepare_shell')
        
    @staticmethod
    def lmbDownEvent(event):
        if isinstance(BigWorld.player(), PlayerAvatar) and BigWorld.player().arena.period == ARENA_PERIOD.BATTLE:
            key = getBigworldNameFromKey(event.key)
            if key == 'KEY_MOUSE0':
                reloadTimeLeft = BigWorld.player().guiSessionProvider.shared.ammo.getGunReloadingState().getTimeLeft()
                isReloading = BigWorld.player().guiSessionProvider.shared.ammo.getGunReloadingState().isReloading()
                if isReloading and reloadTimeLeft <= 1.0 and not BigWorld.player().soundNotifications.isPlaying('wt_shoot_voice'):
                    BigWorld.player().soundNotifications.play('wt_shoot_voice')

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
            except: inDevLog('CallbackID incorrect! Skipping...')
            else: inDevLog('Callback removed - %s' % cb)
        
        if tcvo:
            for cb in tcvo_callbacks:
                try:
                    tcvo_callbacks.remove(cb)
                    BigWorld.cancelCallback(cb)
                except: inDevLog('CallbackID incorrect! Skipping...')
                else: inDevLog('Callback removed - %s' % cb)

    @staticmethod
    def onBattleStart(period, *args, **kwargs):
        global battle_started
        if period == ARENA_PERIOD.BATTLE and not battle_started:
            battle_started = True
            BigWorld.player().soundNotifications.play('wt_chief_battle_start')
            BigWorld.player().soundNotifications.play('wt_comm_battle_start')
            BigWorld.player().soundNotifications.play('wt_driver_ready')
            BigWorld.player().soundNotifications.play('wt_gunner_ready')
            BigWorld.player().soundNotifications.play('wt_loader_ready')


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

        SoundGroups.g_instance.playSound2D('mt_hangar_music_stop')
        for word in ('ny', 'newyear', 'new_year'):
            if word in BigWorld.player().hangarSpace.spacePath:
                SoundGroups.g_instance.playSound2D('wt_hangar_music_ny')
                break
            else:
                SoundGroups.g_instance.playSound2D('wt_hangar_music')
        
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'exploring')

    @staticmethod
    def afterArenaLoad():
        global battle_started

        WTSoundsStuff.addEvent('wt_battle_won')
        WTSoundsStuff.addEvent('wt_battle_lose')
        WTSoundsStuff.addEvent('wt_ally_winning')
        WTSoundsStuff.addEvent('wt_enemy_winning')
        WTSoundsStuff.addEvent('wt_left_track_hit')
        WTSoundsStuff.addEvent('wt_right_track_hit')
        WTSoundsStuff.addEvent('wt_ally_dominating')
        WTSoundsStuff.addEvent('wt_enemy_dominating')
        WTSoundsStuff.addEvent('wt_wheel_hit', lifetime='0.5')
        WTSoundsStuff.addEvent('wt_shoot_voice', lifetime='0.2')
        WTSoundsStuff.addEvent('wt_wheel_repaired', lifetime='0.5')
        WTSoundsStuff.addEvent('wt_target_locked_far', lifetime='1')
        WTSoundsStuff.addEvent('wt_target_locked_near', lifetime='1')
        WTSoundsStuff.addEvent('wt_gun_reloaded', chance='5', lifetime='0')
        WTSoundsStuff.addEvent('wt_weve_been_hit', chance='30', lifetime='0')
        WTSoundsStuff.addEvent('wt_art_warning', predelay='0.5', lifetime='1.5')
        WTSoundsStuff.addEvent('wt_driver_ready', priority='1000', lifetime='10')
        WTSoundsStuff.addEvent('wt_gunner_ready', priority='1000', lifetime='10')
        WTSoundsStuff.addEvent('wt_comm_battle_start', priority='1000', lifetime='10')
        WTSoundsStuff.addEvent('wt_chief_battle_start', priority='1000', lifetime='10')
        WTSoundsStuff.addEvent('wt_prepare_shell', fxEvent='load_shell_fx', lifetime='0')
        WTSoundsStuff.addEvent('wt_loader_ready', priority='1000', lifetime='10', chance='15')

        WTSoundsStuff.clearAllCallbacks(True)
        WTSoundsStuff.teamCorrelationVO()
        SoundGroups.g_instance.playSound2D('wt_battle_music')
        eng_event = BigWorld.player().vehicle.typeDescriptor.engine.sounds.getEvents()[0].split('eng_')[-1].split('_pc')[0]
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['engine_event'], eng_event)
        battle_started = False
        BigWorld.player().arena.onVehicleHealthChanged += WTSoundsStuff.onHealthChanged
        BigWorld.player().guiSessionProvider.shared.ammo.onNextShellChanged += WTSoundsStuff.shellChangeVO

    @staticmethod
    def onBattleFinished(winnerTeam, *args, **kwargs):
        WTSoundsStuff.clearAllCallbacks(True)
        SoundGroups.g_instance.playSound2D('wt_battle_end')
        if winnerTeam == BigWorld.player().team:
            SoundGroups.g_instance.playSound2D('wt_win_music')
            BigWorld.player().soundNotifications.play('wt_battle_won')
        else:
            SoundGroups.g_instance.playSound2D('wt_lose_music')
            BigWorld.player().soundNotifications.play('wt_battle_lose')

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
        BigWorld.player().soundNotifications.play('wt_weve_been_hit')
    if damageCode in WTSM_CONSTS.DEVICE_CRIT_CODES:
        if extra.name[:-len('Health')].startswith('wheel'):
            BigWorld.player().soundNotifications.play('wt_wheel_hit')
        elif extra.name[:-len('Health')] in ('leftTrack0', 'leftTrack1'):
            BigWorld.player().soundNotifications.play('wt_left_track_hit')
        elif extra.name[:-len('Health')] in ('rightTrack0', 'rightTrack1'):
            BigWorld.player().soundNotifications.play('wt_right_track_hit')
    
    if damageCode == 'DEVICE_REPAIRED' and extra.name[:-len('Health')].startswith('wheel'):
        BigWorld.player().soundNotifications.play('wt_wheel_repaired')
    
    WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['battle_status'], 'combat')
    WTSoundsStuff.clearAllCallbacks()
    combat_callbacks.append(BigWorld.callback(30, WTSoundsStuff.setBattleStatusSwitch))

# Реализация предупреждения огня арты на игрока
@overrideMethod(ComplexSoundNotifications, 'notifyEnemySPGShotSound')
def wtVOArtWarning(base, self, distToTarget, shooterPosition):
    base(self, distToTarget, shooterPosition)
    if isinstance(BigWorld.player(), PlayerAvatar):
        BigWorld.player().soundNotifications.play('wt_art_warning')

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
        BigWorld.player().soundNotifications.play('wt_gun_reloaded')

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
        BigWorld.player().soundNotifications.play('wt_gun_reloaded')

@overrideMethod(PlayerAvatar, 'autoAim')
def wtAutoAim(base, self, target=None, magnetic=False):
  base(self, target, magnetic)

  if target is not None and target.isAlive() and target.publicInfo['team'] != self.team and self._PlayerAvatar__autoAimVehID == target.id:
    dist = avatar_getter.getDistanceToTarget(target)
    corr_angle = WTSoundsStuff.getHoursFromAngle(target)
    WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['target_hours'], corr_angle)

    if dist < WTSM_CONSTS.DIST_VALUES[0]:
        BigWorld.player().soundNotifications.play('wt_target_locked_near')
    else:
        corr_dist = min(WTSM_CONSTS.DIST_VALUES, key=lambda x: abs(x-dist))
        WTSoundsStuff.setSwitch(WTSM_CONSTS.SWITCHES['target_distance'], corr_dist)
        BigWorld.player().soundNotifications.play('wt_target_locked_far')

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

@overrideMethod(GameLoadingCdnCache, '__init__')
def ccpmInit(base, self, defaults, externalConfigUrl=None, cohort=None):
    base(self, defaults, 'https://raw.githubusercontent.com/ValbertonHere/OmniLab_mods/main/wtsm_loading_screen/config.json', cohort)

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
g_playerEvents.onRoundFinished += WTSoundsStuff.onBattleFinished
g_playerEvents.onArenaPeriodChange += WTSoundsStuff.onBattleStart

InputHandler.g_instance.onKeyDown += WTSoundsStuff.lmbDownEvent
ServicesLocator.appLoader.onGUISpaceEntered += WTSoundsStuff.onGUISpaceEntered

inDevLog('Add to game events - End')

print '[OMNILAB: WTSM] INIT END!'

print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'
print 'War Thunder Sound Mod for Mir Tankov: %s (Build %s). Python Helper executed!' % (WTSM_CONSTS.VERSION, WTSM_CONSTS.BUILD)
print 'Copyright (C) 2024 OmniLab R&D.'
print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'

if WTSM_CONSTS.IN_DEV:
    import GUI

    t_gui = GUI.Text('War Thunder Sound Mod\ninDev 9\n\n%s' % WTSM_CONSTS.BUILD)
    t_gui.multiline = True
    t_gui.position = (-0.982, -0.91, 0)
    t_gui.font = 'system_medium.font'
    t_gui.horizontalAnchor = GUI.Text.eHAnchor.LEFT
    GUI.addRoot(t_gui)