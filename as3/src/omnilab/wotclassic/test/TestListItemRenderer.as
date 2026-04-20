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
	import net.wg.gui.components.controls.ButtonIconNormal;
	import net.wg.gui.components.controls.IconTextButton;
	import scaleform.clik.utils.Constraints;
	
	public class TestListItemRenderer extends SoundListItemRenderer 
	{
        public var icon: Image;
        public var removeBtn: IconTextButton;
        public var targetMC: MovieClip;
        public var descField: TextField;
        public var errorField: TextField;
        public var hitMc: MovieClip;
		
		private var _itemData: LegacyListItemVO = null;
		
		public function TestListItemRenderer() 
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

        private function onClickHandler(param1:MouseEvent) : void
        {
			DebugUtils.LOG_ERROR("Clicked");
        }
        
        override public function setData(param1: Object) : void
        {
            super.setData(param1);
			this._itemData = new LegacyListItemVO(param1);
			if (this._itemData != null) {
                this.enabled = !this._itemData.disabled;
			}
			invalidateData();
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
				this.icon.source = "../maps/icons/moduleTypes/" + this._itemData.moduleIcon + ".png";
                this.targetMC.visible = this._itemData.targetVisible;
                this.targetMC.gotoAndPlay(this._itemData.target);
                this.removeBtn.visible = this._itemData.isSelected;
                this.descField.visible = !this._itemData.isSelected;
			}
		}
		
        override protected function configUI() : void
        {
            super.configUI();
            
            this.mouseChildren = true;
            this.removeBtn.mouseEnabled = this.removeBtn.mouseChildren = true;
            this.icon.mouseEnabled = this.icon.mouseChildren = false;
            this.targetMC.mouseEnabled = this.targetMC.mouseChildren = false;
            this.textField.mouseEnabled = false;
            this.descField.mouseEnabled = false;
            this.errorField.mouseEnabled = false;
            addEventListener(MouseEvent.CLICK, this.onClickHandler);
            soundType = SoundTypes.NORMAL_BTN;
            if(this.hitMc)
            {
                hitArea = this.hitMc;
            }
        }
	}
}