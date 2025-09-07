package omnilab.wotclassic.controls
{
	
	import flash.events.MouseEvent;
	import flash.text.TextField;
	import net.wg.gui.components.controls.SoundButtonEx;
	
	public class LegacyTasksButton extends SoundButtonEx
	{
		public var tasksLabel: TextField;
		
		public function LegacyTasksButton()
		{
			super();
			
			this.tasksLabel.htmlText = '<TEXTFORMAT INDENT="0" LEFTMARGIN="0" RIGHTMARGIN="0" LEADING="-3"><P ALIGN="LEFT"><FONT FACE="$TitleFont" SIZE="12" COLOR="#fffbce86" KERNING="0">#wek:lobbyHeader/tasks</FONT></P></TEXTFORMAT>';
			this.tooltip = "#wek:lobbyHeader/tasks/tooltip"
			this.addEventListener(MouseEvent.ROLL_OVER, this.onRollOver);
			this.addEventListener(MouseEvent.ROLL_OUT, this.onRollOut);
			this.addEventListener(MouseEvent.MOUSE_DOWN, this.onMouseDown);
			this.addEventListener(MouseEvent.MOUSE_UP, this.onMouseUp);
			this.gotoAndPlay("down");
			
		}
		
		internal function onRollOver(param1:MouseEvent):void {
			this.gotoAndPlay("over");
		}
		
		internal function onRollOut(param1:MouseEvent):void {
			this.gotoAndPlay("out");
		}
		
		internal function onMouseDown(param1:MouseEvent):void {
			this.gotoAndPlay("down");
		}
		
		internal function onMouseUp(param1:MouseEvent):void {
			this.gotoAndPlay("release");
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
			setState(stateStr);
		}
	}
}