package omnilab.wotclassic.controls
{
	import flash.display.MovieClip;
	import flash.events.MouseEvent;
	import flash.text.TextField;
	import omnilab.wotclassic.data.PersonalReservesVO;
	import net.wg.data.constants.generated.TOOLTIPS_CONSTANTS;
	import net.wg.infrastructure.base.BaseDAAPIComponent;
	import net.wg.gui.interfaces.ISoundButtonEx;
	import scaleform.clik.core.UIComponent;
	
	public class PersonalReservesComponent extends BaseDAAPIComponent
	{
		public var personalReserves: MovieClip;
		public var clanReserves: MovieClip;
		public var reservesTF: TextField;
		
		public var showReservesWindow: Function;
		
		public function PersonalReservesComponent() 
		{
			super();
		}
		
		override protected function configUI():void {
			super.configUI();
			
			this.addEventListener(MouseEvent.ROLL_OVER, this.onRollOver);
			this.addEventListener(MouseEvent.ROLL_OUT, this.onRollOut);
			this.addEventListener(MouseEvent.CLICK, this.onClick);
		}
		
		override protected function onDispose():void {
			this.removeEventListener(MouseEvent.ROLL_OVER, this.onRollOver);
			this.removeEventListener(MouseEvent.ROLL_OUT, this.onRollOut);
			this.removeEventListener(MouseEvent.CLICK, this.onClick);
			
			super.onDispose();
		}
		
		public function as_setData(data: Object): void {
			var resData: PersonalReservesVO = new PersonalReservesVO(data);
			var personalFrameLabel: String = resData.personalCount == 0 ? "not_activated" : "active" + resData.personalCount;
			if (!resData.hasActiveReserves) {
				this.personalReserves.gotoAndStop("not_activated");
				this.clanReserves.visible = false;
				this.reservesTF.text = App.utils.locale.integer(resData.personalStorageCount);
				this.reservesTF.x = 36;
				return
			}
			
			this.personalReserves.gotoAndStop(personalFrameLabel);
			this.clanReserves.visible = resData.clanCount != 0;
			
			if (this.clanReserves.visible) {
				this.clanReserves.gotoAndStop("active" + resData.clanCount);
			}
			
			this.reservesTF.text = String(Math.floor(resData.usageTime / 60)) + " мин.";
			this.reservesTF.x = this.clanReserves.visible ? 57 : 36;
		}
		
		private function onRollOver(e: MouseEvent): void {
			App.toolTipMgr.showWulfTooltip(TOOLTIPS_CONSTANTS.PERSONAL_RESERVES_WIDGET, null);
		}
		
		private function onRollOut(e: MouseEvent): void {
			App.toolTipMgr.hide();
		}
		
		private function onClick(e: MouseEvent): void {
			App.toolTipMgr.hide();
			this.showReservesWindow();
		}
	}
}