import Settings
from gui.game_loading.view.splash_screen import SplashScreen

class WoTCSplashScreen(SplashScreen):

    def _allVideosComplete(self):
        self.as_fadeOutS(0.1)

    def _getVideoVolume(self):
        ds = self._userPrefs[Settings.KEY_SOUND_PREFERENCES]
        if not ds:
            return 0.75
        return ds.readFloat('masterVolume', 0.75)

def createSplashScreen(pref):
    pref.writeString('introVideoVersion', '0')
    return WoTCSplashScreen(pref)