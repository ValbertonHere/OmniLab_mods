# Не используется до лучших времён.

import logging
import threading
import urllib2
import ssl
import json
import BigWorld

from urllib import urlencode
from ._constants import API_URL, API_SINGLE_USER_URL, API_MULTIPLE_USER_URL
from .utils import getVehicleOutfitFromDict
from vehicle_systems.camouflages import _currentMapSeason
from vehicle_systems import camouflages

logger = logging.getLogger(__name__)

json_headers = {'Content-type': 'application/json',
                'Accept': 'application/json'}

class GetRequest(urllib2.Request):
    def get_method(self, *args, **kwargs):
        return 'GET'
    
class PutRequest(urllib2.Request):
    def get_method(self, *args, **kwargs):
        return 'PUT'
    
class PatchRequest(urllib2.Request):
    def get_method(self, *args, **kwargs):
        return 'PATCH'
    
class PostRequest(urllib2.Request):
    def get_method(self, *args, **kwargs):
        return 'POST'

class UserCustomizationNetworkAPI(object):
    def __init__(self):
        pass
        # self.api_available = self.__checkResponseCode('api_response', requests.get('https://valberton-style-storage.wotstat.info').status_code)
        
    def request_async(self, url, data, headers, method, callback, error_callback=None, ctx=None):
        event = threading.Event()
        runner = threading.Thread(target=self.run,
                                    args=(event, url, data, headers, method, callback, error_callback, ctx))
        runner.start()
        event.wait()

    def run(self, event, url, data, headers, method, callback, error_callback, ctx):
        event.set()
        try:
            result = method(url, data, headers)
            if callback:
                callback(result, ctx)
        except Exception, e:
            if error_callback:
                error_callback(e)
            else:
                raise e
    
    def __processUserVehicleOutfitResponse(self, data, ctx):
        userConfig = json.loads(urllib2.urlopen(data, context=ssl._create_unverified_context()).read())

        if not userConfig:
            logger.info('No userConfig found on server.')
            return None
        
        vehicleOutfit = userConfig.get(ctx['vehicleName'], None)
        if not vehicleOutfit:
            logger.info('No vehicleName found in userConfig on server.')
            return None
        
        vehicle = BigWorld.entity(ctx['vehicleID'])
        if vehicle:
            vehicle.appearance._CommonTankAppearance__outfit = getVehicleOutfitFromDict(vehicleOutfit, vehicle.typeDescriptor, _currentMapSeason())
            camouflages.updateFashions(vehicle.appearance)
        
        return
    
    def __processArenaVehiclesOutfit(self, data, _):
        logger.info(urllib2.urlopen(data, context=ssl._create_unverified_context()).read())
    
    def __processSaveConfigOnServer(self, data, _):
        # urllib2.urlopen(data, context=ssl._create_unverified_context()).read()
        logger.info(urllib2.urlopen(data, context=ssl._create_unverified_context()).read())

    def getUserVehicleOutfit(self, vehicleID):
        arena = BigWorld.player().arena
        if arena is None:
            return
        
        vehicleVO = arena.vehicles[vehicleID]
        dbID = vehicleVO['accountDBID']
        vehicleName = vehicleVO['vehicleType'].name
        self.request_async(API_SINGLE_USER_URL % urlencode({'id': dbID}), None, json_headers, GetRequest, self.__processUserVehicleOutfitResponse, ctx={'vehicleName': vehicleName, 'vehicleID': vehicleID})

    def getArenaVehiclesOutfits(self):
        arena = BigWorld.player().arena
        if arena is None:
            return
        
        self.request_async(API_MULTIPLE_USER_URL, json.dumps([{'id': vehicleVO['accountDBID'], 'vehicle': vehicleVO['vehicleType'].name} for vehicleVO in arena.vehicles.values()]), json_headers, PostRequest, self.__processArenaVehiclesOutfit)

    def putConfigToServer(self, dbID, config):
        self.request_async(API_SINGLE_USER_URL % urlencode({'id': dbID}), config, json_headers, PutRequest, self.__processSaveConfigOnServer)
    
    def patchConfigOnServer(self, dbID, data):
        self.request_async(API_SINGLE_USER_URL % urlencode({'id': dbID}), data, json_headers, PatchRequest, self.__processSaveConfigOnServer)

g_api = UserCustomizationNetworkAPI()