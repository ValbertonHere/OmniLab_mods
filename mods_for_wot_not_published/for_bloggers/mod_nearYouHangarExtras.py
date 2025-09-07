# Экстры для прототипа ангара Near_You Team

import BigWorld, CGF, GUI, Event
from AvatarInputHandler import cameras
from constants import CollisionFlags
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import tickGroup, onAddedQuery, onRemovedQuery, registerManager, Rule, registerRule
from cgf_components.hangar_camera_manager import HangarCameraManager
from cgf_components.hover_component import IsHoveredComponent
from ClientSelectableCameraObject import ClientSelectableCameraObject
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from debug_utils import LOG_NOTE, LOG_ERROR, LOG_CURRENT_EXCEPTION
from frameworks.wulf import WindowLayer
from GenericComponents import VSEComponent
from gui.shared.event_dispatcher import showShop
from gui.game_loading.resources.consts import Milestones
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.entities.View import View
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from items import vehicles
from items.customizations import ProjectionDecalComponent, CustomizationOutfit, CamouflageComponent, PaintComponent, InsigniaComponent
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.app_loader import IAppLoader
from PlayerEvents import g_playerEvents
from vehicle_outfit.outfit import Outfit
from vehicle_systems.tankStructure import ColliderTypes

@registerComponent
class NYTSelectionComponent(object):
    editorTitle = 'Selection'
    category = 'Common'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    selectionID = ComponentProperty(type=CGFMetaTypes.STRING, editorName='selectionID')

    def __init__(self):
        super(NYTSelectionComponent, self).__init__()
        self.onClickAction = Event.Event()


class NYTHoverManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    @onAddedQuery(VSEComponent, IsHoveredComponent)
    def onIsHoveredAdded(self, vseComponent, *args):
        vseComponent.context.onGameObjectHoverIn()

    @onRemovedQuery(VSEComponent, IsHoveredComponent)
    def onIsHoveredRemoved(self, vseComponent, *args):
        vseComponent.context.onGameObjectHoverOut()

    @onRemovedQuery(CGF.GameObject, NYTSelectionComponent)
    def onIsSelectableRemoved(self, gameObject, *args):
        if gameObject.findComponentByType(IsHoveredComponent):
            gameObject.removeComponentByType(IsHoveredComponent)

    @tickGroup(groupName='Simulation')
    def tick(self):
        gameObjectID = None
        if GUI.mcursor().inWindow and GUI.mcursor().inFocus and self._hangarSpace.isSelectionEnabled and self._hangarSpace.isCursorOver3DScene:
            gameObjectID = self.__getGameObjectUnderCursor()
        hoveredGameObject = CGF.Query(self.spaceID, (CGF.GameObject, IsHoveredComponent))
        for gameObject, _ in hoveredGameObject:
            if gameObject.id != gameObjectID:
                gameObject.removeComponentByType(IsHoveredComponent)
            else:
                return

        if gameObjectID == 0:
            return
        else:
            hoverableGameObjects = CGF.Query(self.spaceID, (CGF.GameObject, NYTSelectionComponent))
            for gameObject, _ in hoverableGameObjects:
                if gameObject.id == gameObjectID:
                    gameObject.createComponent(IsHoveredComponent)

            return

    def __getGameObjectUnderCursor(self):
        cursorPosition = GUI.mcursor().position
        ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
        skipFlags = CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE | CollisionFlags.TRIANGLE_NOCOLLIDE
        res = BigWorld.collideDynamicStatic(self.spaceID, wpoint, wpoint + ray * 1500, skipFlags, -1, -1, ColliderTypes.HANGAR_FLAG)
        if res is not None:
            return res[5]
        else:
            return


class NYTClickManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, *args):
        super(NYTClickManager, self).__init__(*args)
        self._selectedGO = None
        return

    def activate(self):
        self._hangarSpace.onMouseDown += self._onMouseDown
        self._hangarSpace.onMouseUp += self._onMouseUp

    def deactivate(self):
        self._hangarSpace.onMouseDown -= self._onMouseDown
        self._hangarSpace.onMouseUp -= self._onMouseUp

    def _onMouseDown(self):
        clickQuery = CGF.Query(self.spaceID, (CGF.GameObject, IsHoveredComponent, NYTSelectionComponent))
        for go, _, __ in clickQuery:
            self._selectedGO = go

    def _onMouseUp(self):
        clickQuery = CGF.Query(self.spaceID, (CGF.GameObject, IsHoveredComponent, NYTSelectionComponent))
        for go, _, selectionComponent in clickQuery:
            if self._selectedGO == go:
                selectionComponent.onClickAction(selectionComponent.selectionID)


@registerRule
class NYTSelectionRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(NYTHoverManager)
    def reg1(self):
        return
    
    @registerManager(NYTClickManager)
    def reg2(self):
        return


class NearYouTeamSubView(LobbySelectableView, View):
    __background_alpha__ = 0.0
    
    def __init__(self, _=None):
        LobbySelectableView.__init__(self, 0)

    def _populate(self):
        LobbySelectableView._populate(self)

    def _dispose(self):
        g_eventDispatcher.loadHangar()
        ClientSelectableCameraObject.switchCamera()
        LobbySelectableView._dispose(self)
        return
        
    def onViewClose(self, _):
        self.destroy()


