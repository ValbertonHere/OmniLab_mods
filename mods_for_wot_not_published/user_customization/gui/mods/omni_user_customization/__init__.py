import BigWorld, logging

logger = logging.getLogger(__name__)

try:
    from ._constants import NOTIFICATION_HEADER
    # from api import g_api <- Это будет потом. =)
    from .hooks import *
    from .config import g_oucConfig
    from .cache import g_oucCache
    from .views import *
except ImportError:
    logger.exception('User Customization initialization failed! See lines below.')
    BigWorld.crash(1)