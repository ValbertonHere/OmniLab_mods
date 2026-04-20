import base64
import logging
import os
import types

import BigWorld
import ResMgr

from CurrentVehicle import g_currentVehicle

from debug_utils import LOG_CURRENT_EXCEPTION

from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams

from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import InfoDialogBuilder, WarningDialogBuilder
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons

from helpers import dependency

from items.components.c11n_constants import ApplyArea

from serializable_types.customizations import CUSTOMIZATION_CLASSES
from serialization import parseCompDescr

from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService

from th_async import th_async, th_await

from vehicle_outfit.outfit import Outfit
from vehicle_systems.tankStructure import TankPartNames
from vehicle_systems.model_assembler import loadAppearancePrefab
from vehicle_systems.camouflages import SeasonType

from ._constants import DEV_MODE_FILE

__all__ = ('byteify', 'override', 'vfs_file_read', 'vfs_dir_list_files', 'getFashionValue', 'getHangarVehicle',
        'parse_localization_file', 'cache_result', 'getIconPatch', 'readBrandingItem', 'isBattleRestricted',
        'getParentWindow', 'awaitGameLoadingComplete')

logger = logging.getLogger(__name__)

def override(holder, name, wrapper=None, setter=None):
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

def vfs_file_read(path):
	fileInst = ResMgr.openSection(path)
	if fileInst is not None and ResMgr.isFile(path):
		return str(fileInst.asBinary)
	return None

def vfs2realfs(vfs_from, realfs_to):
    realfs_directory = os.path.dirname(realfs_to)
    if not os.path.exists(realfs_directory):
        os.makedirs(realfs_directory)
    vfs_data = vfs_file_read(vfs_from)
    if vfs_data:
        with open(realfs_to, 'wb') as realfs_file:
            realfs_file.write(vfs_data)

def getDevModeState():
    return os.path.exists(DEV_MODE_FILE)
    
def raiseJsonWrong(msg):
    logger.critical('--------------- CUSTOMIZATION JSON WRONG! ---------------')
    LOG_CURRENT_EXCEPTION()
    print msg
    BigWorld.crash(1)

# Взято из https://github.com/wotstat/wotstat-analytics/blob/main/WOTSTAT/res/scripts/client/gui/mods/wot_stat/common/exceptionSending.py
def reader_exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            raiseJsonWrong('Something went wrong while JSON reading process. See lines below.')

    return wrapper

def loadOUCWindow():
    app = dependency.instance(IAppLoader).getApp()
    app.loadView(SFViewLoadParams('UserCustomizationWindowUI'))

def loadUCSerialNumberView():
    app = dependency.instance(IAppLoader).getApp()
    app.loadView(SFViewLoadParams('UserCustomizationSerialNumberViewUI'))

def isInCustomization():
    app = dependency.instance(IAppLoader).getApp()
    return app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION)) is not None

def set3DStylePrefabs(vehicleDescriptor, vehicleAppearance, outfit, cache):
    if cache.prefabs.get(outfit.modelsSet, None) is None:
        return
    
    for tankPart in TankPartNames.ALL:
        tankPartItem = getattr(vehicleDescriptor, tankPart)
        tankPartItem.prefabs = tuple()
        
        if tankPart in (TankPartNames.GUN, TankPartNames.TURRET):
            tankPartPrefabs = cache.prefabs[outfit.modelsSet][tankPart + 's']
        else:
            tankPartPrefabs = cache.prefabs[outfit.modelsSet][tankPart]
        
        for prefab in tankPartPrefabs:
            loadAppearancePrefab(prefab, vehicleAppearance)

def getVehicleOutfitFromDict(outfitDict, vehicleDescriptor, season):
    c11nService = dependency.instance(ICustomizationService)

    isWithAlternateItems = outfitDict['isWithAlternateItems']
    outfit = outfitDict['outfit']

    if isWithAlternateItems:
        outfitComponent = Outfit(component=parseCompDescr(CUSTOMIZATION_CLASSES, base64.b64decode(outfit)), vehicleCD=vehicleDescriptor.makeCompactDescr())
    else:
        outfitComponent = c11nService.getItemByID(32, outfit).getOutfit(season, vehicleDescriptor.makeCompactDescr())
    
    outfitItem = outfitComponent.style
    
    if outfitItem.isProgressive():
        outfitComponent.setProgressionLevel(len(outfitItem.progression.levels))
    if outfitItem.isWithSerialNumber:
        outfitComponent.setSerialNumber('001')
    return outfitComponent

@th_async
def showCustomizationDialog(callback):
    builder = InfoDialogBuilder()
    builder.setFormattedMessage('#userCustomization:dialog/messageInfo')
    builder.setIcon(R.images.gui.maps.icons.customization.customization_items.c_600x450.icon_style())
    builder.setFormattedTitle('#userCustomization:dialog/title')
    builder.addButton(DialogButtons.SUBMIT, None, False, rawLabel='#userCustomization:dialog/serverOutfitBtn/label')
    builder.addButton(DialogButtons.RESEARCH, None, False, rawLabel='#userCustomization:dialog/userOutfitBtn/label')
    result = yield th_await(dialogs.show(builder.buildInLobby()))
    callback(result.result)

def checkCurrentVehicleServerOutfit():
    if getDevModeState():
        return True
    
    # Ищем, где на танке для разного типа карт есть камуфляж на всём танке или только на корпусе (именно в этом случае даётся маскировка).
    camoAffectedOutfits = 0
    for season in SeasonType.COMMON_SEASONS:
        for camo in g_currentVehicle.item.getOutfitComponent(season).camouflages: 
            if camo.appliedTo & ApplyArea.HULL:
                camoAffectedOutfits += 1
                break
    
    return camoAffectedOutfits == len(SeasonType.COMMON_SEASONS)