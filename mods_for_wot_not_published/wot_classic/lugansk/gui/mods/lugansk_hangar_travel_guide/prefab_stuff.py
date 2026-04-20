import BigWorld, CGF, GUI, Event, logging

from AvatarInputHandler import cameras

from constants import CollisionFlags
from cgf_components.highlight_component import HighlightComponent
from cgf_components.hover_component import IsHoveredComponent
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import Rule, onAddedQuery, onRemovedQuery, registerManager, registerRule, tickGroup

from GenericComponents import DynamicModelComponent

from helpers import dependency

from skeletons.gui.shared.utils import IHangarSpace

from vehicle_systems.tankStructure import ColliderTypes

logger = logging.getLogger(__name__)

@registerComponent
class LuganskSelectionComponent(object):
    editorTitle = 'Selection'
    category = 'Common'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

    def __init__(self):
        super(LuganskSelectionComponent, self).__init__()
        self.onClickAction = Event.Event()


class LuganskHoverManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    @onAddedQuery(DynamicModelComponent, HighlightComponent, IsHoveredComponent)
    def onIsHoveredAdded(self, dynamicModel, highlightComponent,*args):
        BigWorld.setEdgeDetectEdgeColor(3, highlightComponent.color)
        BigWorld.addEdgeDetectDynamicModel(dynamicModel)
        self.__enableGroupDraw(True, highlightComponent.groupName)

    @onRemovedQuery(DynamicModelComponent, HighlightComponent, IsHoveredComponent)
    def onIsHoveredRemoved(self, dynamicModel, highlightComponent, *args):
        BigWorld.delEdgeDetectDynamicModel(dynamicModel)
        self.__enableGroupDraw(False, highlightComponent.groupName)

    @onRemovedQuery(CGF.GameObject, LuganskSelectionComponent)
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
            hoverableGameObjects = CGF.Query(self.spaceID, (CGF.GameObject, LuganskSelectionComponent))
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

    def __enableGroupDraw(self, enable, groupName):
        highlightQuery = CGF.Query(self.spaceID, (HighlightComponent, DynamicModelComponent))
        for highlightComponent, dynamicModelComponent in highlightQuery:
            if highlightComponent.groupName and highlightComponent.groupName == groupName:
                if enable and highlightComponent.isActive:
                    BigWorld.addEdgeDetectDynamicModel(dynamicModelComponent)
                else:
                    BigWorld.delEdgeDetectDynamicModel(dynamicModelComponent)


class LuganskClickManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, *args):
        super(LuganskClickManager, self).__init__(*args)
        self._selectedGO = None
        return

    def activate(self):
        self._hangarSpace.onMouseDown += self._onMouseDown
        self._hangarSpace.onMouseUp += self._onMouseUp

    def deactivate(self):
        self._hangarSpace.onMouseDown -= self._onMouseDown
        self._hangarSpace.onMouseUp -= self._onMouseUp

    def _onMouseDown(self):
        clickQuery = CGF.Query(self.spaceID, (CGF.GameObject, IsHoveredComponent, LuganskSelectionComponent))
        for go, _, __ in clickQuery:
            self._selectedGO = go

    def _onMouseUp(self):
        clickQuery = CGF.Query(self.spaceID, (CGF.GameObject, IsHoveredComponent, LuganskSelectionComponent))
        for go, _, selectionComponent in clickQuery:
            if self._selectedGO == go:
                selectionComponent.onClickAction()


@registerRule
class LuganskSelectionRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(LuganskHoverManager)
    def reg1(self):
        return
    
    @registerManager(LuganskClickManager)
    def reg2(self):
        return