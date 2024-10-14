# Попытка в кастомную треню. Не тестировалось.

from gui.shared.utils.key_mapping import getBigworldNameFromKey
from gui.Scaleform.daapi.view.lobby.trainings import Trainings

g_Trainings = Trainings.Trainings()

def onhandleKeyEvent(event):
    key = getBigworldNameFromKey(event.key)
    if key == 'KEY_F3':
        #Создание комнаты (но почему то не работает в ангаре)
        g_Trainings.createTrainingRequest()
    if key == 'KEY_F4':
        #Подключение к комнате (1 замени на id комнаты)
        g_Trainings.joinTrainingRequest(1)
    if key == 'KEY_F5':
        #Выход из комнаты
        g_Trainings._doLeave(True)
    return None



from gui import InputHandler
InputHandler.g_instance.onKeyDown += onhandleKeyEvent


'''
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates, ComponentSettings
from frameworks.wulf import WindowLayer
from skeletons.gui.app_loader import IAppLoader
from helpers import dependency
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.prb_control.entities.training.legacy.ctx import TrainingSettingsCtx
from gui.shared import events
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.shared.event_bus import EVENT_BUS_SCOPE

appLoader = dependency.instance(IAppLoader)
app = appLoader.getApp()
subView = app.containerManager.getContainer(WindowLayer.VIEW).getChildContainer(5).getView()

settings = TrainingSettingsCtx()
settings.setArenaTypeID(0)
settings.setRoundLen(22*60)
settings.setOpened(True)
settings.setComment('TEST')

subView.fireEvent(events.TrainingSettingsEvent(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, ctx={'settings': settings}), scope=EVENT_BUS_SCOPE.LOBBY)
'''