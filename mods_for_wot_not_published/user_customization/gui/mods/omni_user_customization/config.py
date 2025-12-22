import json
import logging
import os

from gui.SystemMessages import SM_TYPE, pushI18nMessage

from helpers import dependency

from items.components.c11n_constants import SeasonType
from items.customizations import CustomizationOutfit

from skeletons.gui.customization import ICustomizationService

from vehicle_outfit.outfit import Outfit

from ._constants import CONFIG_FILE, CONFIG_FOLDER, DEV_MODE_FILE, NOTIFICATION_HEADER, FORBIDDEN_STYLES, CUSTOMIZATION_STRINGS2CLASSES # <- Чуть позже внедрю.

logger = logging.getLogger(__name__)

class UserCustomizationConfig(object):
    c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self):
        if not os.path.isdir(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER)
        
        if not os.path.exists(CONFIG_FILE):
            self.saveConfigToFile({})
        
        self.config = self.getConfigFromFile()
        logger.info('Config initialized!')
    
    def getDevModeState(self):
        return os.path.exists(DEV_MODE_FILE)

    def getConfigFromFile(self):
        return json.load(open(CONFIG_FILE, 'r'))

    def saveConfigToFile(self, data=None):
        if data is None:
            data = self.config
        
        json.dump(data, open(CONFIG_FILE, 'wb'), indent=4)
    
    def saveVehicleOutfit(self, vehicleName, outfit):
        isWithAlternateItems = bool(outfit.style.alternateItems)
        self.config[vehicleName] = {'isWithAlternateItems': isWithAlternateItems, 'outfit': self.__outfit2dict(outfit.pack()) if isWithAlternateItems else outfit.style.id} # Сраный json в Python не умеет нормально конвертировать объекты без __dict__ в json-строку. Поэтому мы просто переводим его в строку и всё работает. Шизика!
        self.saveConfigToFile()
        pushI18nMessage('#userCustomization:notification/outfitSaved', type=SM_TYPE.InformationHeader, messageData={'header': NOTIFICATION_HEADER})

    def isOutfitInConfig(self, vehicleName):
        return bool(self.config.get(vehicleName, False))
    
    def getVehicleOutfit(self, vehicleDescriptor, season=SeasonType.SUMMER):
        savedOutfit = self.config.get(vehicleDescriptor.name, None)
        season = season if season != SeasonType.ALL else SeasonType.SUMMER # Для того, чтоб оно не падало при повышении уровня прогрессионных декалей.

        if savedOutfit is None:
            return None
        
        try:
            isWithAlternateItems = savedOutfit['isWithAlternateItems']
            outfit = savedOutfit['outfit']

            if isinstance(outfit, unicode):
                pushI18nMessage('#userCustomization:notification/outfitResetByConfigUpdate', type=SM_TYPE.InformationHeader, messageData={'header': NOTIFICATION_HEADER})
                del self.config[vehicleDescriptor.name]
                self.saveConfigToFile()
                return None

            if isWithAlternateItems:
                outfitComponent = Outfit(component=self.__dict2outfit(outfit), vehicleCD=vehicleDescriptor.makeCompactDescr())
            else:
                outfitComponent = self.c11nService.getItemByID(32, outfit).getOutfit(season, vehicleDescriptor.makeCompactDescr())
        except:
            pushI18nMessage('#userCustomization:notification/outfitResetByConfigError', type=SM_TYPE.InformationHeader, messageData={'header': NOTIFICATION_HEADER})
            logger.exception('Failed to apply outfit! Tank: %s' % vehicleDescriptor.name)

        if outfitComponent.id in FORBIDDEN_STYLES:
            pushI18nMessage('#userCustomization:notification/outfitResetByForbiddenStyle', type=SM_TYPE.InformationHeader, messageData={'header': NOTIFICATION_HEADER})
            del self.config[vehicleDescriptor.name]
            self.saveConfigToFile()
            return None

        outfitItem = outfitComponent.style
        
        if outfitItem.isProgressive():
            outfitComponent.setProgressionLevel(len(outfitItem.progression.levels))
        if outfitItem.isWithSerialNumber:
            outfitComponent.setSerialNumber('001')

        return outfitComponent
    
    def __outfit2dict(self, customizationOutfit):
        result = {}
        for fieldName in customizationOutfit.fields:
            fieldData = getattr(customizationOutfit, fieldName, customizationOutfit.fields[fieldName].default)
            if isinstance(fieldData, list):
                result[fieldName] = []
                for component in fieldData:
                    if fieldName in CUSTOMIZATION_STRINGS2CLASSES:
                        result[fieldName].append(component.to_dict())
                    else:
                        result[fieldName].append(component)
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
                        result[fieldName].append(CUSTOMIZATION_STRINGS2CLASSES[fieldName](**component))
                    else:
                        result[fieldName].append(component)
            else:
                result[fieldName] = fieldData
        
        return CustomizationOutfit(**result)


g_oucConfig = UserCustomizationConfig()