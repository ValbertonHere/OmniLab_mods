package omnilab.outsource.popovers 
{
	import flash.display.*;
	import net.wg.infrastructure.base.SmartPopOverView;
	import net.wg.gui.components.popovers.PopOver;
	import net.wg.gui.components.popovers.PopOverConst;
	import net.wg.infrastructure.interfaces.IWrapper;
	
	public class OmniSessionStatsPopover extends SmartPopOverView 
	{
		public var bounds: Sprite;
		
		public function OmniSessionStatsPopover() 
		{
			super();
		}
		
		override protected function draw() : void
		{
			super.draw();
			PopOver(wrapper).titleTextField.text = "Сессионная статистика";
		}
		
		override protected function configUI() : void 
		{
			super.configUI();
		}
		
		override protected function initLayout() : void
		{
			popoverLayout.preferredLayout = PopOverConst.ARROW_BOTTOM;
			super.initLayout();
		}
	  
		override public function get width() : Number
		{
			return this.bounds.width;
		}
		  
		override public function get height() : Number
		{
			return this.bounds.height;
		}
      
		override public function set wrapper(param1:IWrapper) : void
		{
			super.wrapper = param1;
			PopOver(param1).isCloseBtnVisible = true;
		}
	}

}