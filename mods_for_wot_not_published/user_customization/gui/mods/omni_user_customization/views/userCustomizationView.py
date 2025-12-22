import logging

from CurrentVehicle import g_currentVehicle

from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider, ListDAAPIDataProvider
from gui.Scaleform.framework.entities.View import View

from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.utils import makeSearchableString, sortByFields

from helpers import dependency, i18n, int2roman

from items.components import c11n_components as cn
from items.components.c11n_constants import ApplyArea, CustomizationType, SeasonType
from items.vehicles import makeIntCompactDescrByID

from serializable_types.customizations import CamouflageComponent, DecalComponent, CustomizationOutfit, PaintComponent, PersonalNumberComponent

from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace

from vehicle_outfit.outfit import Outfit

from ..cache import g_oucCache
from ..config import g_oucConfig

logger = logging.getLogger(__name__)

STYLE_SOURCE_ID_TO_CACHE = {'user': g_oucCache.mod_cache, 'ingame': g_oucCache.game_cache}

class UserCustomizationStylesDataProvider(SortableDAAPIDataProvider):
    def __init__(self):
        super(UserCustomizationStylesDataProvider, self).__init__()
        self.__list = None
        self._sort = (('name', False),)
        self.__sortMapping = {'name': lambda v: v['name']}

    @property
    def sortedCollection(self):
        return list(reversed(sortByFields(self._sort, self.__list, self.__sortingMethod))) # Оно изначально сортирует в обратном порядке почему-то, поэтому просто реверсим лист. =)

    def emptyItem(self):
        return

    def pySortOn(self, fields, order):
        super(UserCustomizationStylesDataProvider, self).pySortOn(fields, order)
        if self.__list:
            self.__list = sortByFields(self._sort, self.__list, self.__sortingMethod)
            self.buildList(self.__list)
    
    @property
    def collection(self):
        return self.__list

    def buildList(self, styleVOs):
        self.__list = styleVOs
        self.refresh()

    def clear(self):
        self.__list = []

    def fini(self):
        self.clear()
        self.destroy()

    def __sortingMethod(self, item, field):
        valueGetter = self.__sortMapping[field]
        return valueGetter(item)


class UserCustomizationAlternateItemsDataProvider(ListDAAPIDataProvider):
    def __init__(self): 
        super(UserCustomizationAlternateItemsDataProvider, self).__init__()
        self.__list = None

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return

    def buildList(self, alternateItemVOs):
        self.__list = alternateItemVOs
        self.refresh()


class UserCustomizationViewMeta(View):
    def as_getDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getDP()
            
    def as_getAIDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getAIDP()
            
    def as_setVehicleTitleS(self, vehicleTitleData):
        if self._isDAAPIInited():
            self.flashObject.as_setVehicleTitle(vehicleTitleData)
            
    def as_setAIVisibleS(self, isVisible):
        if self._isDAAPIInited():
            self.flashObject.as_setAIVisible(isVisible)
            
    def as_setStyleInstalledS(self, isInstalled, styleString):
        if self._isDAAPIInited():
            self.flashObject.as_setStyleInstalled(isInstalled, styleString)
            
    def as_setSeasonBarEnabledS(self, isEnabled):
        if self._isDAAPIInited():
            self.flashObject.as_setSeasonBarEnabled(isEnabled)
            
    def as_setNoStyleItemsVisibleS(self, isVisible):
        if self._isDAAPIInited():
            self.flashObject.as_setNoStyleItemsVisible(isVisible)
            
    def as_setNoAIItemsVisibleS(self, isVisible):
        if self._isDAAPIInited():
            self.flashObject.as_setNoAIItemsVisible(isVisible)
            
    def as_setTabsDataS(self, styleTabsData, aiTabsData):
        if self._isDAAPIInited():
            self.flashObject.as_setTabsData(styleTabsData, aiTabsData)


