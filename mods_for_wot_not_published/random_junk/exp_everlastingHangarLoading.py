import BigWorld
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.ClientHangarSpace import g_clientHangarSpaceOverride
from gui import InputHandler
from gui.shared.utils.key_mapping import getBigworldNameFromKey

class Pizdec():
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.hangarSpace.onSpaceCreate += self.makePizdec
        g_clientHangarSpaceOverride.setPath('TEST')
    
    def makePizdec(self):
        BigWorld.callback(0.5, self.callback)
    
    def callback(self):
        g_clientHangarSpaceOverride.setPath('TEST')

def lessGooo(event):
    key = getBigworldNameFromKey(event.key)
    if key == 'KEY_F8':
        nig = Pizdec()

InputHandler.g_instance.onKeyDown += lessGooo