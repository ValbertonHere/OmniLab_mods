from ResMgr import isFile

from .account_hooks import *
from .avatar_hooks import *

from .views import *

__all__ = ('init', 'fini')

def init():
    print '[OMNILAB R&D: Legacy GUI] INITIALIZED!'

def fini():
    print '[OMNILAB R&D: Legacy GUI] FINISHED!'