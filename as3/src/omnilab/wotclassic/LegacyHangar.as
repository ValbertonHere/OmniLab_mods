package omnilab.wotclassic 
{
	import flash.display.MovieClip;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import net.wg.gui.lobby.hangar.VehicleParameters;
	import net.wg.gui.lobby.vehiclePreview.VehiclePreviewPage;
	import omnilab.wotclassic.controls.test.LegacyVehicleParams;
	
	import net.wg.data.Aliases;
	import net.wg.data.constants.IconsTypes;
	import net.wg.data.constants.generated.LAYER_NAMES;
	import net.wg.gui.components.controls.SoundButtonEx;
	
	import net.wg.gui.lobby.hangar.Hangar;
	import net.wg.gui.lobby.hangar.ResearchPanel;
	import net.wg.gui.lobby.hangar.HangarHeader;
	import net.wg.gui.lobby.hangar.CrewPanelInject;
	import net.wg.gui.lobby.modulesPanel.FittingSelectPopover;
	import net.wg.gui.lobby.hangar.ammunitionPanel.AmmunitionPanel;
	import net.wg.gui.lobby.hangar.ammunitionPanelInject.AmmunitionPanelInject;
	import net.wg.gui.lobby.storage.StorageView;
	import net.wg.gui.tutorial.components.TutorialClip;
	import net.wg.gui.components.containers.MainViewContainer;
	import net.wg.gui.components.controls.IconTextButton;
	import net.wg.gui.components.controls.IconText;
	
	import net.wg.infrastructure.base.AbstractView;
	import net.wg.infrastructure.managers.impl.ContainerManagerBase;
	import net.wg.infrastructure.interfaces.IManagedContent;
	import net.wg.infrastructure.interfaces.IView;
	import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
	import net.wg.infrastructure.events.LoaderEvent;
	
	import scaleform.clik.constants.InvalidationType;
	
	import omnilab.wotclassic.controls.LegacyResearchPanel;
	import omnilab.wotclassic.legacyAmmoPanel.LegacyAmmoPanel;
	
	public class LegacyHangar extends AbstractView
	{
		public var legacyAmmoPanel: LegacyAmmoPanel;
		public var legacyResearchPanel: LegacyResearchPanel;
		public var legacyVehicleParams: LegacyVehicleParams;
		public var reloadViewBtn: SoundButtonEx;
		
		public var reloadView: Function;
		public var showResearch: Function;
		public var onAppResized: Function;
		
		private var _hangarView: Hangar;
		private var _vehiclePreview: VehiclePreviewPage;
		private var _ammoPanel: AmmunitionPanel;
		private var _vehParams: VehicleParameters;
		private var _fittingSelectPopover: FittingSelectPopover;
		
		public function LegacyHangar()
		{
			super();
			
		}
		
		public function appResized(e: Event): void {
			var app_width: Number = Number(App.appWidth)
			var app_height: Number = Number(App.appHeight)
			
			this.onAppResized(app_width, app_height);
			this.legacyResearchPanel.x = app_width - 67;
			this.legacyVehicleParams.x = app_width - 341;
		}
		
		private function reloadViewS(e: MouseEvent): void {
			this.reloadView();
		}
		
		private function showResearchS(e: MouseEvent): void {
			this.showResearch();
		}
		
		// OVERRIDE FUNCTIONS
		
		override protected function configUI():void {
			super.configUI();
			
			
			try{
				var viewContainer:MainViewContainer = _getContainer(LAYER_NAMES.SUBVIEW) as MainViewContainer;
				if (viewContainer != null)
				{
					var num:int = viewContainer.numChildren;
					for (var idx:int = 0; idx < num; ++idx)
					{
						var view:IView = viewContainer.getChildAt(idx) as IView;
						if (view != null)
						{
							processView(view);
						}
					}
					var topmostView:IManagedContent = viewContainer.getTopmostView();
					if (topmostView != null)
					{
						viewContainer.setFocusedView(topmostView);
					}
				}

			(App.containerMgr as ContainerManagerBase).loader.addEventListener(LoaderEvent.VIEW_LOADED, this.onViewLoaded, false, 0, true);
			} catch(e: Error) {
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
		}
		
		override protected function onPopulate() : void {
			super.onPopulate();
			
			registerFlashComponentS(this.legacyAmmoPanel, "LegacyAmmoPanelUI");
			registerFlashComponentS(this.legacyResearchPanel, "LegacyResearchPanelUI");
			registerFlashComponentS(this.legacyVehicleParams, "LegacyVehicleParamsUI");
			
			this.legacyResearchPanel.x = Number(App.appWidth) - 67;
			this.legacyVehicleParams.x = Number(App.appWidth) - 341;
			this.reloadViewBtn.addEventListener(MouseEvent.CLICK, this.reloadViewS)
			this.legacyResearchPanel.researchBtn.addEventListener(MouseEvent.CLICK, this.showResearchS)
			App.stage.addEventListener(Event.RESIZE, this.appResized);
		}
		
		override protected function onDispose():void {
			this.reloadViewBtn.removeEventListener(MouseEvent.CLICK, this.reloadViewS)
			this.legacyResearchPanel.researchBtn.removeEventListener(MouseEvent.CLICK, this.showResearchS)
			App.stage.removeEventListener(Event.RESIZE, this.appResized);
			
			super.onDispose();
		}
		
		private function _getContainer(containerName:String) : ISimpleManagedContainer
		{
			return App.containerMgr.getContainer(LAYER_NAMES.LAYER_ORDER.indexOf(containerName))
		}

		private function onViewLoaded(event:LoaderEvent) : void 
		{
			var view:IView = event.view as IView;
			processView(view);
		}

		private function processView(view:IView) : void 
		{
			var alias:String = view.as_config.alias;
			
			if (alias == Aliases.LOBBY_HANGAR)
			{
				_hangarView = view as Hangar;
				_ammoPanel = _hangarView.ammunitionPanel as AmmunitionPanel;
				
				_hangarView.removeChild(_hangarView.bottomBg);
				_hangarView.removeChild(_hangarView.vehResearchBG);
				_hangarView.removeChild(_hangarView.vehResearchPanel);
				_hangarView.removeChild(_hangarView.vehicleParametersContainer);
				
				_hangarView.addChild(this.legacyResearchPanel);
				_hangarView.addChild(this.legacyVehicleParams);
				_ammoPanel.addChild(this.legacyAmmoPanel);
				
			} else if (alias == "vehiclePreviewPage") {
				_vehiclePreview = view as VehiclePreviewPage;
				
				_vehiclePreview.fadingPanels.removeChild(_vehiclePreview.fadingPanels.vehParams);
				
				_vehiclePreview.fadingPanels.addChild(this.legacyVehicleParams);
			}
		}
	}
}