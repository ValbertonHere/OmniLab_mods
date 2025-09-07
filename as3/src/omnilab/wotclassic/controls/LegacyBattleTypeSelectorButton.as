package omnilab.wotclassic.controls
{
	
	import flash.text.*;
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import net.wg.gui.components.controls.IconText;
	import net.wg.data.constants.IconsTypes;
	import scaleform.clik.events.ButtonEvent;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.infrastructure.interfaces.IClosePopoverCallback;
	import net.wg.gui.lobby.header.vo.HBC_AccountDataVo;
	
	public class LegacyBattleTypeSelectorButton extends SoundButtonEx implements IClosePopoverCallback
	{
		public var battleType: IconText;
		
		public function LegacyBattleTypeSelectorButton()
		{
			super();
		}
		
		override protected function configUI():void {
			super.configUI();
			
			addEventListener(MouseEvent.ROLL_OVER, this.onRollOver);
			addEventListener(MouseEvent.ROLL_OUT, this.onRollOut);
		}
		
		internal function onRollOver(param1:MouseEvent):void {
			gotoAndPlay("over");
			this.width = 204;
		}
		
		internal function onRollOut(param1:MouseEvent):void {
			gotoAndPlay("out");
			this.width = 204;
		}
		
		public function onPopoverOpen(): void {
			selected = true;
			gotoAndPlay("selected_up");
		}
		
		public function onPopoverClose(): void {
			selected = false;
			gotoAndPlay("up");
		}
		
		public function as_disable(isDisabled: Boolean): void {
			this.enabled = !isDisabled;
		}
		
		override public function set enabled (param0:Boolean) : void {
			var stateStr: String = null;
			super.enabled = param0
			if (super.enabled) {
				stateStr = "up";
			} else {
				stateStr = "disabled";
			}
			gotoAndPlay(stateStr);
		}
	}
}