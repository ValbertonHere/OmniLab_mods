# Мод-дампер техники. Нужен для сбора данных при вылете с SD-моделями.

import BigWorld
import os
from datetime import datetime

from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from PlayerEvents import g_playerEvents

logs_folder = './replays/vehicleDumper'

def dump_vehicles():
    try:
        allies = {}
        enemies = {}

        mapName = BigWorld.player().sessionProvider.arenaVisitor.type.getGeometryName()
        playerVehicle = BigWorld.player().vehicle.typeDescriptor.name.split(':')[1]
        currTime = datetime.now().strftime("%d-%m-%Y_%H%M%S")

        for _, v in BigWorld.player().arena.vehicles.items():
            name = v['vehicleType'].name.split(':')[1]
            allyRepeat = 0
            enemyRepeat = 0

            if v['team'] == BigWorld.player().team:
                if name in allies:
                    name = name + ' | %s' % str(allyRepeat)
                    allyRepeat += 1
                allies[name] = (v['vehicleType'].type.userString, v['vehicleType'].level)
            else:
                if name in enemies:
                    name = name + ' | %s' % str(enemyRepeat)
                    enemyRepeat += 1
                enemies[name] = (v['vehicleType'].type.userString, v['vehicleType'].level)

        with open(logs_folder + '/%s.txt' % (currTime), 'w+') as f:
            f.write('THIS FILE CREATED BY ARENA VEHICLE DUMPER.\nCopyright (C) 2024 OmniLab R&D.\n\n')
            f.write('Player: %s\n' % BigWorld.player().name)
            f.write('Vehicle: %s\n' % playerVehicle)
            f.write('Map: %s\n----------------------------------------' % mapName)

            f.write('\nAllies:')
            for k, v in allies.items():
                f.write('\n' + k + ' (userString: ' + v[0] + ', level: ' + str(v[1]) + ')')

            f.write('\n\nEnemies:')
            for k, v in enemies.items():
                f.write('\n' + k + ' (userString: ' + v[0] + ', level: ' + str(v[1]) + ')')

            f.write('\n\nVehicles dumped: \n Allies: %s, Enemies: %s' % (len(allies), len(enemies)))
    except:
        print '----------------------------------------------'
        print "Failed to dump vehicles, here's the traceback:"
        LOG_CURRENT_EXCEPTION()

try:
    if not os.path.isdir(logs_folder):
        os.makedirs(logs_folder)
except Exception:
    LOG_ERROR('Failed to create directory for replay files')


g_playerEvents.onAvatarReady += dump_vehicles