from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_NOTE
from gui.Scaleform.daapi.view.lobby.vehicle_sell_dialog import VehicleSellDialog
from gui.shared.gui_items.processors import plugins

def VehicleSellDialog_as_visibleControlBlockS(self, value):
    base(self, not plugins.VehicleSellsLeftValidator(g_currentVehicle.item).validate().success)

VehicleSellDialog._VehicleSellDialog__useCtrlQuestion = False
base = VehicleSellDialog.as_visibleControlBlockS
VehicleSellDialog.as_visibleControlBlockS = VehicleSellDialog_as_visibleControlBlockS

LOG_NOTE("Valberton's quick vehicle sell tweak - init. Copyright (C) 2025 OmniLab R&D.")