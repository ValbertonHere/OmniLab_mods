# Получение названия и пути к карте через хук.

import game

hookedOnGeometryMapped = game.onGeometryMapped

def hookOnGeometryMapped(spaceID, path):
    hookedOnGeometryMapped(spaceID, path)
    print 'mapName: %s, mapPath: %s' % (path.split('/')[-1], path)

game.onGeometryMapped = hookOnGeometryMapped