# Попытка в реализацию рандомных погодных условий на карте. Работает исправно.

import game
import xml.etree.ElementTree as ET
from urllib import urlopen
from random import randrange


def getWoTmodsPathFolder(): # Код функции переписать с использованием ResMgr.openSection('../paths.xml')['Paths'].values()[0].asString, который возвращает путь к папке res_mods/[номер_патча].
    global WoT_version
    pb_wotmods_patchfolder = urlopen('https://pastebin.com/raw/WPQqaizb')
    WoT_version = pb_wotmods_patchfolder.read()
    print '[VLBRTN] [ENV_CHANGER] Received mods folder for "wotmods" file format from Pastebin - %s' % (WoT_version)


def env_count():
    env_numbs = 0
    for i in env_list_file.findall('environment'):
        env_numbs += 1
    print '[VLBRTN] [ENV_CHANGER] Number of environment for current space - %i' % (env_numbs)
    return env_numbs


def envUpdate(spaceID, path):
    hookedOnGeometryMapped(spaceID, path)
    global env_list_file
    env_list_folder = "res_mods/%s/%s/environments/environments.xml" % (WoT_version, path)
    env_list_file = ET.parse(env_list_folder)
    env_active = env_list_file.find('activeEnvironment')
    env_list = env_list_file.findall('environment')
    env_amount = env_count()
    env_num = randrange(env_amount)
    environment = env_list[env_num]
    if environment.text == env_active.text:
        env_list.remove(env_list[env_num])
        env_amount -= 1
        environment = env_list[randrange(env_amount)]
    env_active.text = environment.text
    env_list_file.write(env_list_folder)


print '---------------------'
print '[VLBRTN] [ENV_CHANGER] Initialization successfull! Maps random weather changer executed!'
print '[VLBRTN] [ENV_CHANGER] Copyright (C) VLBRTN Community.'
print '[VLBRTN] [ENV_CHANGER] Licensed by WTFPLv2 Public Licence.'
print '---------------------'

getWoTmodsPathFolder()
if WoT_version:
    hookedOnGeometryMapped = game.onGeometryMapped
    game.onGeometryMapped = envUpdate
    print '[VLBRTN] [ENV_CHANGER] game.onGeometryMapped hooked!'