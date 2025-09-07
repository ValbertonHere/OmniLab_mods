package omnilab.wotclassic.controls
{
	
	import flash.events.MouseEvent;
	import flash.text.TextField;
	import net.wg.gui.components.controls.SoundButtonEx;
	
	public class LegacyTutorialButton extends SoundButtonEx
	{
		public var tutorialLabel: TextField
		
		public function LegacyTutorialButton()
		{
			super();
			
			this.tutorialLabel.htmlText = '<TEXTFORMAT INDENT="0" LEFTMARGIN="0" RIGHTMARGIN="0" LEADING="-3"><P ALIGN="LEFT"><FONT FACE="$TitleFont" SIZE="12" COLOR="#ffd7d2c6" KERNING="0">#wek:lobbyHeader/tutorial</FONT></P></TEXTFORMAT>';
			this.addEventListener(MouseEvent.ROLL_OVER, this.onRollOver);
			this.addEventListener(MouseEvent.ROLL_OUT, this.onRollOut);
			this.addEventListener(MouseEvent.MOUSE_DOWN, this.onMouseDown);
			this.addEventListener(MouseEvent.MOUSE_UP, this.onMouseUp);
			this.gotoAndPlay("pause_normal_down");
		}
		
		internal function onRollOver(param1:MouseEvent):void {
			this.gotoAndPlay("pause_normal_release");
		}
		
		internal function onRollOut(param1:MouseEvent):void {
			this.gotoAndPlay("pause_normal_down");
		}
		
		internal function onMouseDown(param1:MouseEvent):void {
			this.gotoAndPlay("pause_normal_down");
		}
		
		internal function onMouseUp(param1:MouseEvent):void {
			this.gotoAndPlay("pause_normal_release");
		}
		
		public function as_disable(isDisabled: Boolean): void {
			if (isDisabled) {
				this.gotoAndPlay("normal_disabled");
				this.enabled = false;
				return;
			}
			this.gotoAndPlay("pause_normal_out");
			this.enabled = true;
		}
	}
}