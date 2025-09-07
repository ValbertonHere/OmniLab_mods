package omnilab.wotclassic.legacyAmmoPanel.components
{
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.MouseEvent;
    import flash.text.TextField;
    import net.wg.gui.components.controls.UILoaderAlt;
    import net.wg.gui.events.DeviceEvent;
    import net.wg.gui.interfaces.ISoundButtonEx;
    import org.idmedia.as3commons.util.StringUtils;
    import scaleform.clik.events.ButtonEvent;
	import net.wg.gui.lobby.modulesPanel.components.FittingListItemRenderer;
	
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyBoosterVO;
    
    public class BoosterFittingItemRenderer extends FittingListItemRenderer
    {
        
        private static const AFFECTED_ALPHA:int = 1;
        private static const NOT_AFFECTED_ALPHA:Number = 0.5;
        private static const MAX_LINE_NUMBER:uint = 2;
        private static const DOTS:String = "...";
        private static const TARGET_VEHICLE:String = "vehicle";
         
        public var removeButton:ISoundButtonEx = null;
        public var buyButton:ISoundButtonEx = null;
        public var descField:TextField = null;
        public var notAffected:UILoaderAlt = null;
        public var targetField:TextField = null;
        public var moduleOverlay:MovieClip = null;
        public var moduleHighlight:MovieClip = null;
        
        private var _boosterItemVO:LegacyBoosterVO = null;
        private var _descVisible:Boolean = true;
        
        public function BoosterFittingItemRenderer()
        {
            var _loc2_:DisplayObject = null;
            super();
            var _loc1_:Vector.<DisplayObject> = new <DisplayObject>[this.targetField,this.notAffected];
            for each(_loc2_ in _loc1_)
            {
                rightOffsets[_loc2_] = width - _loc2_.x;
            }
            _loc1_.splice(0, _loc1_.length);
        }
        
        override public function setData(param1:Object) : void
        {
            super.setData(param1);
            this._boosterItemVO = LegacyBoosterVO(param1);
			this.rendererBg.gotoAndPlay(this.getButtonAnimGroup + "up");
        }
        
        override protected function onDispose() : void
        {
            this.buyButton.dispose();
            this.buyButton = null;
            this.removeButton.dispose();
            this.removeButton = null;
            this.notAffected.dispose();
            this.notAffected = null;
            this.descField = null;
            this.targetField = null;
            if(this._boosterItemVO)
            {
                this._boosterItemVO.dispose();
                this._boosterItemVO = null;
            }
            this.moduleHighlight = null;
            this.moduleOverlay = null;
            super.onDispose();
        }
        
        override protected function onBeforeDispose() : void
        {
            this.buyButton.removeEventListener(ButtonEvent.CLICK,this.onBuyButtonClickHandler);
            this.removeButton.removeEventListener(ButtonEvent.CLICK,this.onRemoveButtonClickHandler);
            super.onBeforeDispose();
        }
        
        override protected function configUI() : void
        {
            super.configUI();
            errorField.visible = false;
            this.buyButton.focusTarget = this;
            this.buyButton.addEventListener(ButtonEvent.CLICK,this.onBuyButtonClickHandler);
            this.removeButton.focusTarget = this;
            this.removeButton.addEventListener(ButtonEvent.CLICK,this.onRemoveButtonClickHandler);
            this.notAffected.visible = false;
            this.notAffected.mouseEnabled = this.notAffected.mouseChildren = false;
            this.descField.mouseEnabled = false;
            this.notAffected.source = RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON;
			this.notAffected.height = 24;
			this.notAffected.width = 36;
        }
        
        override protected function setup() : void
        {
            var _loc1_:Boolean = false;
            super.setup();
            if(this._boosterItemVO != null)
            {
                _loc1_ = this._boosterItemVO.isSelected;
                if(!_loc1_)
                {
                    this.removeButton.visible = false;
                    this._descVisible = this.descField.visible = StringUtils.isNotEmpty(this._boosterItemVO.desc);
                    if(this._descVisible)
                    {
                        this.setTruncatedHtmlText(this.descField,this._boosterItemVO.desc,MAX_LINE_NUMBER);
                        App.utils.commons.updateTextFieldSize(this.descField,false,true);
                    }
                    selected = false;
                }
                else
                {
                    this.removeButton.visible = true;
                    this._descVisible = this.descField.visible = false;
                }
                this.buyButton.visible = this._boosterItemVO.buyButtonVisible;
                this.buyButton.label = this._boosterItemVO.buyButtonLabel;
                this.buyButton.tooltip = this._boosterItemVO.buyButtonTooltip;
                this.removeButton.label = this._boosterItemVO.removeButtonLabel;
                this.removeButton.tooltip = this._boosterItemVO.removeButtonTooltip;
                if(this._boosterItemVO.notAffectedTTC && !(_data && !enabled))
                {
                    this.descField.alpha = titleField.alpha = NOT_AFFECTED_ALPHA;
                }
                else
                {
                    this.descField.alpha = titleField.alpha = AFFECTED_ALPHA;
                }
                this.notAffected.visible = this._boosterItemVO.notAffectedTTC;
                if(StringUtils.isNotEmpty(this._boosterItemVO.highlightType))
                {
                    this.moduleHighlight.gotoAndStop(this._boosterItemVO.highlightType);
                    this.moduleOverlay.gotoAndStop(this._boosterItemVO.highlightType);
                    this.moduleHighlight.visible = this.moduleOverlay.visible = true;
                }
                else
                {
                    this.moduleHighlight.visible = this.moduleOverlay.visible = false;
                }
            }
        }
        
        override protected function setupTarget() : void
        {
            super.setupTarget();
            if(this._boosterItemVO.targetVisible && this._boosterItemVO.target != TARGET_VEHICLE)
            {
                this.targetField.text = String(this._boosterItemVO.count);
                this.targetField.visible = true;
            }
            else
            {
                this.targetField.visible = false;
            }
        }
        
        private function setTruncatedHtmlText(param1:TextField, param2:String, param3:uint) : void
        {
            var _loc4_:String = param2;
            this.descField.htmlText = _loc4_;
            while(param1.numLines > param3)
            {
                _loc4_ = _loc4_.substr(0,_loc4_.length - 1);
                this.descField.htmlText = _loc4_ + DOTS;
            }
        }
        
        override protected function handleUserClick(param1:MouseEvent) : void
        {
            hideTooltip();
        }
        
        private function onBuyButtonClickHandler(param1:ButtonEvent) : void
        {
            param1.stopImmediatePropagation();
            dispatchEvent(new DeviceEvent(DeviceEvent.DEVICE_BUY,this._boosterItemVO.id));
        }
        
        private function onRemoveButtonClickHandler(param1:ButtonEvent) : void
        {
            param1.stopImmediatePropagation();
            dispatchEvent(new DeviceEvent(DeviceEvent.DEVICE_REMOVE,this._boosterItemVO.id));
        }
	  
		override protected function handleMouseRollOver(param0:MouseEvent): void
		{
			super.handleMouseRollOver(param0);
			this.rendererBg.gotoAndPlay(this.getButtonAnimGroup + "over");
		}
	  
		override protected function handleMouseRollOut(param0:MouseEvent): void
		{
			super.handleMouseRollOut(param0);
			this.rendererBg.gotoAndPlay(this.getButtonAnimGroup + "up");
		}
		
	  
		private function get getButtonAnimGroup(): String 
		{
			switch (true) {
				case this._boosterItemVO.disabled:
					return "passive_";
					break;
				case this._boosterItemVO.isSelected:
					return "selected_";
					break;
				default:
					return "";
			}
		}
    }
}
