import VOIP
from gui.shared import event_dispatcher

my_dbID = 72764962

def onPlayerSpeaking(dbID, state):
    if dbID != my_dbID:
        print dbID

VOIP.getVOIPManager().onPlayerSpeaking += onPlayerSpeaking

# Чтобы отобразить статистику игрока, но а ник можно получить на офф. портале.
event_dispatcher.showProfileWindow(13850499, '')