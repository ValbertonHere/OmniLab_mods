# Помощник для УГВ.

# Импорты модулей
import BigWorld
import WWISE

from OpenModsCore import overrideMethod

from random import randint
from gui import SystemMessages
from Avatar import PlayerAvatar
from PlayerEvents import g_playerEvents
from gui.shared.personality import ServicesLocator
from skeletons.gui.app_loader import GuiGlobalSpaceID
from gui.IngameSoundNotifications import ComplexSoundNotifications
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AmmoPlugin

# Класс констант мода
class WTSM_CONSTS():

    IN_DEV = False

    DEVICE_DESTR_CODES = {
        'DEVICE_DESTROYED', 
        'DEVICE_DESTROYED_AT_SHOT', 
        'DEVICE_DESTROYED_AT_FIRE', 
        'DEVICE_DESTROYED_AT_RAMMING',
        'DEVICE_DESTROYED_AT_WORLD_COLLISION'
    }

    SWITCHES = {
        'shell_prepared': 'SWITCH_shell_prepared',
        'team_correlation': 'SWITCH_team_correlation',
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
    def clearAllCallbacks():
        global tcvo_callbacks

        for cb in tcvo_callbacks:
            try:
                tcvo_callbacks.remove(cb)
                BigWorld.cancelCallback(cb)
            except: inDevLog('CallbackID incorrect! Skipping...')
            else: inDevLog('Callback removed - %s' % cb)

    @staticmethod
    def onGUISpaceEntered(spaceID, *args, **kwargs):
        if spaceID != GuiGlobalSpaceID.LOBBY:
            return
        
        global welcomeMessageSeen, shell_change_first, tcvo_first
        
        if not welcomeMessageSeen:
            SystemMessages.pushMessage('Вспомогательный скрипт загружен.<br>Необходимые параметры были применены.<br>Данная версия скриптового помощника является эксклюзивной и публикации не подлежит.',
                SystemMessages.SM_TYPE.InformationHeader,
                priority=True,
                messageData={'header': 'УНЕСЁННЫЙ ГРОМОМ ВОЙНЫ'})
            welcomeMessageSeen = True
        
        tcvo_first = True
        shell_change_first = True

        WTSoundsStuff.clearAllCallbacks()

    @staticmethod
    def afterArenaLoad():
        WTSoundsStuff.addEvent('wt_battle_won')
        WTSoundsStuff.addEvent('wt_battle_lose')
        WTSoundsStuff.addEvent('wt_ally_winning')
        WTSoundsStuff.addEvent('wt_enemy_winning')
        WTSoundsStuff.addEvent('wt_ally_dominating')
        WTSoundsStuff.addEvent('wt_enemy_dominating')
        WTSoundsStuff.addEvent('wt_left_track_destroyed')
        WTSoundsStuff.addEvent('wt_right_track_destroyed')
        WTSoundsStuff.addEvent('wt_gun_reloading', chance='15')
        WTSoundsStuff.addEvent('wt_gun_reloaded', chance='15', lifetime='0')
        WTSoundsStuff.addEvent('wt_shoot_voice', chance='15', predelay='0.75', lifetime='0.5')
        WTSoundsStuff.addEvent('wt_art_warning', predelay='0.5', lifetime='1.5')
        WTSoundsStuff.addEvent('wt_prepare_shell', fxEvent='load_shell_fx', lifetime='0')

        WTSoundsStuff.teamCorrelationVO()
        BigWorld.player().guiSessionProvider.shared.ammo.onNextShellChanged += WTSoundsStuff.shellChangeVO

    @staticmethod
    def onBattleFinished(winnerTeam, *args, **kwargs):
        WTSoundsStuff.clearAllCallbacks()
        if winnerTeam == BigWorld.player().team:
            BigWorld.player().soundNotifications.play('wt_battle_won')
        else:
            BigWorld.player().soundNotifications.play('wt_battle_lose')
                    
    @staticmethod
    def setSwitch(group, switch):
        WWISE.WW_setSwitch(group, '%s_%s' % (group, switch))
        inDevLog('Value of %s has been set to %s.' % (group, switch))


# Вывод всяких сообщений в python.log для отладки
def inDevLog(message):
    if WTSM_CONSTS.IN_DEV:
        print '[OMNILAB: WTSM] %s' % (message)
    else: pass

@overrideMethod(PlayerAvatar, '__showDamageIconAndPlaySound')
def devicesVO(base, self, damageCode, extra, *args, **kwargs):
    base(self, damageCode, extra, *args, **kwargs)

    if damageCode in WTSM_CONSTS.DEVICE_DESTR_CODES:
        if extra.name[:-len('Health')] in ('leftTrack0'):
            BigWorld.player().soundNotifications.play('wt_left_track_destroyed')
        elif extra.name[:-len('Health')] in ('rightTrack0'):
            BigWorld.player().soundNotifications.play('wt_right_track_destroyed')

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
        BigWorld.player().soundNotifications.play('wt_gun_reloaded')

@overrideMethod(AmmoPlugin, '__onGunAutoReloadTimeSet')
def wtVOGunReloaded_auto(base, self, state, stunned):
    base(self, state, stunned)
    isAutoReload = self._AmmoPlugin__guiSettings.hasAutoReload
    isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
    timeLast = state.getActualValue()
    timeLeft = state.getTimeLeft()
    if timeLeft == 0.0 and not isAutoReload and not isInPostmortem and (timeLast != -1):
        BigWorld.player().soundNotifications.play('wt_gun_reloaded')

tcvo_first = True
tcvo_callbacks = []
shell_change_first = True
welcomeMessageSeen = False

print '[OMNILAB: WTSM] INIT START!'

# Привязка к ивентам клиента
inDevLog('Add to game events - Start')

g_playerEvents.onAvatarReady += WTSoundsStuff.afterArenaLoad
g_playerEvents.onRoundFinished += WTSoundsStuff.onBattleFinished

ServicesLocator.appLoader.onGUISpaceEntered += WTSoundsStuff.onGUISpaceEntered

inDevLog('Add to game events - End')

print '[OMNILAB: WTSM] INIT END!'

print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'
print 'War Thunder Sound Mod for Mir Tankov: Special Edition for Pbody -iwnl-'
print 'Copyright (C) 2024 OmniLab R&D. NOT FOR PUBLIC USE.'
print '----------OMNILAB RESEARCH & DEVELOPMENT-----------'