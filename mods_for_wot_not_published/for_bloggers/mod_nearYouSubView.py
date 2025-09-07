import BigWorld, CGF, GUI, Event
from AvatarInputHandler import cameras
from ClientSelectableCameraObject import ClientSelectableCameraObject
from cgf_components.hover_component import IsHoveredComponent
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import tickGroup, onAddedQuery, onRemovedQuery, registerManager, Rule, registerRule
from constants import CollisionFlags
from frameworks.wulf import WindowLayer
from GenericComponents import VSEComponent
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.View import View
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import ColliderTypes


@registerComponent
class NYTSelectionComponent(object):
    editorTitle = 'Selection'
    category = 'Common'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    selectionID = ComponentProperty(type=CGFMetaTypes.STRING, editorName='selectionID')
    isSelectable = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='isSelectable')

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
        res = BigWorld.wg_collideDynamicStatic(self.spaceID, wpoint, wpoint + ray * 1500, skipFlags, -1, -1, ColliderTypes.HANGAR_FLAG)
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
                selectionComponent.onClickAction(selectionComponent)


@registerRule
class NYTSelectionRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(NYTHoverManager)
    def reg1(self):
        return
    
    @registerManager(NYTClickManager)
    def reg3(self):
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

g_entitiesFactories.addSettings(ViewSettings('NearYouTeamSubViewUI', NearYouTeamSubView, 'nearYouTeamSubView.swf', WindowLayer.SUB_VIEW, 'NearYouTeamSubViewUI', ScopeTemplates.LOBBY_SUB_SCOPE))