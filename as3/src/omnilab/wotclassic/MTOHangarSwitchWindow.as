package omnilab.wotclassic 
{	
	import flash.text.TextField;
	import flash.events.Event;
	import net.wg.gui.components.controls.Image;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.gui.lobby.settings.components.RadioButtonBar;
	import net.wg.infrastructure.base.AbstractWindowView;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.events.IndexEvent;
	import net.wg.gui.components.controls.CheckBox;
	
	public class MTOHangarSwitchWindow extends AbstractWindowView
	{
		public var hanPreview: Image;
		
		public var okButt: SoundButtonEx;
		public var cancelButt: SoundButtonEx;
		
		public var standartCategoryText: TextField;
		public var premSenseCategoryText: TextField;
		public var specialCategoryText: TextField;
		
		public var standardHanButtBar: RadioButtonBar;
		public var premSenseHanButtBar: RadioButtonBar;
		public var specialHanButtBar: RadioButtonBar;
		
		public var premiumSensetiveCheck: CheckBox;
		
		public var saveHangarChoice: Function;
		
		public var hanButtonBars: Array = new Array();
		
		private var _selectedHangar: String = "";
		private var _hasEventCategory: Boolean;
		
		public function MTOHangarSwitchWindow()
		{
			super();
		}
		
		override protected function configUI():void {
			super.configUI();

			hanButtonBars.push(this.standardHanButtBar);
			

			var standartHanData: Array = new Array();
			var specialHanData: Array = new Array();
			var premSenseHanData: Array = new Array();
			
			standartHanData.push({"label": "#wek_hangarSwitcher:hangar/title", "linkage": "hangar"});
			standartHanData.push({"label": "#wek_hangarSwitcher:hangar_premium/title", "linkage": "hangar_premium"});
			standartHanData.push({"label": "#wek_hangarSwitcher:hangar_v2/title", "linkage": "hangar_v2"});
			standartHanData.push({"label": "#wek_hangarSwitcher:hangar_premium_v2/title", "linkage": "hangar_premium_v2"});
			
			// specialHanData.push({"label": "#wek_hangarSwitcher:23feb_2014_hangar/title", "linkage": "hangar_premium_23feb_v2"});
			// specialHanData.push({"label": "#wek_hangarSwitcher:hangar_premium_igr/title", "linkage": "hangar_premium_igr"});
			// specialHanData.push({"label": "#wek_hangarSwitcher:hangar_premium_9may/title", "linkage": "hangar_premium_9may"});
			
			premSenseHanData.push({"label": "#wek_hangarSwitcher:prem_sense_hangars_v1/title", "linkage": "ps_v1"});
			premSenseHanData.push({"label": "#wek_hangarSwitcher:prem_sense_hangars_v2/title", "linkage": "ps_v2"});
			
			standardHanButtBar.dataProvider = new DataProvider(standartHanData);
			premSenseHanButtBar.dataProvider = new DataProvider(premSenseHanData);

			if (this._hasEventCategory) {
				hanButtonBars.push(this.specialHanButtBar);
				specialHanButtBar.dataProvider = new DataProvider(specialHanData);
			}
		}
		
		override protected function onPopulate():void {
			super.onPopulate();

			this._hasEventCategory = this.specialCategoryText != null || this.specialHanButtBar != null;

			window.title = "#wek_hangarSwitcher:window/title";
			window.formBgPadding.bottom = 40;
			window.formBgPadding.top = 34;
			width = 325;
			height = this._hasEventCategory ? 395 : 348;
			
			standardHanButtBar.addEventListener(IndexEvent.INDEX_CHANGE, this.onStandardHanButtonClick);
			premSenseHanButtBar.addEventListener(IndexEvent.INDEX_CHANGE, this.onPremSenseHanButtonClick);

			if (this._hasEventCategory) {
				specialHanButtBar.addEventListener(IndexEvent.INDEX_CHANGE, this.onSpecialHanButtonClick);
			}

			premiumSensetiveCheck.addEventListener(Event.SELECT, this.onCheckBoxClicked);
			okButt.addEventListener(ButtonEvent.CLICK, this.closeWithSave);
			cancelButt.addEventListener(ButtonEvent.CLICK, this.closeWithoutSave);
		}
		
		public function as_setPremSensetive(isEnabled: Boolean):void {
			this.premiumSensetiveCheck.selected = isEnabled;
			this.onCheckBoxClicked(null);
		}

		private function _changeSelect(hangarName: String): void {
			hanPreview.source = "../maps/icons/wotclassic/" + hangarName + "_preview.png";
			this._selectedHangar = hangarName
		}
		
		private function onStandardHanButtonClick(param0: IndexEvent):void {
			if (this._hasEventCategory) {
				specialHanButtBar.selectedIndex = -1
			}
			premSenseHanButtBar.selectedIndex = -1
			this._changeSelect(param0.target.selectedItem.linkage);
		}
		
		private function onSpecialHanButtonClick(param0: IndexEvent):void {
			standardHanButtBar.selectedIndex = -1
			premSenseHanButtBar.selectedIndex = -1
			this._changeSelect(param0.target.selectedItem.linkage);
		}
		
		private function onPremSenseHanButtonClick(param0: IndexEvent):void {
			standardHanButtBar.selectedIndex = -1
			if (this._hasEventCategory) {
				specialHanButtBar.selectedIndex = -1
			}
			this._changeSelect(param0.target.selectedItem.linkage);
		}
		
		private function onCheckBoxClicked(param0: Event):void {
			this._selectedHangar = null;
			for each (var hanButtonBar in hanButtonBars) {
				hanButtonBar.selectedIndex = -1;
				hanButtonBar.enabled = !this.premiumSensetiveCheck.selected;
			}
			
			if (!this.premiumSensetiveCheck.selected) {
				premSenseHanButtBar.selectedIndex = -1;
			}
			
			premSenseHanButtBar.enabled = this.premiumSensetiveCheck.selected;
			
			this.standartCategoryText.alpha = this.premiumSensetiveCheck.selected ? 0.5 : 1.0
			this.premSenseCategoryText.alpha = !this.premiumSensetiveCheck.selected ? 0.5 : 1.0
			if (this._hasEventCategory) {
				this.specialCategoryText.alpha = this.premiumSensetiveCheck.selected ? 0.5 : 1.0
			}
		}
		
		private function closeWithoutSave(param0: ButtonEvent):void {
			onWindowCloseS();
		}
		
		private function closeWithSave(param0: ButtonEvent):void {
			if (this._selectedHangar) {
				this.saveHangarChoice(this._selectedHangar, this.premiumSensetiveCheck.selected);
			}
			onWindowCloseS();
		}
	}
}