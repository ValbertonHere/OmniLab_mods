package omnilab.wotclassic.test 
{
	import flash.display.MovieClip;
	import flash.utils.Dictionary;
	import net.wg.gui.components.controls.SoundListItemRenderer;
	import flash.events.MouseEvent;
	import flash.text.TextField;
	import net.wg.data.constants.SoundTypes;
	import net.wg.data.constants.InvalidationType;
	import net.wg.gui.components.controls.Image;
	import omnilab.mtclassic_test.hangar.legacyAmmoPanel.data.LegacyListItemVO;
	
	public class ModuleListItemRenderer extends SoundListItemRenderer 
	{
        public var icon: MovieClip;
        public var targetMC: MovieClip;
        public var descField: TextField;
        public var errorField: TextField;
		
		private var _itemData: LegacyListItemVO = null;
		
		public function ModuleListItemRenderer() 
		{
			super();
			preventAutosizing = true;
		}
        
        private function setTruncatedHtmlText(param1:TextField, param2:String, param3:uint) : void
        {
            var _loc4_:String = param2;
            this.descField.htmlText = _loc4_;
            while(param1.numLines > param3)
            {
                _loc4_ = _loc4_.substr(0,_loc4_.length - 1);
                this.descField.htmlText = _loc4_ + "...";
            }
        }
        
		private function get getButtonAnimGroup(): String 
		{
			var animGroup: String = this._itemData.isSelected ? "selected_" : "";
            return animGroup
		}

        private function onClickHandler(param1:MouseEvent) : void
        {
			DebugUtils.LOG_ERROR("Clicked");
        }
        
        override public function setData(param1: Object) : void
        {
            super.setData(param1);
			this._itemData = new LegacyListItemVO(param1);
			if (this._itemData != null) {
				this.gotoAndPlay(this.getButtonAnimGroup + "over");
			}
			invalidateData();
        }
	  
		override protected function handleMouseRollOver(param0:MouseEvent): void
		{
			super.handleMouseRollOver(param0);
			this.gotoAndPlay(this.getButtonAnimGroup + "over");
		}
	  
		override protected function handleMouseRollOut(param0:MouseEvent): void
		{
			super.handleMouseRollOut(param0);
			this.gotoAndPlay(this.getButtonAnimGroup + "up");
		}
		
        override protected function draw() : void
		{
			super.draw();
			if (this._itemData != null)
			{
				this.textField.text = this._itemData.title;
				this.setTruncatedHtmlText(this.descField, this._itemData.descr, 2);
				App.utils.commons.updateTextFieldSize(this.descField, false, true);
                this.errorField.visible = false;
				this.icon.gotoAndStop(this._itemData.level);
                this.targetMC.visible = this._itemData.targetVisible;
                this.targetMC.gotoAndPlay(this._itemData.target);
                this.enabled = !this._itemData.disabled;
			}
		}
		
        override protected function configUI() : void
        {
            super.configUI();
            addEventListener(MouseEvent.CLICK, this.onClickHandler);
            soundType = SoundTypes.NORMAL_BTN;
        }
	}
}