class NearYouHangarExtras():
    hangarSpace = dependency.descriptor(IHangarSpace)
    appLoader = dependency.instance(IAppLoader)
    
    def __init__(self):
        self.__cameraEntity = None
        self.__vehStylePreviewEnt = None

        g_playerEvents.onLoadingMilestoneReached += self.onHangarLoaded
        g_entitiesFactories.addSettings(ViewSettings('NearYouTeamSubViewUI', NearYouTeamSubView, 'nearYouTeamSubView.swf', WindowLayer.SUB_VIEW, 'NearYouTeamSubViewUI', ScopeTemplates.LOBBY_SUB_SCOPE))

    def onGameObjectClicked(self, selectionID):
        cameraManager = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
        if cameraManager.getCurrentCameraName() != 'NYTCamera' and selectionID != 'nearyou_shop':
            ClientSelectableCameraObject.switchCamera(self.__cameraEntity, 'NYTCamera')
            app = self.appLoader.getApp()
            app.loadView(SFViewLoadParams('NearYouTeamSubViewUI'))
            return
        
        handler = self.callNYTTVHandlerBySelectionID(selectionID)
        if handler is not None:
            handler()

    def onHangarLoaded(self, milestoneName):
        if milestoneName == Milestones.HANGAR_READY:
            if self.hangarSpace.spacePath.split('/')[-1].lower() == 'nearyouhangar':
                try:
                    LOG_NOTE('Catching entities...')
                    for entity in BigWorld.entities.values(): # Проверка на конкретный тип объекта без наследуемых классов.
                        if type(entity) is ClientSelectableCameraVehicle:
                            self.__onVehicleStylePreviewEntityCatched(entity)
                        elif type(entity) is ClientSelectableCameraObject:
                            self.__cameraEntity = entity

                    LOG_NOTE('Catching prefabs...')
                    nytQuery = CGF.Query(self.hangarSpace.spaceID, (CGF.GameObject, NYTSelectionComponent))
                    for _, selectionComponent in nytQuery:
                        selectionComponent.onClickAction += self.onGameObjectClicked

                    LOG_NOTE('Complete!')
                except:
                    LOG_ERROR('Error during loading hangar extras, send lines below to developer. Telegram: @lrvval.')
                    LOG_CURRENT_EXCEPTION()

    def callNYTTVHandlerBySelectionID(self, selectionID):
        handlersDict = {'TV_Near': self.__onNearTVClicked,
                        'TV_Dyff': self.__onDyffTVClicked,
                        'TV_C1ymba': self.__onClymbaTVClicked,
                        'TV_Pomidop': self.__onIIomidopTVClicked,
                        'TV_Guit88man': self.__onGuitmanTVClicked,
                        'nearyou_shop': self.__onNYShopClicked}
        
        if selectionID not in handlersDict:
            LOG_ERROR('NYT TV Handler not found.')
            return None
        else:
            return handlersDict[selectionID]

    def __onVehicleStylePreviewEntityCatched(self, ent):
        self.__vehStylePreviewEnt = ent
        self.__vehStylePreviewEnt.setEnable(False)
        # self.__vehStylePreviewEnt.onMouseClick = self.__onVehicleStylePreviewEntityClicked

        styleId = 31289
        modifications = [(4)]
        insignias = [InsigniaComponent(31016, 4096)]
        camos = [CamouflageComponent(31247, 1, 272, 0)]
        paints = [PaintComponent(31257, 16384),
                  PaintComponent(31258, 4096),
                  PaintComponent(31259, 1),
                  PaintComponent(31260, 272)]
        projectionDecals = [ProjectionDecalComponent(id=31259, tags=[('front', 'safe', 'formfactor_square')]),
                            ProjectionDecalComponent(id=31261, tags=[('formfactor_square', 'direction_left_to_right', 'safe', 'right')]),
                            ProjectionDecalComponent(id=31261, tags=[('left', 'formfactor_square', 'direction_right_to_left', 'safe')])]
        stylePreviewOutfit = Outfit(component=CustomizationOutfit(modifications=modifications, paints=paints, camouflages=camos, projection_decals=projectionDecals, styleId=styleId, insignias=insignias))

        self.__vehStylePreviewEnt.recreateVehicle(typeDescriptor=vehicles.VehicleDescr(typeName='ussr:R45_IS-7'), outfit=stylePreviewOutfit)

    def __onVehicleStylePreviewEntityClicked(self):
        showShop('https://shop-ru-cdn.lesta.ru/bob4/bob4/items/platform_ig_1812')
        return True
    
    def __onNearTVClicked(self):
        BigWorld.wg_openWebBrowser('https://www.youtube.com/@NearYouHR')

    def __onDyffTVClicked(self):
        BigWorld.wg_openWebBrowser('https://www.youtube.com/channel/UCmPzycVuPeuYM3sbPw2AvFw')
        
    def __onClymbaTVClicked(self):
        BigWorld.wg_openWebBrowser('https://www.youtube.com/@C1ymba')
        
    def __onIIomidopTVClicked(self):
        BigWorld.wg_openWebBrowser('https://www.youtube.com/c/IIomudopMSK')
        
    def __onGuitmanTVClicked(self):
        BigWorld.wg_openWebBrowser('https://www.twitch.tv/guit88man')
    
    def __onNYShopClicked(self):
        BigWorld.wg_openWebBrowser('https://nearyou-shop.ru/')
    
g_nearYouHangarExtras = NearYouHangarExtras()