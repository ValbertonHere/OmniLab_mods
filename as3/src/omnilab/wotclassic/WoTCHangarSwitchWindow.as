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
	
	public class WoTCHangarSwitchWindow extends AbstractWindowView
	{
		public var hanPreview: Image;
		
		public var okButt: SoundButtonEx;
		public var cancelButt: SoundButtonEx;
		
		public var standartCategoryText: TextField;
		public var premSenseCategoryText: TextField;
		public var specialCategoryText: TextField;
		
		public var StandardHanButtBar: RadioButtonBar;
		public var SpecialHanButtBar: RadioButtonBar;
		public var PremSenseHanButtBar: RadioButtonBar;
		
		public var PremiumSensetiveCheck: CheckBox;
		
		public var saveHangarChoice: Function;
		
		public var hanButtonBars: Array = new Array();
		public var hanCategories: Array = new Array();
		
		private var _selectedHangar: String = "";
		
		public function WoTCHangarSwitchWindow()
		{
			super();
		}
		
		override protected function configUI():void {
			super.configUI();
			
			hanButtonBars.push(this.StandardHanButtBar)
			hanButtonBars.push(this.SpecialHanButtBar)
			
			hanCategories.push(this.standartCategoryText)
			hanCategories.push(this.specialCategoryText)
			
			var standartHanData: Array = new Array();
			var specialHanData: Array = new Array();
			var premSenseHanData: Array = new Array();
			
			standartHanData.push({"label": "#wek_hangarSwitcher:hangar/title", "linkage": "hangar"});
			standartHanData.push({"label": "#wek_hangarSwitcher:hangar_premium/title", "linkage": "hangar_premium"});
			standartHanData.push({"label": "#wek_hangarSwitcher:hangar_v2/title", "linkage": "hangar_v2"});
			standartHanData.push({"label": "#wek_hangarSwitcher:hangar_premium_v2/title", "linkage": "hangar_premium_v2"});
			
			// specialHanData.push({"label": "#wek_hangarSwitcher:23feb_2014_hangar/title", "linkage": "hangar_premium_23feb_v2"});
			specialHanData.push({"label": "#wek_hangarSwitcher:hangar_premium_igr/title", "linkage": "hangar_premium_igr"});
			
			premSenseHanData.push({"label": "#wek_hangarSwitcher:prem_sense_hangars_v1/title", "linkage": "ps_v1"});
			premSenseHanData.push({"label": "#wek_hangarSwitcher:prem_sense_hangars_v2/title", "linkage": "ps_v2"});
			
			StandardHanButtBar.dataProvider = new DataProvider(standartHanData);
			SpecialHanButtBar.dataProvider = new DataProvider(specialHanData);
			PremSenseHanButtBar.dataProvider = new DataProvider(premSenseHanData);
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			window.title = "#wek_hangarSwitcher:window/title"
			window.formBgPadding.bottom = 40
			window.formBgPadding.top = 34
			width = 325;
			height = 395;
			
			StandardHanButtBar.addEventListener(IndexEvent.INDEX_CHANGE, this.onStandardHanButtonClick);
			SpecialHanButtBar.addEventListener(IndexEvent.INDEX_CHANGE, this.onBirthdayHanButtonClick);
			PremSenseHanButtBar.addEventListener(IndexEvent.INDEX_CHANGE, this.onPremSenseHanButtonClick);
			PremiumSensetiveCheck.addEventListener(Event.SELECT, this.onCheckBoxClicked);
			okButt.addEventListener(ButtonEvent.CLICK, this.closeWithSave);
			cancelButt.addEventListener(ButtonEvent.CLICK, this.closeWithoutSave);
		}
		
		public function as_setPremSensetive(isEnabled: Boolean):void {
			this.PremiumSensetiveCheck.selected = isEnabled;
			this.onCheckBoxClicked(null);
		}
		
		private function onStandardHanButtonClick(param0: IndexEvent):void {
			SpecialHanButtBar.selectedIndex = -1
			PremSenseHanButtBar.selectedIndex = -1
			hanPreview.source = "../maps/icons/wotclassic/" + param0.target.selectedItem.linkage + "_preview.png";
			this._selectedHangar = param0.target.selectedItem.linkage
		}
		
		private function onBirthdayHanButtonClick(param0: IndexEvent):void {
			StandardHanButtBar.selectedIndex = -1
			PremSenseHanButtBar.selectedIndex = -1
			hanPreview.source = "../maps/icons/wotclassic/" + param0.target.selectedItem.linkage + "_preview.png";
			this._selectedHangar = param0.target.selectedItem.linkage
		}
		
		private function onPremSenseHanButtonClick(param0: IndexEvent):void {
			StandardHanButtBar.selectedIndex = -1
			SpecialHanButtBar.selectedIndex = -1
			hanPreview.source = "../maps/icons/wotclassic/" + param0.target.selectedItem.linkage + "_preview.png";
			this._selectedHangar = param0.target.selectedItem.linkage
		}
		
		private function onCheckBoxClicked(param0: Event):void {
			this._selectedHangar = null;
			for each (var hanButtonBar in hanButtonBars) {
				hanButtonBar.selectedIndex = -1;
				hanButtonBar.enabled = !this.PremiumSensetiveCheck.selected;
			}
			
			if (!this.PremiumSensetiveCheck.selected) {
				PremSenseHanButtBar.selectedIndex = -1;
			}
			
			PremSenseHanButtBar.enabled = this.PremiumSensetiveCheck.selected;
			
			this.standartCategoryText.alpha = this.PremiumSensetiveCheck.selected ? 0.5 : 1.0
			this.specialCategoryText.alpha = this.PremiumSensetiveCheck.selected ? 0.5 : 1.0
			this.premSenseCategoryText.alpha = !this.PremiumSensetiveCheck.selected ? 0.5 : 1.0
			
		}
		
		private function closeWithoutSave(param0: ButtonEvent):void {
			onWindowCloseS();
		}
		
		private function closeWithSave(param0: ButtonEvent):void {
			if (this._selectedHangar) {
				this.saveHangarChoice(this._selectedHangar, this.PremiumSensetiveCheck.selected);
			}
			onWindowCloseS();
		}
	}
}