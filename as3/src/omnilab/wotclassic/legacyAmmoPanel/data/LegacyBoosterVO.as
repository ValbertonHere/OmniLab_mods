package omnilab.wotclassic.legacyAmmoPanel.data
{
	import net.wg.gui.lobby.modulesPanel.data.DeviceVO;
	
    public class LegacyBoosterVO extends DeviceVO
    {
         
        
        public var desc:String = "";
        
        public var notAffectedTTC:Boolean = false;
        
        public var count:int = -1;
        
        public var removable:Boolean = true;
        
        public var buyButtonLabel:String = "";
        
        public var buyButtonTooltip:String = "";
        
        public var buyButtonVisible:Boolean = false;
        
        public function LegacyBoosterVO(param1:Object)
        {
            super(param1);
        }
    }
}
