# Гарантированная загрузка ангара.

from debug_utils import LOG_NOTE
from gui import ClientHangarSpace
from gui.game_control.hangar_switch_controller import SceneSpaceConfig
from gui.shared.personality import ServicesLocator
from helpers import dependency
from skeletons.gui.app_loader import GuiGlobalSpaceID
from skeletons.gui.game_control import IHangarSpaceSwitchController


class NYTHangarOverrider():
    hangarSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    EXCEPT_THIS_SCENES = ['ARMORY_YARD', 'hb_offence', 'hb_defence'] # Исключение для запуска ивент-зависимых ангаров.

    def __init__(self):
        ServicesLocator.appLoader.onGUISpaceEntered += self.onGUISpaceEntered
        ClientHangarSpace._getHangarPath = lambda pld1, pld2: 'spaces/NearYouHangar' if self.hangarSwitchController.currentSceneName not in self.EXCEPT_THIS_SCENES else 'spaces/' + self.hangarSwitchController._sceneSpaceParams[self.hangarSwitchController.currentSceneName].getHangarSpaceId()

    def onGUISpaceEntered(self, spaceID, *args, **kwargs):
        if spaceID != GuiGlobalSpaceID.LOBBY:
            return
        
        if self.hangarSwitchController is not None:
            self.lockHangarOverride('NearYouHangar')

    def lockHangarOverride(self, hangarName):
        for name in self.hangarSwitchController._sceneSpaceParams.iterkeys():
            if name not in self.EXCEPT_THIS_SCENES:
                self.hangarSwitchController._sceneSpaceParams[name] = SceneSpaceConfig(hangarName)

        for isPremium in (True, False):
            self.hangarSwitchController._defaultHangarSpaceConfig.setSpaceIdOverride(isPremium, hangarName)

        self.hangarSwitchController._HangarSpaceSwitchController__isHangarOverridingLocked = True
        LOG_NOTE('Hangar override was locked. Hangar name: ', hangarName, 'Excepted this scenes:', self.EXCEPT_THIS_SCENES)


g_NYTHangarOverrider = NYTHangarOverrider()