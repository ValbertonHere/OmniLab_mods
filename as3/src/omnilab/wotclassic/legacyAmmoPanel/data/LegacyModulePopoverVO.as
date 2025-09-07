package omnilab.wotclassic.legacyAmmoPanel.data 
{
	import net.wg.gui.lobby.modulesPanel.data.FittingSelectPopoverVO;
	
	public class LegacyModulePopoverVO extends FittingSelectPopoverVO 
	{
		public var slotIndex: int = 0;
		public var slotType: String = "";
		
		public function LegacyModulePopoverVO(param0:Object) 
		{
			super(param0);
		}
		
		override protected function onDataWrite (param0:String, param1:Object) : Boolean{
			super.onDataWrite(param0, param1);
			return true;
		}
		
		override protected function onDispose () : void{
			super.onDispose();
		}
	}

}