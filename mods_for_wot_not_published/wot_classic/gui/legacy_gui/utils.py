"""Taken from POLIROID mods."""

import types

def override(holder, name, wrapper=None, setter=None):
    """Override methods, properties, functions, attributes
    :param holder: holder in which target will be overrided
    :param name: name of target to be overriden
    :param wrapper: replacement for override target
    :param setter: replacement for target property setter"""
    if wrapper is None:
        return lambda wrapper, setter=None: override(holder, name, wrapper, setter)
    target = getattr(holder, name)
    wrapped = lambda *a, **kw: wrapper(target, *a, **kw)
    if not isinstance(holder, types.ModuleType) and isinstance(target, types.FunctionType):
        setattr(holder, name, staticmethod(wrapped))
    elif isinstance(target, property):
        prop_getter = lambda *a, **kw: wrapper(target.fget, *a, **kw)
        prop_setter = target.fset if not setter else lambda *a, **kw: setter(target.fset, *a, **kw)
        setattr(holder, name, property(prop_getter, prop_setter, target.fdel))
    else:
        setattr(holder, name, wrapped)
