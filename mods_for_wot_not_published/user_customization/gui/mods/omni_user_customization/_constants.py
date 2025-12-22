from items.customizations import PaintComponent, CamouflageComponent, DecalComponent, ProjectionDecalComponent, PersonalNumberComponent, SequenceComponent, AttachmentComponent, InsigniaComponent

OUC_CACHE_DUMMY = {'attachments': [], 
              'camouflages': [], 
              'decals': [], 
              'insignias': [],
              'modifications': [],
              'paints': [],
              'personal_numbers': [],
              'projection_decals': [],
              'styles': {'2d': {}, '3d': {}}}
GAME_CACHE_DUMMY = {'styles': {'2d': {}, '3d': {}}}
CLIENT_FORBIDDEN_STYLES = [31268, # Lebwa Team 2025
                    31272, # Yusha Team 2025
                    31276, # Near_You Team 2025
                    31280, # Jove Team 2025
                    31288, # Jove Team 2025 (sale)
                    31289, # Near_You Team 2025 (sale)
                    31290, # Lebwa Team 2025 (sale)
                    31291, # Yusha Team 2025 (sale)
                    31332, # Honeybadger (KV-2)
                    31378, # 2D Rattenkonig for Ratte (removed in 1.39)
                    31457, # BloggerNY Style
                    31480, # BloggerNY Style (sale)
                    613, # 2D Ignis Purgatio for Bat-Chat 25t
                    614, # 2D Nemesis for E100
                    615, # 3D The Reaper's scythe for 430U (No models)
                    616, # 2D Zhubolom for STB-1
                    647, # 2D No-name style for Strv S1
                    653] # 2D No-name style for T54E2
NOTIFICATION_HEADER = '#userCustomization:notification/header'
TEMPLATE_FOLDER = 'valberton/user_customization/template/'
TEMPLATE_FILES = ['camouflages/template.dds', # Оно никогда не поменяется, поэтому тупо хардкод.
                  'decals/template_emblem.dds',
                  'decals/template_inscription.dds',
                  'xml/template_camouflages.xml',
                  'xml/template_decals.xml',
                  'xml/template_styles.xml']
CUSTOMIZATION_STRINGS2CLASSES = {'attachments': AttachmentComponent,
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
SERVER_FORBIDDEN_STYLES = VALSPACE_FILESERVER + '/mods_stuff/user_customization/FORBIDDEN_STYLES'
API_URL = 'https://uc-api.valspace.ru'
API_SINGLE_USER_URL = API_URL + '/api/v1/settings?%s'
API_MULTIPLE_USER_URL = API_URL + '/api/v1/settings/user-vehicles'