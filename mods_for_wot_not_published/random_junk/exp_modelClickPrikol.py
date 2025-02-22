from CurrentVehicle import g_currentPreviewVehicle
from items import vehicles
from HeroTank import HeroTank
from skeletons.gui.game_control import IHeroTankController, ILimitedUIController
from helpers import dependency
from gui.game_control.hero_tank_controller import HeroTankController
from gui.limited_ui.lui_controller import LimitedUIController
from gui.limited_ui.lui_rules_storage import LUI_RULES
#from gui.limited_ui.lui_rules_storage import LuiRules
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from vehicle_outfit.outfit import Outfit
from items.customizations import parseOutfitDescr, CustomizationOutfit, CamouflageComponent, AttachmentComponent, PaintComponent
from ClientSelectableCameraObject import ClientSelectableCameraObject
import CGF

niggerID = BigWorld.createEntity('ClientSelectableCameraObject', BigWorld.player().hangarSpace.spaceID, 0, BigWorld.player().position + (0, 10, 20), (0, 0, 0), {'modelName': 'content/Environment/hd_env_EU_001_Karelia_Stones/normal/lod0/hd_env_EU_001_karelia_stones_03.model', 
                                                                                                                                 'clickSoundName': 'play'})

def onLoad(go):
    print dir(go)
    
CGF.loadGameObject('content/OmniPrefabs/OmniCamera.prefab', BigWorld.player().hangarSpace.spaceID, BigWorld.player().position + (0, 10, 20), onLoad)


def onClick(self):
    if 'hd_env_EU_001_karelia_stones_03' in self.modelName:
        ClientSelectableCameraObject.switchCamera(self, 'OmniPrefabCamera')
    else:
        base(self)
    return self.state != CameraMovementStates.FROM_OBJECT

#ClientSelectableCameraObject.onMouseClick = base
base = ClientSelectableCameraObject.onMouseClick
ClientSelectableCameraObject.onMouseClick = onClick

class nig():
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _limitedUIController = dependency.descriptor(ILimitedUIController)

#HeroTankController.isEnabled = lambda _: True
#LimitedUIController.isRuleCompleted = lambda self, ruleID: True if ruleID == LUI_RULES.HeroTank else not self.isEnabled

def onTankClick(self):
    BigWorld.wg_openWebBrowser('https://www.youtube.com/')
    return self.state != CameraMovementStates.FROM_OBJECT

#HeroTank.onMouseClick = onTankClick

camos = [CamouflageComponent(518, 2, 4368, 0)]#, CamouflageComponent(id=camoId, appliedTo=256), CamouflageComponent(id=camoId, appliedTo=4096)]
paints = [PaintComponent(262, 30583)]
custOutfit = Outfit(component=CustomizationOutfit(camouflages=camos, paints=paints, styleId=128))

def debugReloadHero(heroName):
    for e in BigWorld.entities.values():
        if isinstance(e, HeroTank):
            print e.selectionId
            heroDescriptor = vehicles.VehicleDescr(typeName=heroName)
            e._HeroTank__heroTankCD = vehicles.makeVehicleTypeCompDescrByName(heroName)
            e.recreateVehicle(heroDescriptor, outfit=custOutfit)
            return

#print nig()._limitedUIController
debugReloadHero('ussr:R45_IS-7')
