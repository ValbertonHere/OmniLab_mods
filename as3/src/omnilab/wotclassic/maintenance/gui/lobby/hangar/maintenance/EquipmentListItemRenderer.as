package omnilab.wotclassic.maintenance.gui.lobby.hangar.maintenance
{
    import flash.display.MovieClip;
    import flash.events.MouseEvent;
    import flash.text.TextField;
    import net.wg.data.constants.Currencies;
    import net.wg.data.constants.SoundTypes;
    import net.wg.data.constants.Values;
    import net.wg.data.constants.generated.CURRENCIES_CONSTANTS;
    import net.wg.gui.components.advanced.ModuleTypesUIWithFill;
    import net.wg.gui.components.controls.ActionPrice;
    import net.wg.gui.components.controls.BitmapFill;
    import net.wg.gui.components.controls.IconText;
    import net.wg.gui.components.controls.SoundListItemRenderer;
    import net.wg.gui.components.controls.VO.ActionPriceVO;
    import net.wg.gui.events.ModuleInfoEvent;
    import omnilab.wotclassic.maintenance.gui.lobby.components.maintenance.data.ModuleVO;
    import omnilab.wotclassic.maintenance.gui.lobby.components.maintenance.events.OnEquipmentRendererOver;
    import org.idmedia.as3commons.util.StringUtils;
    import scaleform.clik.constants.InvalidationType;
    import scaleform.gfx.MouseEventEx;
    
    public class EquipmentListItemRenderer extends SoundListItemRenderer
    {
        
        private static const RENDERER_HEIGHT:int = 48;
        
        private static const SHOP:String = "shop";
        
        private static const HANGAR:String = "hangar";
        
        private static const HANGAR_CANT_INSTALL:String = "hangarCantInstall";
        
        private static const VEHICLE:String = "vehicle";
        
        private static const MODULE_ICON_OFFSET:int = -5;
         
        
        public var disabledOverlayMc:BitmapFill;
        
        public var disableMc:BitmapFill;
        
        public var slotOverlay:MovieClip;
        
        public var moduleType:ModuleTypesUIWithFill;
        
        public var titleField:TextField;
        
        public var descField:TextField;
        
        public var errorField:TextField;
        
        public var priceMC:IconText;
        
        public var targetMC:MovieClip;
		
		public var actionPriceBG:MovieClip;
        
        public var hitMc:MovieClip;
        
        public function EquipmentListItemRenderer()
        {
            super();
        }
        
        override public function setData(param1:Object) : void
        {
            super.setData(param1);
            invalidate(InvalidationType.DATA);
        }
        
        override protected function configUI() : void
        {
            super.configUI();
            addEventListener(MouseEvent.ROLL_OVER,this.onRollOverHandler);
            addEventListener(MouseEvent.ROLL_OUT,this.onRollOutHandler);
            addEventListener(MouseEvent.CLICK,this.onClickHandler);
            soundType = SoundTypes.NORMAL_BTN;
            this.slotOverlay.visible = false;
            this.slotOverlay.mouseEnabled = this.slotOverlay.mouseChildren = false;
            if(this.hitMc)
            {
                hitArea = this.hitMc;
            }
            preventAutosizing = true;
        }
        
        override protected function onDispose() : void
        {
            removeEventListener(MouseEvent.ROLL_OVER,this.onRollOverHandler);
            removeEventListener(MouseEvent.ROLL_OUT,this.onRollOutHandler);
            removeEventListener(MouseEvent.CLICK,this.onClickHandler);
            this.disabledOverlayMc.dispose();
            this.disabledOverlayMc = null;
            this.disableMc.dispose();
            this.disableMc = null;
            this.slotOverlay = null;
            this.moduleType.dispose();
            this.moduleType = null;
            this.titleField = null;
            this.descField = null;
            this.priceMC.dispose();
            this.priceMC = null;
            this.targetMC = null;
            this.hitMc = null;
            this.errorField = null;
            super.onDispose();
        }
        
        override protected function draw() : void
        {
            var _loc1_:ModuleVO = null;
            var _loc2_:String = null;
            var _loc3_:Boolean = false;
            var _loc4_:Boolean = false;
            var _loc5_:Boolean = false;
            if(isInvalid(InvalidationType.DATA))
            {
                if(data)
                {
                    visible = true;
                    _loc1_ = this.module;
                    if(_loc1_.inSetup && _loc1_.status != Values.EMPTY_STR)
                    {
                        this.titleField.text = this.descField.text = Values.EMPTY_STR;
                    }
                    else
                    {
                        this.titleField.text = _loc1_.name;
                        this.descField.text = _loc1_.desc;
                    }
                    this.moduleType.moduleIcon.source = "../" + "maps/icons/moduleTypes/" + _loc1_.moduleLabel + ".png";
					this.priceMC.visible = false;
					this.actionPriceBG.visible = false;
                    _loc2_ = this.module.highlightType;
                    _loc3_ = StringUtils.isNotEmpty(_loc2_);
                    this.slotOverlay.visible = _loc3_;
                    if(_loc3_)
                    {
                        this.slotOverlay.gotoAndStop(_loc2_);
                    }
                    if(_loc1_.inSetup)
                    {
                        this.targetMC.gotoAndPlay(VEHICLE);
                        this.targetMC.textField.text = _loc1_.status == Values.EMPTY_STR ? Values.EMPTY_STR : MENU.FITTINGLISTITEMRENDERER_REPLACE;
                    }
                    else if(_loc1_.isInInventory)
                    {
                        if(_loc1_.status == Values.EMPTY_STR)
                        {
                            this.targetMC.gotoAndPlay(HANGAR);
                        }
                        else if(_loc1_.status != MENU.MODULEFITS_CREDITS_ERROR && _loc1_.status == MENU.MODULEFITS_GOLD_ERROR)
                        {
                            this.targetMC.gotoAndPlay(HANGAR_CANT_INSTALL);
                        }
                    }
                    else
                    {
						_loc5_ = _loc1_.inSetup || _loc1_.isInInventory
                        this.priceMC.visible = !_loc5_;
                        if(this.priceMC.visible)
                        {
							this.actionPriceBG.visible = _loc1_.isActionPrice;
							if (this.actionPriceBG.visible) {
								this.actionPriceBG.gotoAndStop("alignTop");
								this.priceMC.x = 210;
							}
                            this.priceMC.text = App.utils.locale.integer(_loc1_.itemPrices[0].price.getPriceVO().value);
                            this.priceMC.textColor = this.getPriceColor();
                            this.priceMC.icon = _loc1_.currency;
                            this.priceMC.validateNow();
                        }
                        this.targetMC.gotoAndStop(SHOP);
						
                    }
                    this.errorField.text = _loc1_.status;
                    _loc4_ = !_loc1_.disabled && (_loc1_.status != MENU.MODULEFITS_UNLOCK_ERROR && _loc1_.status != MENU.MODULEFITS_NOT_WITH_INSTALLED_EQUIPMENT);
                    enabled = _loc4_;
                    this.disabledOverlayMc.visible = this.disableMc.visible = !_loc4_;
                    this.disabledOverlayMc.validateNow();
                    this.disableMc.validateNow();
                    mouseEnabled = true;
                }
                else
                {
                    visible = false;
                }
            }
            super.draw();
        }
        
        override protected function updateAfterStateChange() : void
        {
            super.updateAfterStateChange();
            this.moduleType.scaleX = this.moduleType.scaleY = 1;
            this.moduleType.x = MODULE_ICON_OFFSET;
            this.moduleType.y = MODULE_ICON_OFFSET;
        }
        
        override public function get height() : Number
        {
            return RENDERER_HEIGHT;
        }
        
        override public function set height(param1:Number) : void
        {
        }
        
        override public function set width(param1:Number) : void
        {
        }
        
        private function get module() : ModuleVO
        {
            return data as ModuleVO;
        }
        
        private function getPriceColor() : uint
        {
            var _loc1_:ModuleVO = this.module;
            if(_loc1_.price < _loc1_.userCredits[_loc1_.currency])
            {
                if(_loc1_.status == MENU.MODULEFITS_NOT_WITH_INSTALLED_EQUIPMENT)
                {
                    return Currencies.DISABLED_COLOR;
                }
                return Currencies.TEXT_COLORS[_loc1_.currency];
            }
            return Currencies.TEXT_COLORS[CURRENCIES_CONSTANTS.ERROR];
        }
        
        private function onRollOverHandler(param1:MouseEvent) : void
        {
            owner.dispatchEvent(new OnEquipmentRendererOver(OnEquipmentRendererOver.ON_EQUIPMENT_RENDERER_OVER,this.module.id,this.module.prices,this.module.inventoryCount,this.module.vehicleCount,this.module.slotIndex));
        }
        
        private function onRollOutHandler(param1:MouseEvent) : void
        {
            App.toolTipMgr.hide();
        }
        
        private function onClickHandler(param1:MouseEvent) : void
        {
            App.toolTipMgr.hide();
            if(param1 is MouseEventEx)
            {
                if(App.utils.commons.isRightButton(param1))
                {
                    dispatchEvent(new ModuleInfoEvent(ModuleInfoEvent.SHOW_INFO,this.module.id));
                }
            }
        }
    }
}
