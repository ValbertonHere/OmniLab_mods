try:
    from .account_hooks import *
    print '[OMNILAB R&D: Legacy GUI] LOBBY GUI INITIALIZED!'
    from .avatar_hooks import *
    print '[OMNILAB R&D: Legacy GUI] BATTLE GUI INITIALIZED!'
except:
    print '[OMNILAB R&D: Legacy GUI] ONE OF GUI MODS NOT INSTALLED!'

from .views import *

__all__ = ('init', 'fini')

def init():
    print '[OMNILAB R&D: Legacy GUI] INITIALIZED!'

def fini():
    print '[OMNILAB R&D: Legacy GUI] FINISHED!'