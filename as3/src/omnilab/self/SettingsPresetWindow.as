package omnilab.self
{
	import flash.text.TextField;
	import net.wg.gui.components.controls.ScrollingListEx;
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.gui.components.controls.SoundButtonEx;
	import flash.events.MouseEvent;
	
	public class SettingsPresetWindow extends AbstractWindowView 
	{
		
		public var createApplyBtn: SoundButtonEx;
		public var updateDeleteBtn: SoundButtonEx;
		public var showFolderBtn: SoundButtonEx;
		public var presetStatusTF: TextField;
		
		public var py_createApplyPreset: Function;
		public var py_updateDeletePreset: Function;
		public var py_showPresetFolder: Function;;
		
		public function SettingsPresetWindow() 
		{
			super();
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			window.title = "Пресет настроек";
			window.formBgPadding.bottom = 35;
		}
		
		override protected function configUI():void {
			super.configUI();
			createApplyBtn.addEventListener(MouseEvent.CLICK, this.onCreateApplyBtnClicked);
			updateDeleteBtn.addEventListener(MouseEvent.CLICK, this.onUpdateDeleteBtnClicked);
			showFolderBtn.addEventListener(MouseEvent.CLICK, this.onShowFolderBtnClicked);
		}
		
		public function as_setPresetStatus(status: String) {
			this.presetStatusTF.text = status;
		}
		
		public function as_updatePresetStatus(isPresetFound: Boolean, statusText: String) {
			this.presetStatusTF.text = statusText;
			if (isPresetFound) {
				this.createApplyBtn.label = "Применить";
				this.createApplyBtn.tooltip = "#settingsPresetWindow:createApplyBtn/apply/tooltip";
				this.updateDeleteBtn.label = "Удалить";
				this.updateDeleteBtn.tooltip = "#settingsPresetWindow:updateDeleteBtn/delete/tooltip";
			} else {
				this.createApplyBtn.label = "Cоздать";
				this.createApplyBtn.tooltip = "#settingsPresetWindow:createApplyBtn/create/tooltip";
				this.updateDeleteBtn.label = "Сканировать";
				this.updateDeleteBtn.tooltip = "#settingsPresetWindow:updateDeleteBtn/update/tooltip";
			}
		}
		
		public function onCreateApplyBtnClicked(param1: MouseEvent) {
			this.py_createApplyPreset();
		}
		
		public function onUpdateDeleteBtnClicked(param1: MouseEvent) {
			this.py_updateDeletePreset();
		}
		
		public function onShowFolderBtnClicked(param1: MouseEvent) {
			this.py_showPresetFolder();
		}
	}
}