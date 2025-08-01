import BigWorld
from Vehicle import Vehicle
from items.vehicles import g_list, g_cache
from items import vehicles
from constants import VEHICLE_MODE
import threading
import time
from gui.shared.utils.key_mapping import getBigworldNameFromKey
from gui import InputHandler
SDModList = [vehicles.VehicleDescr(typeName='france:F01_RenaultFT'),
 vehicles.VehicleDescr(typeName='france:F44_Somua_S35'),
 vehicles.VehicleDescr(typeName='france:F13_AMX38'),
 vehicles.VehicleDescr(typeName='france:F04_B1'),
 vehicles.VehicleDescr(typeName='france:F05_BDR_G1B'),
 vehicles.VehicleDescr(typeName='france:F06_ARL_44'),
 vehicles.VehicleDescr(typeName='france:F07_AMX_M4_1945'),
 vehicles.VehicleDescr(typeName='france:F08_AMX_50_100'),
 vehicles.VehicleDescr(typeName='france:F09_AMX_50_120'),
 vehicles.VehicleDescr(typeName='france:F10_AMX_50B'),
 vehicles.VehicleDescr(typeName='germany:G12_Ltraktor'),
 vehicles.VehicleDescr(typeName='germany:G06_PzII'),
 vehicles.VehicleDescr(typeName='germany:G83_Pz_IV_AusfA'),
 vehicles.VehicleDescr(typeName='germany:G10_PzIII_AusfJ'),
 vehicles.VehicleDescr(typeName='germany:G81_Pz_IV_AusfH'),
 vehicles.VehicleDescr(typeName='germany:G27_VK3001P'),
 vehicles.VehicleDescr(typeName='germany:G57_PzVI_Tiger_P'),
 vehicles.VehicleDescr(typeName='germany:G16_PzVIB_Tiger_II'),
 vehicles.VehicleDescr(typeName='germany:G58_VK4502P'),
 vehicles.VehicleDescr(typeName='germany:G42_Maus'),
 vehicles.VehicleDescr(typeName='ussr:R11_MS-1'),
 vehicles.VehicleDescr(typeName='ussr:R08_BT-2'),
 vehicles.VehicleDescr(typeName='ussr:R22_T-46'),
 vehicles.VehicleDescr(typeName='ussr:R06_T-28'),
 vehicles.VehicleDescr(typeName='ussr:R80_KV1'),
 vehicles.VehicleDescr(typeName='ussr:R106_KV85'),
 vehicles.VehicleDescr(typeName='ussr:R01_IS'),
 vehicles.VehicleDescr(typeName='ussr:R19_IS-3'),
 vehicles.VehicleDescr(typeName='ussr:R81_IS8'),
 vehicles.VehicleDescr(typeName='ussr:R45_IS-7')]
pos = None

def nig():
    global pos
    for idx, SDMod in enumerate(SDModList):
        pl = BigWorld.player()
        OFFLINE_BATTLE_ENTITY_STATES = {'publicInfo': dict(pl.vehicle.publicInfo),
         'health': SDMod.maxHealth,
         'isCrewActive': 1,
         'physicsMode': 0,
         'engineMode': (1, 0),
         'gunAnglesPacked': 32817,
         'botDisplayStatus': 1}
        OFFLINE_BATTLE_ENTITY_STATES['publicInfo']['compDescr'] = SDMod.makeCompactDescr()
        OFFLINE_BATTLE_ENTITY_STATES['publicInfo']['name'] = 'BattleUnit'
        OFFLINE_BATTLE_ENTITY_STATES['publicInfo']['team'] = 2
        Nig = BigWorld.createEntity('Vehicle', pl.spaceID, 0, pos, (pl.roll, pl.pitch, -pl.yaw), OFFLINE_BATTLE_ENTITY_STATES)
        pl.arena.vehicles[Nig] = {'wtr': 0,
         'isAlive': 1,
         'vehPostProgression': [],
         'isTeamKiller': 0,
         'personalMissionInfo': {},
         'personalMissionIDs': [],
         'fakeName': 'BattleUnit',
         'accountDBID': 0,
         'igrType': 0,
         'ranked': (0, 0),
         'customRoleSlotTypeId': 0,
         'outfitCD': '',
         'botDisplayStatus': 1,
         'badges': ([], []),
         'forbidInBattleInvitations': False,
         'vehicleType': SDMod,
         'name': 'BattleUnit',
         'isPrebattleCreator': False,
         'prebattleID': 0,
         'maxHealth': SDMod.maxHealth,
         'events': {},
         'clanAbbrev': '',
         'isAvatarReady': True,
         'team': 2,
         'clanDBID': 0,
         'overriddenBadge': 0,
         'avatarSessionID': '2130706436'}
        pos += (0.0, 0.0, -8.0)
        if idx in (9, 19, 29):
            pos += (-13.0, 0.0, 80.0)
        pl.arena.onVehicleAdded(Nig)
        time.sleep(0.5)


def onhandleKeyEvent(event):
    global pos
    key = getBigworldNameFromKey(event.key)
    if key == 'KEY_NUMPAD1':
        pos = BigWorld.player().position
        thread = threading.Thread(target=nig)
        thread.start()


InputHandler.g_instance.onKeyDown += onhandleKeyEvent