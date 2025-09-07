from time import sleep
from BigWorld import callback
from functools import partial
import GUI
from debug_utils import LOG_DEBUG
from gui import g_guiResetters
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.shared.utils import graphics
from helpers import getClientOverride
from gui.Scaleform.daapi.view.meta.DAAPISimpleContainerMeta import DAAPISimpleContainerMeta

class GameLoadingMeta(DAAPISimpleContainerMeta):

    def as_setLocaleS(self, locale):
        return self.flashObject.as_setLocale(locale) if self._isDAAPIInited() else None

    def as_setVersionS(self, version):
        return self.flashObject.as_setVersion(version) if self._isDAAPIInited() else None

    def as_setInfoS(self, info):
        return self.flashObject.as_setInfo(info) if self._isDAAPIInited() else None

    def as_setProgressS(self, progress):
        return self.flashObject.as_setProgress(progress) if self._isDAAPIInited() else None

    def as_updateStageS(self, width, height, scale):
        return self.flashObject.as_updateStage(width, height, scale) if self._isDAAPIInited() else None

class GameLoading(ExternalFlashComponent, GameLoadingMeta):

    def __init__(self):
        super(GameLoading, self).__init__(ExternalFlashSettings('gameLoading', 'gameLoadingApp.swf', 'root.main', 'registerGameLoading'))
        self.createExternalComponent()
        self.active(True)

    def afterCreate(self):
        super(GameLoading, self).afterCreate()
        self.as_setLocaleS(getClientOverride())
        self.as_setVersionS('#wek_gameLoading:game_version')
        self.flashObject.copyright.textField.text = '#wek_gameLoading:copyright'
        self._updateStage()
        return

    def onUpdateStage(self):
        self._updateStage()

    def onLoad(self, dataSection):
        g_guiResetters.add(self.onUpdateStage)
        self.active(True)

    def onDelete(self):
        g_guiResetters.discard(self.onUpdateStage)
        self.close()

    def setProgress(self, value):
        self.as_setProgressS(value)

    def addMessage(self, message):
        LOG_DEBUG(message)

    def reset(self):
        self.as_setProgressS(0)

    def _updateStage(self):
        width, height = GUI.screenResolution()
        scaleLength = len(graphics.getInterfaceScalesList([width, height]))
        self.as_updateStageS(width, height, scaleLength - 1)

    def getChildren(self):
        return (self.flashObject.background, self.flashObject.wotLogo, self.flashObject.copyright, 
                self.flashObject.form, self.flashObject.ageRating, self.flashObject.versionTF)