package omnilab.wotclassic.legacyAmmoPanel.data
{
	import net.wg.gui.lobby.modulesPanel.data.DeviceVO;
	
	public class LegacyOptDeviceVO extends DeviceVO
	{
       
      
		public var removable:Boolean = false;
		public var desc:String = "";
		public var notAffectedTTCTooltip:String = "";
		public var notAffectedTTC:Boolean = false;
		public var spec: String = "";
		public var isTrophyOrModern: Boolean = false;
		public var isAvailable: Boolean = false;
		public var destroyButtonLabel: String = "";
		public var isUpgradable: Boolean = false;
      
		public function LegacyOptDeviceVO(param1:Object) {
			super(param1);
		}
	}
}