class UserCustomizationView(UserCustomizationViewMeta):
    c11nService = dependency.descriptor(ICustomizationService)
    hangarSpace = dependency.descriptor(IHangarSpace)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(UserCustomizationView, self).__init__()
        self.vehicle = g_currentVehicle.item
        self.__outfit = g_oucConfig.getVehicleOutfit(self.vehicle.descriptor, SeasonType.SUMMER)
        self.__filterText = ''
        self.__selectedStyleTabs = ['2d', 'user']
        self.__selectedAITab = None
        self.__tabsData = ([{'id': '2d', 
                                'label': '#userCustomization:view/styleTypeTabs/2d', 
                                'selected': True},
                            {'id': '3d', 
                                'label': '#userCustomization:view/styleTypeTabs/3d', 
                                'selected': False}],
                            [{'id': 'user',
                                'label': '#userCustomization:view/styleSourceTabs/user',
                                'selected': True},
                            {'id': 'ingame',
                                'label': '#userCustomization:view/styleSourceTabs/ingame',
                                'selected': False}])
        self.__aiTabsData = []

    @property
    def outfit(self):
        return self.__outfit

    def _populate(self):
        super(UserCustomizationView, self)._populate()
        self._stylesDP = UserCustomizationStylesDataProvider()
        self._alternateItemsDP = UserCustomizationAlternateItemsDataProvider()
        self._stylesDP.setFlashObject(self.as_getDPS())
        self._alternateItemsDP.setFlashObject(self.as_getAIDPS())
        self.as_setVehicleTitleS(self.__setVehicleTitle())
        self.py_selectItem(None, SeasonType.SUMMER)

    def __setVehicleTitle(self):
        return {'tankTierStr': text_styles.grandTitle(int2roman(self.vehicle.level)), 
                'tankNameStr': text_styles.grandTitle(self.vehicle.userName), 
                'tankTierStrSmall': text_styles.promoTitle(int2roman(self.vehicle.level)), 
                'tankNameStrSmall': text_styles.promoTitle(self.vehicle.userName), 
                'typeIconPath': getTypeBigIconPath(self.vehicle.type, self.vehicle.isElite), 
                'isElite': self.vehicle.isElite,
                'showInfoIcon': False}

    def __getItemByID(self, itemTypeID, itemID):
        intCD = makeIntCompactDescrByID('customizationItem', itemTypeID, itemID)
        return self.itemsCache.items.getItemByCD(intCD)

    def __updateStyleTabContentData(self):
        data = []

        styleType, styleSource = self.__selectedStyleTabs
        for styleID, styleInfo in STYLE_SOURCE_ID_TO_CACHE[styleSource]['styles'][styleType].items():
            if self.__selectedStyleTabs[0] == '3d' and not styleInfo.mayInstall(self.vehicle):
                continue
            styleInfoDict = {'id': styleID,
                             'intCD': styleInfo.intCD,
                             'name': styleInfo.userName if styleInfo.userName else i18n.makeString('#userCustomization:view/stylesCarousel/styleWithoutName', styleID=styleID), 
                             'iconPath': styleInfo.icon if styleInfo.icon else '../maps/icons/valberton/ouc_no_style_image.png',
                             'isWide': styleInfo.isWide()}
            if self.__filterText:
                if not self.__filterText in makeSearchableString(styleInfoDict['name']):
                    continue
            data.append(styleInfoDict)

        self.as_setNoStyleItemsVisibleS(not data)
        self._stylesDP.buildList(data)

    def __updateAITabContentData(self):
        ai_data = []
        ai_tabs_data = {}

        self.as_setAIVisibleS(False)
        if self.__outfit and self.__outfit.style:
            self.as_setAIVisibleS(bool(self.__outfit.style.alternateItems))
            
            if self.__outfit.style.alternateItems:
                for itemTypeID, itemIDs in self.__outfit.style.alternateItems.items():
                    for itemID in itemIDs:
                        item = self.__getItemByID(itemTypeID, itemID)

                        if item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL: # Пока проекционные декали не поддерживаются.
                            continue

                        if item.itemTypeID not in ai_tabs_data:
                            ai_tabs_data[item.itemTypeID] = ({'id': '%s_wide' % item.itemTypeName if item.isWide() else item.itemTypeName,
                                                              'label': '#item_types:customization/plural/%s' % item.itemTypeName,
                                                              'linkage': str(item.itemTypeID),
                                                              'selected': False})
                                        
                        if item.itemTypeID == self.__selectedAITab:
                            itemIcon = '../../' + item.texture
                            
                            if item.itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE and item.palettes[0] != [4278190335, 4278255360, 4294901760, 4278190080]: # Список с числами - эталон FullRGB палитры.
                                itemIcon = item.icon

                            ai_data.append({'id': item.id, 
                                            'iconPath': itemIcon,
                                            'typeID': item.itemTypeID, 
                                            'isWide': item.isWide()})

        self.__aiTabsData = [tabData for tabData in ai_tabs_data.values()]
        self.__updateSelectedTab()
        self.as_setNoAIItemsVisibleS(not ai_data)
        self._alternateItemsDP.buildList(ai_data)
        
    def __updateSelectedTab(self):
        for tabsDataIdx, tabsData in enumerate(self.__tabsData):
            for tabIdx, tab in enumerate(tabsData):
                self.__tabsData[tabsDataIdx][tabIdx]['selected'] = False
                if tab.get('id') in self.__selectedStyleTabs:
                    self.__tabsData[tabsDataIdx][tabIdx]['selected'] = True
        
        self.as_setTabsDataS(self.__tabsData, self.__aiTabsData)

    def __updateView(self):
        # Проверям, есть ли танк в конфиге мода.
        isOutfitInConfig = g_oucConfig.isOutfitInConfig(self.vehicle.descriptor.name)

        if isOutfitInConfig:
            styleString = i18n.makeString('#userCustomization:window/styleInstalled', styleName=self.__outfit.style.userString)
            isOutfitForAllSeasons = True

            # Мега-тупая система, но она лучше всего помогает понять, есть ли у стиля разные варианты для сезонов.
            for season, outfit in self.__outfit.style.outfits.items():
                if season in SeasonType.COMMON_SEASONS:
                    if outfit != self.__outfit.style.outfits[1]:
                       isOutfitForAllSeasons = False
                       break
            
            self.as_setSeasonBarEnabledS(not isOutfitForAllSeasons)
        else:
            styleString = '#userCustomization:window/styleNotInstalled'
            self.as_setSeasonBarEnabledS(False)

        self.as_setStyleInstalledS(isOutfitInConfig, styleString)
        self.__updateSelectedTab()
        self.__updateStyleTabContentData()
        self.__updateAITabContentData()
        return
    
    def __createCamouflageComponents(self, camoID):
        camos = [CamouflageComponent(id=camoID, appliedTo=ApplyArea.HULL),
             CamouflageComponent(id=camoID, appliedTo=ApplyArea.TURRET),
             CamouflageComponent(id=camoID, appliedTo=ApplyArea.GUN)]
        
        return Outfit(component=CustomizationOutfit(camouflages=camos), vehicleCD=self.vehicle.strCD)
    
    def __createDecalComponents(self, emblemID, inscriptionID, vehDescr):
        decals = []
        emblemRegions, inscriptionRegions = cn.getAvailableDecalRegions(vehDescr)

        if emblemID and emblemRegions:
            decals.append(DecalComponent(id=emblemID, appliedTo=emblemRegions))
        if inscriptionID and inscriptionRegions:
            decals.append(DecalComponent(id=inscriptionID, appliedTo=inscriptionRegions))

        return Outfit(component=CustomizationOutfit(decals=decals), vehicleCD=self.vehicle.strCD)
    
    def __createPaintComponents(self, paintID):
        paints = [PaintComponent(id=paintID, appliedTo=ApplyArea.HULL),
                PaintComponent(id=paintID, appliedTo=ApplyArea.TURRET),
                PaintComponent(id=paintID, appliedTo=ApplyArea.GUN)]

        return Outfit(component=CustomizationOutfit(paints=paints), vehicleCD=self.vehicle.strCD)
    
    def __createPNumberComponents(self, pNumberID, vehDescr):
        p_numbers = []
        _, inscriptionRegions = cn.getAvailableDecalRegions(vehDescr)

        if pNumberID and inscriptionRegions:
            p_numbers.append(PersonalNumberComponent(id=pNumberID, number='001', appliedTo=inscriptionRegions))

        return Outfit(component=CustomizationOutfit(personal_numbers=p_numbers), vehicleCD=g_currentVehicle.item.strCD)
    
    # TODO: Доделать к релизу
    # def __createProjectionDecalComponents(self, paintID):
    #     paints = [ProjectionDecalComponent(id=paintID, appliedTo=ApplyArea.HULL),
    #             ProjectionDecalComponent(id=paintID, appliedTo=ApplyArea.TURRET),
    #             ProjectionDecalComponent(id=paintID, appliedTo=ApplyArea.GUN)]
    #     
    #     return Outfit(component=CustomizationOutfit(paints=paints), vehicleCD=self.vehicle.strCD)

    def py_getOutfitID(self):
        if self.__outfit:
            return self.__outfit.id
        else:
            return None

    def py_selectItem(self, itemID, seasonID):
        try:
            self.__selectedAITab = None
            vehicleCD = self.vehicle.strCD

            if itemID:
                item = self.__getItemByID(CustomizationType.STYLE, itemID)
                outfit = item.getOutfit(seasonID, vehicleCD)

                if item.isProgressive:
                    outfit.setProgressionLevel(item.maxProgressionLevel)
                if item.isWithSerialNumber:
                    outfit.setSerialNumber('001')
            else:
                outfit = self.vehicle.getOutfit(seasonID)
            
            self.__outfit = outfit
            self.hangarSpace.updateVehicleOutfit(self.__outfit)
            if g_oucConfig.getDevModeState():
                logger.info('Applied styleID: %s' % itemID)
        except:
            self.hangarSpace.updateVehicle(self.vehicle)
            logger.exception('Failed to apply style. ID=%s' % itemID)
        
        self.__updateView()

    def py_selectAlternateItem(self, itemTypeID, itemID, seasonID):
        try:
            if itemID:
                if itemTypeID == GUI_ITEM_TYPE.PAINT:
                    self.__outfit = self.__outfit.patch(self.__createPaintComponents(itemID))
                elif itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
                    self.__outfit = self.__outfit.patch(self.__createCamouflageComponents(itemID))
                elif itemTypeID == GUI_ITEM_TYPE.EMBLEM:
                    self.__outfit = self.__outfit.patch(self.__createDecalComponents(itemID, 0, self.vehicle.descriptor))
                elif itemTypeID == GUI_ITEM_TYPE.INSCRIPTION:
                    self.__outfit = self.__outfit.patch(self.__createDecalComponents(0, itemID, self.vehicle.descriptor))
                elif itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
                    self.__outfit = self.__outfit.patch(self.__createPNumberComponents(itemID, self.vehicle.descriptor))
            else:
                logger.warning('Unknown alternate item type to replace: itemTypeID')
            
            self.hangarSpace.updateVehicleOutfit(self.__outfit)
        except:
            self.hangarSpace.updateVehicle(self.vehicle)
            logger.exception('Failed to apply style. ID=%s' % itemID)
    
    def py_selectStyleTab(self, tabDataID, tabID):
        self.__selectedStyleTabs[tabDataID] = tabID
        self.__updateView()
    
    def py_selectAITab(self, tabLinkage):
        self.__selectedAITab = int(tabLinkage)
        self.__updateView()
    
    def py_setFilter(self, filterText):
        self.__filterText = makeSearchableString(filterText)
        self.__updateView()