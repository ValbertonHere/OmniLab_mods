from decimal import Decimal
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.shared.items_parameters.params_helper import getParameters
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class LegacyVehicleParams(BaseDAAPIComponent):
    PARAMS = ['maxHealth', 'vehicleWeight', 'enginePower', 'speedLimits', 'chassisRotationSpeed',
            'hullArmor', 'turretArmor', 'damage', 'piercingPower', 'reloadTime', 'turretRotationSpeed',
            'circularVisionRadius', 'radioDistance']

    def __init__(self):
        super(LegacyVehicleParams, self).__init__()
        g_currentVehicle.onChanged += self._update
        g_currentPreviewVehicle.onChanged += self._update
        
    def rebuildParams(self):
        normalizeValue = lambda v: (Decimal(str(round(v, 2))).normalize() + Decimal(0)).to_eng_string()
        getParam = lambda param: getParameters(self._getVehicle()).get(param, 'NF')
        paramsList = []

        for param in self.PARAMS:
            value = getParam(param)[0] if param == 'speedLimits' else getParam(param)
            if not self._getVehicle().hasTurrets:
                if param == 'turretArmor':
                    continue
                elif param == 'turretRotationSpeed':
                    param = 'gunRotationSpeed'
            if isinstance(value, list) or isinstance(value, tuple):
                separator = '-' if param in ('damage', 'piercingPower') else '/'
                value = separator.join(normalizeValue(v) for v in value)
            elif value == 'NF':
                pass
            else:
                value = normalizeValue(value)
            paramsList.append({'title': '#wek:vehicleParams/%s' % param, 'value': value})
        if self._isDAAPIInited():
            self.flashObject.as_update(paramsList)

    def _getVehicle(self):
        return g_currentPreviewVehicle.item if g_currentPreviewVehicle.isPresent() else g_currentVehicle.item

    def _update(self):
        self.rebuildParams()

    def _populate(self):
        super(LegacyVehicleParams, self)._populate()
        self._update()

    def _dispose(self):
        super(LegacyVehicleParams, self)._dispose()
        return