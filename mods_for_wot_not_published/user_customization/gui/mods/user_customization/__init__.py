import BigWorld, logging

logger = logging.getLogger(__name__)

try:
    # from api import g_api <- Это будет потом. =)
    from .cache import *
    from .config import *
    from .patches import *
    from .views import *
except ImportError:
    logger.exception('User Customization initialization failed! See lines below.')
    BigWorld.crash(1)