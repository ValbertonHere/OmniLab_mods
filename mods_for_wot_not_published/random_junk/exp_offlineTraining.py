from gui.prb_control.entities.base.legacy.ctx import SetTeamStateCtx
from gui.prb_control.entities.base.legacy.listener import ILegacyListener
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.trainings.TrainingRoomBase import TrainingRoomBase
from Avatar import PlayerAvatar
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.prb_control.items.prb_items import PlayerPrbInfo
from gui.prb_control import prb_getters
from constants import PREBATTLE_UPDATE
import zlib
from ClientArena import ClientArena

from OpenModsCore import overrideMethod

#appLoader = dependency.instance(IAppLoader)
#app = appLoader.getApp()
#hangarSWF = app.containerManager.getContainer(WindowLayer.VIEW).getChildContainer(5).getView()
FakeBot = "x\x9ck`\xd2\xf0\xfa\xfb\xb1\x83!\x94_1O\x8c\x81\x8d\x81\t\x88\xc5\x19\x84\x18\x18\n\x19C\xe5\x9d\xf2K|\xf2\x93\xe3\r\x15\x94s\x13\x0b\x8a\xe3K\x8a\x123\xf32\xf3\xd2\xad\x92\xf2K\xfc\x12sS\x0b\x99\xbc\x99\xbc\x19\x81\x90\xc1\x9b!\x94\xc1\x1b\x02\x19k\x0b\x99\xbd\x19\x92\xe3\x9d\xc2\x0b\xb8\x1c\x8b\x8a\x12+\xb9\nYb[\x83\nYk\x0b\xd9@\n\xda\n\xd9CYX\x046\xb3\x14r\x80\xf4d0\xc5\xc6\xb6\x15r\x02eNd\x80\xd5q\x81\x14\x95\x14r\xeb\x01\x00\x0c.'\xd2"
#BigWorld.player().arena.update(2, FakeBot)
print BigWorld.player().arena.vehicles

#@overrideMethod(ClientArena, '__onVehicleAddedUpdate')
def ClientArena__onVehicleAddedUpdate(base, self, argStr):
    print argStr
    base(self, argStr)
    
#@overrideMethod(TrainingRoomBase, 'onRostersChanged')
def TrainingRoomBase_onRostersChanged(base, self, entity, rosters, full):
    base(self, entity, rosters, full)
    print '|-'
    print entity
    print '-'
    print rosters
    print '-'
    print full
    print '-'

class Nigger(ILegacyListener):
    
    @adisp_process
    def _nig(self):
        yield self.prbDispatcher.sendPrbRequest(SetTeamStateCtx(1, True, isForced=True))
    
    @adisp_process
    def _nig2(self):
        yield self.prbDispatcher.sendPrbRequest(SetTeamStateCtx(2, True, isForced=True))

#nigger = Nigger()
#nigger._nig()
#nigger._nig2()