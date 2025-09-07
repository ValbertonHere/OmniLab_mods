package omnilab.wotclassic.controls.test 
{
	import flash.text.StyleSheet;
	import flash.text.TextField;
	import scaleform.clik.controls.ListItemRenderer;
	import omnilab.wotclassic.controls.test.data.LegacyVehParamVO;
	import scaleform.clik.constants.InvalidationType;
	
	public class LegacyVehicleParamRenderer extends ListItemRenderer 
	{
		public var paramTitleTF: TextField;
		public var paramValueTF: TextField;
		
		private var _title: String = "";
		private var _value: String = "";
		
		public function LegacyVehicleParamRenderer() 
		{
			super();
			var paramStyle = new StyleSheet();      
			paramStyle.setStyle("h1",{color:"#B4A983"});
			paramStyle.setStyle("p", {color:"#9F9260"});
			this.paramTitleTF.styleSheet = paramStyle;
		}
		
		private function _update(): void {
			this.paramTitleTF.htmlText = this._title;
			this.paramValueTF.text = this._value;
		}
		
		override public function setData(param1:Object) : void {
			if(param1 == null)
			{
				return;
			}
			super.setData(param1);
			this._title = param1["title"];
		if (param1["value"].indexOf("/") >= 0 || param1["value"].indexOf("-") >= 0 || param1["value"] == "NF") {
				this._value = param1["value"];
			} else {
				this._value = App.utils.locale.integer(param1["value"]);
			}
			this._update();
		}
		
		override protected function configUI() : void {
			super.configUI();
			preventAutosizing = true;
		}
		
		override protected function draw() : void {
			super.draw();
			this._update();
		}
	}
}