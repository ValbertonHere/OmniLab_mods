from debug_utils import LOG_CURRENT_EXCEPTION

try:
    from .account_hooks import *
    from .avatar_hooks import *
    from .battle_views import *
    from .lobby_views import *
    print '[OMNILAB R&D: Legacy GUI] LOBBY GUI INITIALIZED!'
except:
    print '[OMNILAB R&D: Legacy GUI] One of gui mods not installed or has caused an exception. See lines below.'
    LOG_CURRENT_EXCEPTION()


__all__ = ()
