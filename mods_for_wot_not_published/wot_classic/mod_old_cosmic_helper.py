from cosmic_event.gui.impl.battle.cosmic_hud.announcements import AnnouncementGoal
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.cosmic_hud_view_model import AnnouncementTypeEnum
from SoundGroups import g_instance

def AnnouncementGoal_updateAnnouncement(self, transaction):
    base(self, transaction)
    if self._ended:
        return
    else:
        remTime = self.getRemainingTime()
        print remTime, self.type
        if remTime <= 3 and self.type in (AnnouncementTypeEnum.PICKUPS, AnnouncementTypeEnum.PREPARETOSCAN, AnnouncementTypeEnum.PREPARETOSCANFINAL):
            g_instance.playSound2D('ev_cosmic_old_timer')
        return


base = AnnouncementGoal.updateAnnouncement
AnnouncementGoal.updateAnnouncement = AnnouncementGoal_updateAnnouncement