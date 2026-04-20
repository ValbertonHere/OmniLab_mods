import json
import logging
import os

from gui.SystemMessages import SM_TYPE, pushI18nMessage

from helpers import dependency

from items.components.c11n_constants import SeasonType
from items.customizations import CustomizationOutfit

from skeletons.gui.customization import ICustomizationService

from vehicle_outfit.outfit import Outfit
from vehicle_systems.camouflages import getStyleProgressionOutfit

from ._constants import CONFIG_FILE, CONFIG_FOLDER, NOTIFICATION_HEADER, DEV_NOTIFICATION_HEADER, FORBIDDEN_STYLES, OUTFIT_COMPONENT_NAME_TO_OBJECT, USER_START_UNIQUE_ID # <- Чуть позже внедрю.
from .cache import g_oucCache
from .utils import getDevModeState

logger = logging.getLogger(__name__)

class UserCustomizationConfig(object):
    c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self):
        if not os.path.isdir(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER)
        
        if not os.path.exists(CONFIG_FILE):
            self.saveConfigToFile({})
        
        self.updateConfig()
        logger.info('Config initialized!')

    def getConfigFromFile(self):
        return json.load(open(CONFIG_FILE, 'r'))

    def saveConfigToFile(self, data=None):
        if data is None:
            data = self.config
        
        json.dump(data, open(CONFIG_FILE, 'wb'), indent=4)
    
    def updateConfig(self):
        self.config = self.getConfigFromFile()
    
    def saveVehicleOutfit(self, vehicleName, outfitObj):
        outfit = None
        isWithAlternateItems = bool(outfitObj.style.alternateItems)
        self.config[vehicleName] = {'isWithAlternateItems': isWithAlternateItems}

        if isWithAlternateItems:
            outfit = self.__outfit2dict(outfitObj.pack())
        else:
            if outfitObj.style.id >= USER_START_UNIQUE_ID:
                outfit = g_oucCache.getComponentStrIDFromIntID('styles', outfitObj.style.id)
            else:
                outfit = outfitObj.style.id
        
        if outfitObj.style.isWithSerialNumber:
            self.config[vehicleName].update({'serialNumber': outfitObj.serialNumber})

        self.config[vehicleName].update({'outfit': outfit})
        self.saveConfigToFile()
        pushI18nMessage('#userCustomization:notification/outfitSaved', type=SM_TYPE.InformationHeader, messageData=NOTIFICATION_HEADER)
        
        if getDevModeState():
            pushI18nMessage('#userCustomization:notification/devModeWarn', type=SM_TYPE.WarningHeader, messageData=DEV_NOTIFICATION_HEADER)

    def removeOutfitFromConfig(self, vehicleName):
        del self.config[vehicleName]
        self.saveConfigToFile()
        pushI18nMessage('#userCustomization:notification/outfitRemoved', type=SM_TYPE.InformationHeader, messageData=NOTIFICATION_HEADER)

    def isOutfitInConfig(self, vehicleName):
        return vehicleName in self.config

    def getVehicleOutfit(self, vehicleDescriptor, season=SeasonType.SUMMER):
        savedOutfit = self.config.get(vehicleDescriptor.name, None)
        season = season if season != SeasonType.ALL else SeasonType.SUMMER # Для того, чтоб оно не падало при повышении уровня прогрессионных декалей.

        if savedOutfit is None:
            return None
        
        try:
            isWithAlternateItems = savedOutfit['isWithAlternateItems']
            outfit = savedOutfit['outfit']

            if isWithAlternateItems:
                outfitComponent = Outfit(component=self.__dict2outfit(outfit), vehicleCD=vehicleDescriptor.makeCompactDescr())
            else:
                if isinstance(outfit, unicode):
                    # Переводим строковый ID в числовой.
                    outfit = g_oucCache.getComponentIntIDFromStrID('styles', outfit)

                outfitComponent = self.c11nService.getItemByID(32, outfit).getOutfit(season, vehicleDescriptor.makeCompactDescr())
                
        except:
            pushI18nMessage('#userCustomization:notification/outfitResetByConfigError', type=SM_TYPE.InformationHeader, messageData=NOTIFICATION_HEADER)
            logger.exception('Failed to apply outfit! Tank: %s' % vehicleDescriptor.name)
            return

        if outfitComponent.id in FORBIDDEN_STYLES:
            pushI18nMessage('#userCustomization:notification/outfitResetByForbiddenStyle', type=SM_TYPE.InformationHeader, messageData=NOTIFICATION_HEADER)
            del self.config[vehicleDescriptor.name]
            self.saveConfigToFile()
            return None

        outfitItem = outfitComponent.style
        
        if outfitItem.isProgressive():
            outfitComponent.setProgressionLevel(len(outfitItem.progression.levels))
            outfitComponent = getStyleProgressionOutfit(outfitComponent, outfitComponent.progressionLevel, season)
        if outfitItem.isWithSerialNumber:
            outfitComponent.setSerialNumber(savedOutfit.get('serialNumber', '00000'))

        return outfitComponent

    def __outfit2dict(self, customizationOutfit):
        result = {}
        for fieldName in customizationOutfit.fields:
            fieldData = getattr(customizationOutfit, fieldName, customizationOutfit.fields[fieldName].default)
            if isinstance(fieldData, list):
                result[fieldName] = []
                for component in fieldData:
                    if fieldName in OUTFIT_COMPONENT_NAME_TO_OBJECT:
                        component_dict = component.to_dict()
                        
                        # Переводим числовой ID в строковый, чтоб не потерялась связка элементов к стилю.
                        if component.id >= USER_START_UNIQUE_ID:
                            component_dict['id'] = g_oucCache.getComponentStrIDFromIntID(fieldName, component.id)

                        result[fieldName].append(component_dict)
                    else:
                        result[fieldName].append(component)
            
            elif fieldName == 'styleId':
                result[fieldName] = g_oucCache.getComponentStrIDFromIntID('styles', fieldData)
            else:
                result[fieldName] = fieldData

        return result
    
    def __dict2outfit(self, outfitDict):
        result = {}
        for fieldName, fieldData in outfitDict.items():
            if isinstance(fieldData, list):
                result[fieldName] = []
                for component in fieldData:
                    if isinstance(component, dict):
                        if isinstance(component['id'], unicode):
                            component['id'] = g_oucCache.getComponentIntIDFromStrID(fieldName, component['id'])

                        result[fieldName].append(OUTFIT_COMPONENT_NAME_TO_OBJECT[fieldName](**component))
                    else:
                        result[fieldName].append(component)
            
            elif fieldName == 'styleId':
                result[fieldName] = g_oucCache.getComponentIntIDFromStrID('styles', fieldData)
            else:
                result[fieldName] = fieldData
        
        return CustomizationOutfit(**result)


g_oucConfig = UserCustomizationConfig()