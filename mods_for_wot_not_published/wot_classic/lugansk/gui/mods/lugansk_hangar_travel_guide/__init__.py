import logging, BigWorld

from ._constants import *
from .hangar_extras import *
from .main_view import *
from .prefab_stuff import *

logger = logging.getLogger(__name__)

try: 
    import openwg_gameface
except ImportError:
  logger.critical('\n' +
                  "!!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!\n"
                  "!!!\n"
                  "!!!   Lugansk Hangar Travel Guide mod requires the openwg_gameface module to function.\n"
                  "!!!   Without it, this and other GF UI mods will not work correctly.\n"
                  "!!!   Please download and install it from: https://gitlab.com/openwg/wot.gameface/-/releases/\n"
                  "!!!\n"
                  "!!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!\n")

  BigWorld.crash(1)


g_luganskHangarExtras = LuganskHangarExtras()