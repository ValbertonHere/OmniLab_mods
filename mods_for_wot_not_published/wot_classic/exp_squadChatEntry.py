from messenger.gui.Scaleform.channels import ControllersCollection
from messenger import MessengerEntry
from messenger.proto.bw.entities import BWChannelEntity
from messenger.gui.Scaleform.view.lobby.LobbyChannelWindow import LobbyChannelWindow
from messenger.gui.events_dispatcher import showLobbyChannelWindow
from messenger.gui.Scaleform.view.lobby import _MessengerPackageBusinessHandler

def new_loadViewWithDefName(self, alias, name=None, parent=None, *args, **kwargs):
    if args[0]['clientID'] == -483:
        print 'onSquadClick'
        return
    else:
        base5(self, alias, name, parent, *args, **kwargs)

#_MessengerPackageBusinessHandler.loadViewWithDefName = base5
#base5 = _MessengerPackageBusinessHandler.loadViewWithDefName
#_MessengerPackageBusinessHandler.loadViewWithDefName = new_loadViewWithDefName

def addChannel():
    #channelEnt = BWChannelEntity({'id': -483, 'channelName': '#chat:channels/squad', 'isReadOnly': True, 'isSystem': True, 'isSecured': True, 'greeting': 'OmniTest1'})
    #channelEnt.setClientID(-483)
    #MessengerEntry.g_instance.gui.getEntry(2)._LobbyEntry__carouselHandler.addChannel(channelEnt, True)
    MessengerEntry.g_instance.gui.getEntry(2)._LobbyEntry__carouselHandler._ChannelsCarouselHandler__setItemField(-483, 'icon', 'squad_icon.png')
    
#print MessengerEntry.g_instance.gui.getEntry(2)._LobbyEntry__carouselHandler._ChannelsCarouselHandler__channelsDP._ChannelsDataProvider__data
#print channelEnt
addChannel()
print 'done'