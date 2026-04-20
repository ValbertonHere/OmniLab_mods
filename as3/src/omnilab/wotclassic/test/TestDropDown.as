package omnilab.wotclassic.test 
{
	import net.wg.gui.components.controls.DropdownMenu;
	import flash.events.Event;
	import flash.geom.Point;
	import net.wg.gui.components.crosshairPanel.CrosshairSniper;
	
	public class TestDropDown extends DropdownMenu 
	{
		
		public function TestDropDown() 
		{
			super();
			
		}
        
        override protected function draw() : void
        {
            super.draw();
            if(Boolean(_dataProvider))
            {
                enabled = _dataProvider.length > 0;
            }
        }
        
        override protected function showDropdown() : void
        {
            super.showDropdown();
            if(_dropdownRef)
            {
                parent.parent.addChild(_dropdownRef);
                // _dropdownRef.addEventListener(OnEquipmentRendererOver.ON_EQUIPMENT_RENDERER_OVER,this.handleOnEquipmentRendererOver,false,0,true);
                this.updateDDPosition(null);
            }
        }
        
        override protected function updateDDPosition(param1:Event) : void
        {
            var _loc2_:Point = null;
            if(_dropdownRef)
            {
                super.updateDDPosition(param1);
                _dropdownRef.x *= App.appScale;
                _dropdownRef.y *= App.appScale;
                _loc2_ = parent.parent.parent.globalToLocal(new Point(_dropdownRef.x,_dropdownRef.y));
                _dropdownRef.x = _loc2_.x;
                _dropdownRef.y = _loc2_.y;
            }
        }
	}
}