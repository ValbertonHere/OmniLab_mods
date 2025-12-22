import base64
import logging
import os
import types

import BigWorld
import ResMgr

from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams

from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import InfoDialogBuilder, WarningDialogBuilder
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons

from helpers import dependency

from serializable_types.customizations import CUSTOMIZATION_CLASSES
from serialization import parseCompDescr

from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService

from th_async import th_async, th_await

from vehicle_outfit.outfit import Outfit
from vehicle_systems.tankStructure import TankPartNames
from vehicle_systems.model_assembler import loadAppearancePrefab

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

def loadOUCWindow():
    app = dependency.instance(IAppLoader).getApp()
    app.loadView(SFViewLoadParams('UserCustomizationWindowUI'))

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
def showCustomizationDialog(isServerCamoApplied, callback):
    if isServerCamoApplied:
        builder = InfoDialogBuilder()
        builder.setFormattedMessage('#userCustomization:dialog/messageInfo')
        builder.setIcon(R.images.gui.maps.icons.customization.customization_items.c_600x450.icon_style())
    else:
        builder = WarningDialogBuilder()
        builder.setFormattedMessage('#userCustomization:dialog/messageWarning')
    
    builder.setFormattedTitle('#userCustomization:dialog/title')
    builder.addButton(DialogButtons.SUBMIT if isServerCamoApplied else DialogButtons.PURCHASE, None, False, rawLabel='#userCustomization:dialog/serverOutfitBtn/label')
    builder.addButton(DialogButtons.RESEARCH, None, False, rawLabel='#userCustomization:dialog/userOutfitBtn/label')
    result = yield th_await(dialogs.show(builder.buildInLobby()))
    callback(result.result)

def readUserCustomItem(itemCls, itemType, itemName, dataSection, cache, storage):
    from items.readers.c11n_readers import _readItems
    itemsFileName = 'valberton/user_customization/xml/%s' % itemName
    try:
        _readItems(cache, itemCls, (None, 'ouc_%s' % itemName), dataSection, itemType, storage, {})
    except:
        logger.exception("Failed to read custom item, id's conflict? (xml: %s)" % itemsFileName)
        BigWorld.crash(1)
    finally:
        ResMgr.purge(itemsFileName)