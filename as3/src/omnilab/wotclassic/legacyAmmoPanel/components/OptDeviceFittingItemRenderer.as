package omnilab.wotclassic.legacyAmmoPanel.components
{
	import flash.display.MovieClip;
	import flash.events.MouseEvent;
	import flash.text.TextField;
	import net.wg.gui.events.DeviceEvent;
	import net.wg.gui.interfaces.ISoundButtonEx;
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyOptDeviceVO;
	import org.idmedia.as3commons.util.StringUtils;
	import scaleform.clik.events.ButtonEvent;
	import net.wg.gui.lobby.modulesPanel.components.FittingListItemRenderer;
   
	public class OptDeviceFittingItemRenderer extends FittingListItemRenderer
	{
      
		private static const AFFECTED_ALPHA: int = 1;
		private static const NOT_AFFECTED_ALPHA: Number = 0.5;
		private static const MAX_LINE_NUMBER: uint = 2;
		private static const DOTS: String = "...";
		private static const BG_HIGHLIGHT_GAP: int = 2;
		private static const BUTTONS_WIDTH: int = 142;
		private static const SMALL_BUTTONS_WIDTH: int = 110;
		private static const BUTTONS_SPACING: int = 9;
		private static const BUTTONS_START_X: int = 78;
       
		public var removeButton: ISoundButtonEx;
		public var destroyButton: ISoundButtonEx;
		public var upgradeButton: ISoundButtonEx;
		public var installButton: ISoundButtonEx;
		public var locked: MovieClip;
		public var descField: TextField;
		public var bgHighlightMc: MovieClip = null;
		public var moduleOverlay: MovieClip = null;
		
		private var _optDevData: LegacyOptDeviceVO = null;
      
		public function OptDeviceFittingItemRenderer()
		{
			super();
		}
      
		override public function setData(param1:Object) : void
		{
			super.setData(param1);
			this._optDevData = LegacyOptDeviceVO(param1);
			if (_optDevData != null) {
				this.rendererBg.gotoAndPlay(this.getButtonAnimGroup + "up");
			}
		}
      
		override protected function showItemTooltip() : void
		{
			if(this._optDevData.notAffectedTTC)
			{
				App.toolTipMgr.showComplex(this._optDevData.notAffectedTTCTooltip);
			}
			else
			{
				super.showItemTooltip();
			}
		}
	  
		override protected function onDispose() : void
		{
			this.installButton.dispose();
			this.installButton = null;
			this.upgradeButton.dispose();
			this.upgradeButton = null;
			this.destroyButton.dispose();
			this.destroyButton = null;
			this.removeButton.dispose();
			this.removeButton = null;
			this.descField = null;
			this.locked = null;
			this._optDevData = null;
			this.bgHighlightMc = null;
			this.moduleOverlay = null;
			super.onDispose();
		}
      
		override protected function onBeforeDispose() : void
		{
			this.installButton.removeEventListener(ButtonEvent.CLICK,this.onInstallButtonClickHandler);
			this.installButton.removeEventListener(MouseEvent.ROLL_OVER,this.onInstallButtonRollOverHandler);
			this.installButton.removeEventListener(MouseEvent.ROLL_OUT,this.onInstallButtonRollOutHandler);
			this.upgradeButton.removeEventListener(ButtonEvent.CLICK,this.onUpgradeButtonClickHandler);
			this.upgradeButton.removeEventListener(MouseEvent.ROLL_OVER,this.onUpgradeButtonRollOverHandler);
			this.upgradeButton.removeEventListener(MouseEvent.ROLL_OUT,this.onUpgradeButtonRollOutHandler);
			this.destroyButton.removeEventListener(ButtonEvent.CLICK,this.onDestroyButtonClickHandler);
			this.destroyButton.removeEventListener(MouseEvent.ROLL_OVER,this.onDestroyButtonRollOverHandler);
			this.destroyButton.removeEventListener(MouseEvent.ROLL_OUT,this.onDestroyButtonRollOutHandler);
			this.removeButton.removeEventListener(ButtonEvent.CLICK,this.onRemoveButtonClickHandler);
			this.removeButton.removeEventListener(MouseEvent.ROLL_OVER,this.onRemoveButtonRollOverHandler);
			this.removeButton.removeEventListener(MouseEvent.ROLL_OUT,this.onRemoveButtonRollOutHandler);
			super.onBeforeDispose();
		}
	  
		override protected function configUI() : void
		{
			super.configUI();
			this.installButton.focusable = false;
			this.installButton.addEventListener(ButtonEvent.CLICK,this.onInstallButtonClickHandler);
			this.installButton.addEventListener(MouseEvent.ROLL_OVER,this.onInstallButtonRollOverHandler);
			this.installButton.addEventListener(MouseEvent.ROLL_OUT,this.onInstallButtonRollOutHandler);
			this.upgradeButton.focusable = false;
			this.upgradeButton.addEventListener(ButtonEvent.CLICK,this.onUpgradeButtonClickHandler);
			this.upgradeButton.addEventListener(MouseEvent.ROLL_OVER,this.onUpgradeButtonRollOverHandler);
			this.upgradeButton.addEventListener(MouseEvent.ROLL_OUT,this.onUpgradeButtonRollOutHandler);
			this.destroyButton.focusable = false;
			this.destroyButton.addEventListener(ButtonEvent.CLICK,this.onDestroyButtonClickHandler);
			this.destroyButton.addEventListener(MouseEvent.ROLL_OVER,this.onDestroyButtonRollOverHandler);
			this.destroyButton.addEventListener(MouseEvent.ROLL_OUT,this.onDestroyButtonRollOutHandler);
			this.removeButton.focusable = false;
			this.removeButton.addEventListener(ButtonEvent.CLICK,this.onRemoveButtonClickHandler);
			this.removeButton.addEventListener(MouseEvent.ROLL_OVER,this.onRemoveButtonRollOverHandler);
			this.removeButton.addEventListener(MouseEvent.ROLL_OUT,this.onRemoveButtonRollOutHandler);
			this.locked.visible = false;
			this.locked.mouseEnabled = this.locked.mouseChildren = false;
			this.bgHighlightMc.mouseEnabled = this.bgHighlightMc.mouseChildren = false;
			this.moduleOverlay.mouseEnabled = this.moduleOverlay.mouseChildren = false;
			this.descField.mouseEnabled = false;
		}
	  
		override protected function setup() : void
		{
			var _loc1_:Boolean = false;
			var _loc2_:Boolean = false;
			var _loc3_:Number = NaN;
			var _loc4_:Boolean = false;
			var _loc5_:Boolean = false;
			super.setup();
			if(this._optDevData != null)
			{
				_loc1_ = this._optDevData.isSelected;
				_loc2_ = this._optDevData.removable;
				_loc4_ = this._optDevData.isTrophyOrModern && !this._optDevData.disabled;
				this.moduleType.moduleIcon.source = "../" + "maps/icons/moduleTypes/" + _optDevData.moduleLabel + ".png"
				this.locked.visible = !_loc2_;
				this.destroyButton.visible = !_loc2_ && _loc1_;
				this.upgradeButton.visible = _loc4_  && this._optDevData.isUpgradable;
				this.installButton.visible = _loc4_ && !_loc1_;
				if(this.destroyButton.visible)
				{
					switch (this._optDevData.isTrophyOrModern) {
						case true:
							this.destroyButton.label = "#menu:cst_item_ctx_menu/deconstruct";
							break;
						case false:
							this.destroyButton.label = "#menu:cst_item_ctx_menu/destroy";
							break;
					}
					this.destroyButton.width = BUTTONS_WIDTH;
					this.destroyButton.x = BUTTONS_START_X + BUTTONS_SPACING + BUTTONS_WIDTH;
				}
				this.removeButton.visible = _loc1_;
				if(this.removeButton.visible)
				{
					this.removeButton.label = this._optDevData.removeButtonLabel;
					this.removeButton.tooltip = this._optDevData.removeButtonTooltip;
					this.removeButton.width = BUTTONS_WIDTH;
					this.removeButton.x = BUTTONS_START_X;
				}
				if(this.installButton.visible) {
					this.installButton.label = "#menu:contextMenu/equip";
					this.upgradeButton.x = BUTTONS_START_X + BUTTONS_SPACING + BUTTONS_WIDTH;
					this.upgradeButton.width = BUTTONS_WIDTH;
				}
				
				if(this.upgradeButton.visible)
				{
					this.upgradeButton.label = "#menu:cst_item_ctx_menu/upgrade";
					if (_loc1_) {
						this.upgradeButton.width = this.destroyButton.width = this.removeButton.width = SMALL_BUTTONS_WIDTH;
						this.upgradeButton.x = BUTTONS_START_X;
						this.removeButton.x = BUTTONS_START_X + BUTTONS_SPACING + SMALL_BUTTONS_WIDTH;
						this.destroyButton.x =  this.removeButton.x + BUTTONS_SPACING + SMALL_BUTTONS_WIDTH;
					}
				}
				this.removeButton.visible = _loc1_;
				_loc5_ = _loc1_ || _loc4_
				this.descField.visible = !_loc5_ && StringUtils.isNotEmpty(this._optDevData.desc);
				if(this.descField.visible)
				{
					this.setTruncatedHtmlText(this.descField,this._optDevData.desc,MAX_LINE_NUMBER);
					App.utils.commons.updateTextFieldSize(this.descField,false,true);
					if(!this._optDevData.notAffectedTTC)
					{
						layoutErrorField(this.descField);
					}
				}
				_loc3_ = this._optDevData.notAffectedTTC ? NOT_AFFECTED_ALPHA : AFFECTED_ALPHA;
				this.descField.alpha = titleField.alpha = moduleType.alpha = _loc3_;
				errorField.visible = this._optDevData.notAffectedTTC || !this._optDevData.isSelected && StringUtils.isNotEmpty(this._optDevData.status);
				if(errorField.visible)
				{
					errorField.htmlText = this._optDevData.status;
					App.utils.commons.updateTextFieldSize(errorField,false,true);
				}
				if(StringUtils.isNotEmpty(this._optDevData.overlayType))
				{
					this.moduleOverlay.gotoAndStop(this._optDevData.overlayType);
					this.moduleOverlay.visible = true;
				}
				else
				{
					this.moduleOverlay.visible = false;
				}
				this.updateBgHighlight();
			}
		}
      
		override protected function updateAfterStateChange() : void
		{
			super.updateAfterStateChange();
			if(initialized && Boolean(this._optDevData))
			{
				this.updateBgHighlight();
			}
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
				case this._optDevData.disabled:
					return "passive_";
					break;
				case this._optDevData.isSelected:
					return "selected_";
					break;
				default:
					return "";
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
      
		private function mouseHitTest() : Boolean
		{
			return hitTestPoint(App.stage.mouseX,App.stage.mouseY,true);
		}
      
		private function updateBgHighlight() : void
		{
			this.bgHighlightMc.visible = StringUtils.isNotEmpty(this._optDevData.bgHighlightType);
			this.bgHighlightMc.gotoAndStop(this._optDevData.bgHighlightType);
		}
      
		private function onInstallButtonRollOverHandler(param1:MouseEvent) : void
		{
			hideTooltip();
		}
      
		private function onInstallButtonRollOutHandler(param1:MouseEvent) : void
		{
			if(this.mouseHitTest())
			{
				this.showItemTooltip();
			}
		}
      
		private function onUpgradeButtonRollOverHandler(param1:MouseEvent) : void
		{
			hideTooltip();
		}
      
		private function onUpgradeButtonRollOutHandler(param1:MouseEvent) : void
		{
			if(this.mouseHitTest())
			{
				this.showItemTooltip();
			}
		}
	  
		private function onDestroyButtonRollOverHandler(param1:MouseEvent) : void
		{
			hideTooltip();
		}
      
		private function onDestroyButtonRollOutHandler(param1:MouseEvent) : void
		{
			if(this.mouseHitTest())
			{
				this.showItemTooltip();
			}
		}
      
		private function onRemoveButtonRollOverHandler(param1:MouseEvent) : void
		{
			hideTooltip();
		}
      
		private function onRemoveButtonRollOutHandler(param1:MouseEvent) : void
		{
			if(this.mouseHitTest())
			{
				this.showItemTooltip();
			}
		}
      
		private function onInstallButtonClickHandler(param1:ButtonEvent) : void
		{
			dispatchEvent(new DeviceEvent(DeviceEvent.DEVICE_BUY, this._optDevData.id));
		}
      
		private function onUpgradeButtonClickHandler(param1:ButtonEvent) : void
		{
			dispatchEvent(new DeviceEvent(DeviceEvent.DEVICE_UPGRADE, this._optDevData.id));
		}
      
		private function onDestroyButtonClickHandler(param1:ButtonEvent) : void
		{
			dispatchEvent(new DeviceEvent(DeviceEvent.DEVICE_DESTROY, this._optDevData.id));
		}
      
		private function onRemoveButtonClickHandler(param1:ButtonEvent) : void
		{
			dispatchEvent(new DeviceEvent(DeviceEvent.DEVICE_REMOVE,this._optDevData.id));
		}
	}
}