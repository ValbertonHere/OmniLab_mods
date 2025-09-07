from gui.game_loading.wotc_loading import gameLoading

def init():
    if gameLoading is not None:
        for i in gameLoading.getChildren():
            i.visible = False