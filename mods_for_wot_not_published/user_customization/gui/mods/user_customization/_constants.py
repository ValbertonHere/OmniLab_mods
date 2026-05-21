import BigWorld, os
from external_strings_utils import unicode_from_utf8
from items.customizations import PaintComponent, CamouflageComponent, DecalComponent, ProjectionDecalComponent, PersonalNumberComponent, SequenceComponent, AttachmentComponent, InsigniaComponent
from gui.shared.gui_items import GUI_ITEM_TYPE

SUCCESS_STATUSES = [200, 201, 304]
USER_CUSTOMIZATION_CACHE = os.path.normpath(os.path.join(os.path.dirname(unicode_from_utf8(BigWorld.getPreferencesFilePath())[1]), 'mods', 'valberton', 'user_customization'))
FORBIDDEN_CONTENT_FILE = USER_CUSTOMIZATION_CACHE + '/FORBIDDEN_CONTENT'
USER_START_UNIQUE_ID = 55000
UC_CACHE_DUMMY = {'attachments': {}, 
              'camouflages': {}, 
              'decals': {}, 
              'insignias': {},
              'modifications': {},
              'paints': {},
              'personal_numbers': {},
              'projection_decals': {},
              'styles': {'2d': {}, '3d': {}}}
GAME_CACHE_DUMMY = {'styles': {'2d': {}, '3d': {}}}
ITEMS_CACHE_UPDATE_POOL = GUI_ITEM_TYPE.CUSTOMIZATIONS + (GUI_ITEM_TYPE.CUSTOMIZATION, )
CLIENT_FORBIDDEN_CONTENT = {'styles': [31268, # Lebwa Team 2025
                                        31272, # Yusha Team 2025
                                        31276, # Near_You Team 2025
                                        31280, # Jove Team 2025
                                        31288, # Jove Team 2025 (распродажа)
                                        31289, # Near_You Team 2025 (распродажа)
                                        31290, # Lebwa Team 2025 (распродажа)
                                        31291, # Yusha Team 2025 (распродажа)
                                        31332, # Медоед (КВ-2)
                                        31378, # 2D "Раттенкёниг" для Ратте (удалён в 1.39)
                                        31457, # Блогерский
                                        31480, # Блогерский (распродажа)
                                        613, # 2D "Ignis Purgatio" для Bat-Chat 25t
                                        614, # 2D "Немезис" для E100
                                        615, # 3D "Коса жнеца" для 430U (No models)
                                        616, # 2D "Жуболом" для STB-1
                                        647, # 2D стиль без названия для Strv S1
                                        653], # 2D стиль без названия для T54E2
                            'numbers': ('1488', '01488', '14880')}
NOTIFICATION_HEADER = {'header': '#userCustomization:notification/header'}
DEV_NOTIFICATION_HEADER = {'header': '#userCustomization:notification/dev_header'}
TEMPLATE_FOLDER = 'valberton/user_customization/template/'
TEMPLATE_FILES = ['camouflages/template.dds', # Оно никогда не поменяется, поэтому тупо хардкод.
                  'decals/template_emblem.dds',
                  'decals/template_inscription.dds',
                  'styles/template.png',
                  'json/template.json']
OUTFIT_COMPONENT_NAME_TO_OBJECT = {'attachments': AttachmentComponent,
                                 'camouflages': CamouflageComponent,
                                 'decals': DecalComponent,
                                 'insignias': InsigniaComponent,
                                 'paints': PaintComponent,
                                 'personal_numbers': PersonalNumberComponent,
                                 'projection_decals': ProjectionDecalComponent,
                                 'sequences': SequenceComponent}
CONFIG_FOLDER = './mods/configs/valberton'
CONFIG_FILE = CONFIG_FOLDER + '/userCustomization.json'
DEV_MODE_FILE = CONFIG_FOLDER + '/.dev_mode'
VALSPACE_FILESERVER = 'https://files.valspace.ru'
SERVER_FORBIDDEN_CONTENT_GIT = 'https://raw.githubusercontent.com/ValbertonHere/user-customization-bugtracker/refs/heads/main/FORBIDDEN_CONTENT.json'
SERVER_FORBIDDEN_CONTENT_VALSPACE = VALSPACE_FILESERVER + '/mods_stuff/user_customization/FORBIDDEN_CONTENT.json'
API_URL = 'https://uc-api.valspace.ru'
API_SINGLE_USER_URL = API_URL + '/api/v1/settings?%s'
API_MULTIPLE_USER_URL = API_URL + '/api/v1/settings/user-vehicles'