package 
{
	import flash.text.*;
	import flash.display.*;
	import flash.events.MouseEvent;
	
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.data.managers.impl.ToolTipParams;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	
	import net.wg.data.constants.generated.TOOLTIPS_CONSTANTS;
	
	
	public class TestWindow extends AbstractWindowView implements IPopOverCaller
	{
		public var button: SoundButtonEx;
		public var onClicked: Function;
		
		public function TestWindow() 
		{
			super();
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			
			width = 921;
			height = 425;
			window.title = "Тестовое UwU"
		}
		
		override protected function configUI():void {
			super.configUI();
			this.button.addEventListener(MouseEvent.CLICK, this.onButtonClicked);
		}
		
		public function onButtonClicked(param1:MouseEvent):void {
			DebugUtils.LOG_WARNING("Clicked");
			this.onClicked();
			App.popoverMgr.show(this, "OmniSessionStatsPopoverUI");
		}
      
		public function getHitArea() : DisplayObject
		{
			return button;
		}
		  
		public function getTargetButton() : DisplayObject
		{
			return button;
		}
	}
}