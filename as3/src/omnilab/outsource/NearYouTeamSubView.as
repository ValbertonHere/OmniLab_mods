package omnilab.outsource 
{
	import flash.display.*;
	import flash.events.MouseEvent;
	import flash.events.Event;
	import flash.text.TextField;
	
	import net.wg.gui.interfaces.ISoundButtonEx;
	import net.wg.infrastructure.base.AbstractView;
	
	public class NearYouTeamSubView extends AbstractView 
	{
		public var closeBtn: ISoundButtonEx;
		public var NYT_Logo: Sprite;
		public var right_back: Sprite;
		public var left_back: Sprite;
		public var text: Sprite;
		
		public var onViewClose: Function;
		
		public function NearYouTeamSubView() 
		{
			super();
		}
		
		public function appResized(e: Event): void {
			var app_width: Number = Number(App.appWidth)
			var app_height: Number = Number(App.appHeight)
			
			updateStage(app_width, app_height)
		}
			
		private function onCloseClick(param1: MouseEvent): void {
			this.onViewClose();
		}
		
		override public function updateStage(param1:Number, param2:Number) : void {
			this.closeBtn.x = param1 - 118;
			this.right_back.height = this.left_back.height = param2 - 90;
			this.right_back.x = param1 - 810;
			this.NYT_Logo.x = param1/2 - 91;
			this.text.x = param1/2 - 330;
			this.text.y = param2 - 220;
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			this.addEventListener(MouseEvent.CLICK, onViewClose);
			App.stage.addEventListener(Event.RESIZE, this.appResized);
			
			this.NYT_Logo.mouseEnabled = this.right_back.mouseEnabled = this.left_back.mouseEnabled = this.text.mouseEnabled = false;
			this.appResized(null);
		}
		
		override protected function onDispose():void {
			super.onDispose();
			this.removeEventListener(MouseEvent.CLICK, onViewClose);
			App.stage.removeEventListener(Event.RESIZE, this.appResized);
		}
	}
}