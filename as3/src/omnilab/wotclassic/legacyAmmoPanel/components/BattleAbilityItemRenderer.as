package omnilab.wotclassic.legacyAmmoPanel.components
{
    import flash.display.MovieClip;
    import flash.text.TextField;
    import net.wg.data.constants.SoundTypes;
    import net.wg.data.constants.Values;
    import net.wg.gui.events.DeviceEvent;
    import net.wg.gui.interfaces.ISoundButtonEx;
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyBattleAbilityVO;
    import net.wg.infrastructure.managers.ITooltipMgr;
    import org.idmedia.as3commons.util.StringUtils;
    import scaleform.clik.constants.InvalidationType;
    import scaleform.clik.events.ButtonEvent;
    import scaleform.clik.events.ListEvent;
	import net.wg.gui.lobby.modulesPanel.components.FittingListItemRenderer;
	import flash.events.MouseEvent;
    
    public class BattleAbilityItemRenderer extends FittingListItemRenderer
    {
        
        private static const EQUIPPED_ON_VEHICLE:String = "vehicle";
        
        private static const BUTTON_WIDTH:int = 140;
        
        private static const DISABLED_ALPHA:Number = 0.5;
        
        private static const NOT_ACTIVATED_TF_OFFSET:int = 15;
         
        
        public var descField:TextField = null;
        
        public var notActivatedTF:TextField = null;
        
        public var removeButton:ISoundButtonEx = null;
        
        private var _battleAbilityVO:LegacyBattleAbilityVO = null;
        
        private var _tooltipMgr:ITooltipMgr;
        
        public function BattleAbilityItemRenderer()
        {
            this._tooltipMgr = App.toolTipMgr;
            super();
        }
        
        override public function setData(param1:Object) : void
        {
            super.setData(param1);
            this._battleAbilityVO = LegacyBattleAbilityVO(param1);
			if (_battleAbilityVO != null) {
				this.rendererBg.gotoAndPlay(this.getButtonAnimGroup + "up");
			}
        }
        
        override protected function draw() : void
        {
            super.draw();
            if(isInvalid(InvalidationType.SIZE))
            {
                this.notActivatedTF.x = width - this.notActivatedTF.width - NOT_ACTIVATED_TF_OFFSET | 0;
            }
        }
        
        override protected function configUI() : void
        {
            super.configUI();
            this.removeButton.visible = false;
            this.removeButton.focusTarget = this;
            this.removeButton.width = BUTTON_WIDTH;
            this.removeButton.addEventListener(ButtonEvent.CLICK,this.onRemoveButtonClickHandler);
            this.removeButton.soundType = SoundTypes.ITEM_RDR;
            this.descField.mouseEnabled = this.notActivatedTF.mouseEnabled = false;
			this.notActivatedTF.text = "Не активирован";
			this.notActivatedTF.alpha = DISABLED_ALPHA;
        }
        
        override protected function onDispose() : void
        {
            this.removeButton.removeEventListener(ButtonEvent.CLICK,this.onRemoveButtonClickHandler);
            this.removeButton.dispose();
            this.removeButton = null;
            this.descField = null;
            this.notActivatedTF = null;
            this._battleAbilityVO = null;
            this._tooltipMgr = null;
            super.onDispose();
        }
        
        override protected function setup() : void
        {
            var _loc1_:Boolean = false;
            var _loc2_:String = null;
            var _loc3_:* = false;
            var _loc4_:Boolean = false;
            var _loc5_:int = 0;
            var _loc6_:String = null;
            var _loc7_:Boolean = false;
            super.setup();
            if(this._battleAbilityVO != null)
            {
                _loc1_ = this._battleAbilityVO.isSelected;
                _loc2_ = this._battleAbilityVO.filterText;
                _loc3_ = _loc2_ != Values.EMPTY_STR;
                _loc4_ = !_loc1_ && this._battleAbilityVO.target == EQUIPPED_ON_VEHICLE;
                _loc5_ = this._battleAbilityVO.level;
				this.moduleType.moduleIcon.source = "../" + "maps/icons/moduleTypes/" + _battleAbilityVO.moduleLabel + ".png";
                _loc6_ = this._battleAbilityVO.desc;
                if(this.descField.visible)
                {
                    App.utils.commons.truncateTextFieldText(this.descField,_loc6_,false,true);
                }
                errorField.visible = false;
                this.notActivatedTF.visible = this._battleAbilityVO.disabled;
            }
        }
        
        override protected function showItemTooltip() : void
        {
            this._tooltipMgr.showSpecial(this._battleAbilityVO.tooltipType,null,this._battleAbilityVO.id,this._battleAbilityVO.slotIndex);
        }
        
        private function onRemoveButtonClickHandler(param1:ButtonEvent) : void
        {
            dispatchEvent(new DeviceEvent(DeviceEvent.DEVICE_REMOVE,this._battleAbilityVO.id));
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
				case this._battleAbilityVO.disabled:
					return "passive_";
					break;
				case this._battleAbilityVO.isSelected:
					return "selected_";
					break;
				default:
					return "";
			}
		}
    }
}
