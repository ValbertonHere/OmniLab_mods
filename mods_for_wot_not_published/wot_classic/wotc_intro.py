import BigWorld, Settings
from gui.game_loading.view.splash_screen import SplashScreen, DEFAULT_VIDEO_BUFFERING_TIME
from gui.Scaleform.genConsts.SPLASHSCREENCONSTANTS import SPLASHSCREENCONSTANTS
from gui.doc_loaders.GuiDirReader import GuiDirReader
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING

class WoTCSplashScreen(SplashScreen):

    def __init__(self, preferences):
        super(SplashScreen, self).__init__(ExternalFlashSettings('splashScreen', 'splashScreenApp.swf', 'root.main', SPLASHSCREENCONSTANTS.ON_SPLASH_SCREEN_LOADED_CALLBACK))
        self.createExternalComponent()
        self._userPrefs = preferences
        self._movieFiles = GuiDirReader.getAvailableIntroVideoFiles()
        self._isFirstRun = True
        try:
            with open('wotc_isFirstRun', 'r') as f2r:
                self._isFirstRun = bool(int(f2r.read()))
        except:
            LOG_WARNING('''
                        Please, learn how to install mods normally! Thank you!
                        File "wotc_isFirstRun" does not exist or contains an invalid value.
                        Not critical, but think about your life. Send to developers lines below.
                        ''')
            LOG_CURRENT_EXCEPTION()
        if self._isFirstRun:
            self._movieFiles.insert(0, 'videos/wot_classic/firstRun.usm')
        self._writeSetting = False
        self._bufferTime = self._userPrefs.readFloat(Settings.VIDEO_BUFFERING_TIME, DEFAULT_VIDEO_BUFFERING_TIME)
        self._soundValue = self._getVideoVolume() if BigWorld.isWindowVisible() else 0
        self._canSkip = True
        self._currentMovie = None
        self._width = 0
        self._height = 0
        return

    def _allVideosComplete(self):
        self._isFirstRun = False
        with open('wotc_isFirstRun', 'w') as f2w:
            f2w.write(int(self._isFirstRun))

        self.as_fadeOutS(0.1)

    def _getVideoVolume(self):
        ds = self._userPrefs[Settings.KEY_SOUND_PREFERENCES]
        if not ds:
            return 0.75
        return ds.readFloat('masterVolume', 0.75)

def createSplashScreen(pref):
    pref.writeString('introVideoVersion', '0')
    return WoTCSplashScreen(pref)