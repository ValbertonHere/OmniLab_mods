# Общение клиента и сервера на Web-Socket.

import socket
from time import sleep
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel
from OpenModsCore import overrideMethod
import BigWorld
from PlayerEvents import g_playerEvents

@overrideMethod(DamageLogPanel, '_updateTotalDamageValue')
def test(base, self, value):
    base(self, value)
    send_message('Total damage in battle: ' + value)

def onBattleResultsReceived(_, data):
    send_message('-----------BATTLE ENDED------------')
    send_message('Total damage after battle: %s' % data['personal'].items()[0][1]['damageDealt'])

def client_init():
    client = socket.socket()
    hostname = '26.174.146.138'
    port = 12345
    client.connect((hostname, port))
    return client

def send_message(msg='No message found.'):
    client = client_init()
    sleep(0.01)
    client.send(msg.encode())
    data = client.recv(1024)
    print "Server sent: %s" % data.decode()
    client.close()

send_message('init')

g_playerEvents.onBattleResultsReceived += onBattleResultsReceived