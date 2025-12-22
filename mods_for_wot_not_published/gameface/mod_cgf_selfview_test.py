
import logging
from frameworks.wulf import ViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from frameworks.wulf import ViewSettings, ViewFlags
from openwg_gameface import ModDynAccessor
from skeletons.gui.impl import IGuiLoader
from helpers import dependency
from gui.impl.pub.dialog_window import DialogFlags

VAL_TEST_VIEW = 'VAL_TEST'

logger = logging.getLogger(__name__)

def get_parent_window():
    ui_loader = dependency.instance(IGuiLoader)
    if ui_loader and ui_loader.windowsManager:
        return ui_loader.windowsManager.getMainWindow()
    return None

class SelfViewModel(ViewModel):
  
    def __init__(self, properties=0, commands=0):
        super(SelfViewModel, self).__init__(properties=properties, commands=commands)
    
    def _initialize(self):
        super(SelfViewModel, self)._initialize()


class SelfView(ViewImpl):

    viewLayoutID = ModDynAccessor(VAL_TEST_VIEW)
    
    def __init__(self, layoutID=None):
        settings = ViewSettings(SelfView.viewLayoutID(), flags=ViewFlags.VIEW, model=SelfViewModel())
        super(SelfView, self).__init__(settings)
        
    @property
    def viewModel(self):
        return super(SelfView, self).getViewModel()

class SelfWindow(WindowImpl):

    def __init__(self):
        super(SelfWindow, self).__init__(wndFlags=DialogFlags.WINDOW, content=SelfView(), parent=get_parent_window())