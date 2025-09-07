package omnilab.wotclassic.legacyAmmoPanel.components
{
    import flash.display.MovieClip;
    import net.wg.data.constants.generated.FITTING_TYPES;
    import net.wg.data.constants.generated.TOOLTIPS_CONSTANTS;
    import net.wg.gui.components.advanced.ModuleTypesUIWithFill;
    import net.wg.gui.components.controls.Image;
    import net.wg.gui.lobby.modulesPanel.components.DeviceSlot;
    import org.idmedia.as3commons.util.StringUtils;
    import scaleform.clik.constants.InvalidationType;
	import net.wg.infrastructure.managers.ITooltipMgr;
    import flash.events.MouseEvent;
    
    public class BattleAbilitySlot extends DeviceSlot
    {
        
        private static const EMPTY:String = "empty";
        private static const AFFECTS_TTC_ALPHA:Number = 1;
        private static const NOT_AFFECTS_TTC_ALPHA:Number = 0.5;
		
        public var moduleType:ModuleTypesUIWithFill = null;
        public var locked:MovieClip = null;
        public var alertIcon:Image = null;
        public var greenBorderMc:MovieClip = null;
        public var equipSlotHighlight:MovieClip = null;
        public var levelMC:MovieClip = null;
        public var equipSlotOverlay:MovieClip = null;
		
        private var _isAvailable:Boolean = false;
		private var _toolTipMgr:ITooltipMgr;
        
        public function BattleAbilitySlot()
        {
            super();
			this._toolTipMgr = App.toolTipMgr;
            preventAutosizing = true;
        }
        
        override public function update(param1:Object) : void
        {
            super.update(param1);
            this._isAvailable = true;
        }
        
        override protected function configUI() : void
        {
            super.configUI();
            if(this.equipSlotOverlay)
            {
                this.equipSlotOverlay.mouseEnabled = this.equipSlotOverlay.mouseChildren = false;
            }
			addEventListener(MouseEvent.ROLL_OVER,this.onRollOverHandler);
			addEventListener(MouseEvent.ROLL_OUT,this.onRollOutHandler);
        }
        
        override protected function onDispose() : void
        {
			removeEventListener(MouseEvent.ROLL_OVER, this.onRollOverHandler);
			removeEventListener(MouseEvent.ROLL_OUT, this.onRollOutHandler);
            this.moduleType.dispose();
            this.moduleType = null;
            this.locked = null;
            this.alertIcon.dispose();
            this.alertIcon = null;
            this.greenBorderMc = null;
            this.equipSlotHighlight = null;
            this.levelMC = null;
            this.equipSlotOverlay = null;
            super.onDispose();
        }
        
        override protected function draw() : void
        {
            var _loc1_:Boolean = false;
            var _loc2_:String = null;
            var _loc3_:* = false;
            var _loc4_:Boolean = false;
            var _loc5_:String = null;
            var _loc6_:Boolean = false;
            var _loc7_:int = 0;
            super.draw();
            if(slotData != null && isInvalid(InvalidationType.DATA))
            {
                _loc1_ = isEmpty();
                _loc2_ = _loc1_ ? EMPTY : slotData.moduleLabel;
                _loc3_ = type == FITTING_TYPES.BOOSTER;
                _loc4_ = slotData.affectsAtTTC;
                this.moduleType.moduleIcon.source = "../" + "maps/icons/moduleTypes/" + slotData.moduleLabel + ".png";
                this.locked.visible = _loc3_ ? false : (_loc1_ ? false : !slotData.removable);
                this.moduleType.alpha = _loc1_ || _loc4_ ? AFFECTS_TTC_ALPHA : NOT_AFFECTS_TTC_ALPHA;
                this.greenBorderMc.visible = slotData.highlight;
                this.alertIcon.visible = !_loc4_;
                if(this.alertIcon.visible && StringUtils.isEmpty(this.alertIcon.source))
                {
                    this.alertIcon.source = RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_32X32;
                }
                _loc5_ = slotData.bgHighlightType;
                _loc6_ = StringUtils.isNotEmpty(_loc5_);
                this.equipSlotHighlight.visible = this.equipSlotOverlay.visible = _loc6_;
                if(_loc6_)
                {
                    this.equipSlotHighlight.gotoAndStop(_loc5_);
                    this.equipSlotOverlay.gotoAndStop(_loc5_);
                }
                if((_loc7_ = slotData.level) > 0)
                {
                    this.levelMC.gotoAndStop(slotData.level);
                    this.levelMC.visible = true;
                }
                else
                {
                    this.levelMC.visible = false;
                }
            }
        }
		
		private function onRollOverHandler(param1:MouseEvent) : void
		{
			if(this.slotData && StringUtils.isNotEmpty(this.slotData.tooltipType))
			{
				if(TOOLTIPS_CONSTANTS.COMPLEX == this.slotData.tooltipType)
				{
				   this._toolTipMgr.showComplex(this.slotData.tooltip);
				}
				else if(this.slotData.tooltipType == "abilityLobbyTooltip")
				{
				   this._toolTipMgr.showWulfTooltip(this.slotData.tooltipType, this.slotData.id, this.slotData.slotIndex);
				}
				else if(!this.isEmpty())
				{
				   this._toolTipMgr.showWulfTooltip(this.slotData.tooltipType, this.slotData.id, this.slotData.slotIndex);
				}
			 }
		}
      
		private function onRollOutHandler(param1:MouseEvent) : void
		{
			this._toolTipMgr.hide();
		}
        
        public function get isAvailable() : Boolean
        {
            return this._isAvailable;
        }
        
        public function set isAvailable(param1:Boolean) : void
        {
            this._isAvailable = param1;
        }
    }
}
