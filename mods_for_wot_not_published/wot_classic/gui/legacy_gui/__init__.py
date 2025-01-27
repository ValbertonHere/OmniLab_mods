from debug_utils import LOG_CURRENT_EXCEPTION

try:
    from .account_hooks import *
    
    try:
        from .avatar_hooks import *
        from .battle_views import *
    except:
        print '[OMNILAB R&D: Legacy GUI] Battle GUI not installed or has caused an exception. See lines below.'

    from .lobby_views import *
    print '[OMNILAB R&D: Legacy GUI] LOBBY GUI INITIALIZED!'
except:
    print '[OMNILAB R&D: Legacy GUI] One of gui mods not installed or has caused an exception. See lines below.'
    LOG_CURRENT_EXCEPTION()
    pass


__all__ = ()
