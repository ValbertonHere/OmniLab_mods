package omnilab.wotclassic.controls.test 
{
	import net.wg.gui.components.controls.ScrollingListEx;
	import net.wg.infrastructure.base.AbstractView;
	import net.wg.data.ListDAAPIDataProvider;
	import omnilab.wotclassic.controls.test.data.LegacyVehParamVO;
	import flash.events.Event;
	import scaleform.clik.interfaces.IDataProvider;
	import net.wg.infrastructure.base.BaseDAAPIComponent;
	import scaleform.clik.data.DataProvider;
	
	public class LegacyVehicleParams extends BaseDAAPIComponent
	{
		public var paramsList: ScrollingListEx;
		
		protected var _dataProvider:IDataProvider = null;
		protected var _dataArray: Array = null;
		private var _forceInvalidateOnDataChange: Boolean = true;
		
		public function LegacyVehicleParams() 
		{
			super();
		}
      
		public function as_update(param1: Array): void
		{
			this._dataArray = param1;
			this._dataProvider = new DataProvider(this._dataArray);
			this.paramsList.dataProvider = this._dataProvider;
			this.paramsList.height = 28 * this._dataProvider.length;
			this.paramsList.rowHeight = 28;
			this.paramsList.validateNow();
		}
		
		override protected function configUI() : void {
			mouseEnabled = this.paramsList.mouseEnabled = false;
		}
	}
}