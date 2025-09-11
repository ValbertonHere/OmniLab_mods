package omnilab.self
{
	import flash.text.TextField;
	import flash.events.MouseEvent;

	import scaleform.clik.data.DataProvider;
	import scaleform.clik.events.IndexEvent;

	import net.wg.infrastructure.base.AbstractWindowView;

	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.gui.components.controls.TextInput;
	import net.wg.gui.lobby.settings.components.RadioButtonBar;

	
	
	public class SettingsPresetWindow extends AbstractWindowView 
	{
		public var createApplyBtn: SoundButtonEx;
		public var updateDeleteBtn: SoundButtonEx;
		public var showFolderBtn: SoundButtonEx;
		public var applyPresetNameBtn: SoundButtonEx;

		public var presetStatusTF: TextField;
		public var selectPresetDD: RadioButtonBar;
		public var selectedPresetNameTI: TextInput;
		
		public var py_createApplyPreset: Function;
		public var py_updateDeletePreset: Function;
		public var py_showPresetFolder: Function;
		public var py_applyPresetName: Function;
		public var py_selectPreset: Function;
		public var py_getPresets: Function;
		public var py_getSelectedPreset: Function;
		
		public function SettingsPresetWindow() 
		{
			super();
		}
		
		override protected function onPopulate(): void {
			super.onPopulate();
			window.title = "Пресет настроек";
			window.formBgPadding.bottom = 35;
		}
		
		override protected function configUI(): void {
			super.configUI();
			this.createApplyBtn.addEventListener(MouseEvent.CLICK, this.onCreateApplyBtnClicked);
			this.updateDeleteBtn.addEventListener(MouseEvent.CLICK, this.onUpdateDeleteBtnClicked)
			this.showFolderBtn.addEventListener(MouseEvent.CLICK, this.onShowFolderBtnClicked);
			this.applyPresetNameBtn.addEventListener(MouseEvent.CLICK, this.onApplyPresetNameBtnClicked);
			this.selectPresetDD.addEventListener(IndexEvent.INDEX_CHANGE, this.onPresetSelected);

			this._updatePresetDD();
		}
		
		public function as_setPresetStatus(status: String): void {
			this.presetStatusTF.text = status;
		}
		
		public function as_updatePresetStatus(isPresetFound: Boolean, statusText: String): void {
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

		public function as_setNameInputEnabled(isPresetFound: Boolean, canPresetBeRenamed: Boolean): void {
			this.applyPresetNameBtn.enabled = isPresetFound && canPresetBeRenamed;
			this.selectedPresetNameTI.enabled = canPresetBeRenamed;
			this.selectedPresetNameTI.text = canPresetBeRenamed ? "" : "Устаревший формат пресета.";
		}
		
		private function onCreateApplyBtnClicked(param1: MouseEvent): void {
			this.py_createApplyPreset(this.selectedPresetNameTI.text);
			this._updatePresetDD();
		}
		
		private function onUpdateDeleteBtnClicked(param1: MouseEvent): void {
			this.py_updateDeletePreset();
			this._updatePresetDD();
		}
		
		private function onShowFolderBtnClicked(param1: MouseEvent): void {
			this.py_showPresetFolder();
			this._updatePresetDD();
		}
		
		private function onApplyPresetNameBtnClicked(param1: MouseEvent): void {
			this.py_applyPresetName(this.selectedPresetNameTI.text)
			this._updatePresetDD();
		}

		private function onPresetSelected(param1: IndexEvent): void {
			this.py_selectPreset(this.selectPresetDD.selectedIndex);
		}

		private function _updatePresetDD(): void {
			this.selectPresetDD.dataProvider = new DataProvider(this.py_getPresets());
			this.selectPresetDD.selectedIndex = this.py_getSelectedPreset();
		}
	}
}