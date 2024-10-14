import BigWorld
from OpenModsCore import overrideMethod
from helpers.EffectsList import _FlashBangEffectDesc
from Math import Vector4Provider, Vector4Animation
from functools import partial

renderSettings = BigWorld.WGRenderSettings()
print renderSettings.flashBangAnimation

def nigger():
    renderSettings = BigWorld.WGRenderSettings()
    animation = Vector4Animation()
    keyframes = []
    keyframes.append((0.0, Vector4Provider((0, 0, 0, 0))))
    keyframes.append((0.1, Vector4Provider((1, 1, 1, 0.5))))
    keyframes.append((1.1, Vector4Provider((0, 0, 0, 0))))
    animation.keyframes = keyframes
    #animation.duration = 2
    renderSettings.flashBangAnimation(animation)
    BigWorld.callback(5, partial(nigger2, animation))

def nigger2(anim):
    renderSettings.removeFlashBangAnimation(anim)
    

nigger()


#@overrideMethod(_FlashBangEffectDesc, 'create')
def nullEffect(base, self, model, list, args):
    args['isPlayerVehicle'] = True
    args['showShockWave'] = True
    args['showFriendlyFlashBang'] = False
    args['showFlashBang'] = True
    self._keyframes = []
    self._keyframes.append((0.0, Vector4Provider((0, 0, 0, 0))))
    self._keyframes.append((0.1, Vector4Provider((1, 0, 0, 0.5))))
    self._keyframes.append((1.1, Vector4Provider((0, 0, 0, 0))))
    #print 'model =', model
    #print 'list =', list
    #print 'args =', args
    #print 'keyframes =', self._keyframes
    base(self, model, list, args)


#helpers.EffectsList._FlashBangEffectDesc.create = nullEffect