package omnilab.mtclassic_test.hangar.legacyAmmoPanel.components 
{
	import flash.display.*;

	import net.wg.gui.components.advanced.ModuleTypesUIWithFill;
	import net.wg.gui.components.controls.Image;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.gui.lobby.components.data.DeviceSlotVO;
	import scaleform.clik.constants.InvalidationType;
	import org.idmedia.as3commons.util.StringUtils;
	import omnilab.wotclassic.test.TestDropDown;
	import scaleform.clik.data.DataProvider;
	import omnilab.wotclassic.maintenance.gui.lobby.components.maintenance.MaintenanceDropDown;
	import omnilab.mtclassic_test.hangar.legacyAmmoPanel.data.LegacyListItemVO;
	import omnilab.wotclassic.legacyAmmoPanel.LegacyAmmoPanel;
	
	public class LegacySlot extends SoundButtonEx 
	{
		public var moduleType:ModuleTypesUIWithFill = null;
		public var locked:MovieClip = null;
		public var alertIcon:Image = null;
		public var greenBorderMc:MovieClip = null;
		public var equipSlotHighlight:MovieClip = null;
        public var levelMC:MovieClip = null;
		public var equipSlotOverlay:MovieClip = null;
		// public var background:MovieClip = null;
		public var select: LegacyDropDown = null;

		public var slotIndex: int;
		public var slotType: String;
		public var slotData: DeviceSlotVO = null;
		
		public function LegacySlot() 
		{
			super();
			preventAutosizing = true;
			
		}

		override protected function configUI() : void 
		{
			super.configUI();
            this.select.handleScroll = true;
			focusTarget = this.select;
			this.displayFocus
			focusable = tabEnabled = tabChildren = true;
			if(this.equipSlotOverlay)
			{
				this.equipSlotOverlay.mouseEnabled = this.equipSlotOverlay.mouseChildren = false;
			}
		}

		public function update(data: DeviceSlotVO)
		{
			this.slotData = data;
			this.enabled = !this.slotData.slotLocked;
			this.select.itemRenderer = this.slotData.slotType.indexOf("vehicle") != -1 ? "ModuleListItemRendererUI" : "TestListItemRendererUI";
			this.select.menuWidth = this.slotData.slotType.indexOf("vehicle") != -1 ? 391 : 447;
			invalidate(InvalidationType.DATA);
		}
		
		public function updateSelect(data: Array): void {
			var dataProv: DataProvider = new DataProvider(data);
			var maxItemsCount: int = Math.round((App.appHeight - 500) / 58);

			this.select.rowCount = Math.min(maxItemsCount, dataProv.length);
			this.select.dataProvider = dataProv;
			// this.select.validateNow();
		}
		
		override protected function draw() : void 
		{
			var isEmpty:Boolean = false;
			var moduleLabel:String = null;
			var affectsAtTTC:Boolean = false;
			var extraModuleInfo:String = null;
			var bgHighlightType:String = null;
			var isSlotHighlight:Boolean = false;
			var overlayType:String = null;
			var isSlotOverlay:Boolean = false;
			var moduleLevel:int = 0;

			super.draw();
			
			if(this.slotData != null && isInvalid(InvalidationType.DATA))
			{
				isEmpty = this.isEmpty();
				affectsAtTTC = this.slotData.affectsAtTTC;
				this.moduleType.moduleIcon.source = "../maps/icons/moduleTypes/" + this.slotData.moduleLabel + ".png";
				this.locked.visible = !!isEmpty ? Boolean(false) : Boolean(!this.slotData.removable);
				this.moduleType.alpha = isEmpty || affectsAtTTC ? 1 : 0.5;
				extraModuleInfo = this.slotData.extraModuleInfo;
				
				if(isEmpty || StringUtils.isEmpty(extraModuleInfo))
				{
					this.moduleType.hideExtraIcon();
				}
				else
				{
					this.moduleType.setExtraIconBySource(extraModuleInfo);
					this.moduleType.showExtraIcon();
				}
				this.moduleType.validateNow();
				this.greenBorderMc.visible = this.slotData.highlight;
				this.alertIcon.visible = !affectsAtTTC;
				if(!affectsAtTTC && StringUtils.isEmpty(this.alertIcon.source))
				{
					this.alertIcon.source = RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_32X32;
				}
				bgHighlightType = this.slotData.bgHighlightType;
				isSlotHighlight = StringUtils.isNotEmpty(bgHighlightType);
				this.equipSlotHighlight.visible = isSlotHighlight;
				if(isSlotHighlight)
				{
					this.equipSlotHighlight.gotoAndStop(bgHighlightType);
				}
				overlayType = this.slotData.overlayType;
				isSlotOverlay = StringUtils.isNotEmpty(overlayType);
				this.equipSlotOverlay.visible = isSlotOverlay;
				if(isSlotOverlay)
				{
					this.equipSlotOverlay.gotoAndStop(overlayType);
				}
				moduleLevel = this.slotData.level;
				if(moduleLevel != -1) 
				{
					this.levelMC.gotoAndStop(moduleLevel);
					this.levelMC.visible = true;
				} else 
				{
					this.levelMC.visible = false;
				}
				this.mouseChildren = !this.slotData.slotLocked;
			}
		}
      
		protected function isEmpty() : Boolean
		{
			return isNaN(this.slotData.id);
		}
	}
}