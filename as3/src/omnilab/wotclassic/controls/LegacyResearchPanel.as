package omnilab.wotclassic.controls
{
	import flash.events.MouseEvent;
	import net.wg.gui.components.controls.IconText;
	import net.wg.infrastructure.base.BaseDAAPIComponent;
	import net.wg.gui.components.controls.IconTextButton;
	import net.wg.data.constants.IconsTypes;
	
	public class LegacyResearchPanel extends BaseDAAPIComponent
	{
		public var researchBtn: IconTextButton;
		public var vehXP: IconText;
		
		public function LegacyResearchPanel() 
		{
			super();
		}
		
		public function as_setVehInfo(isElite: Boolean, vehExp: int): void {
			vehXP.text = App.utils.locale.integer(vehExp);
			vehXP.icon = isElite ? IconsTypes.ELITE_XP : IconsTypes.XP;
		}
	}
}