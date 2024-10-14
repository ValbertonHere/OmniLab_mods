# Тест генерирования звука на определенных координатах на карте. Работает.

import BigWorld
import SoundGroups

player = BigWorld.player()
position = player.getOwnVehiclePosition()

print 'mod_loaded'
print '------------'
print player.name
print position
print SoundGroups.g_instance.playSound2D
print SoundGroups.g_instance.playSoundPos('expl_ammo_NPC', (105.0, -5, 100.0))
print '------------'