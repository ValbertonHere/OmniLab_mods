package omnilab.wotclassic.battle 
{
	import flash.events.Event;
	import net.wg.gui.battle.views.BaseBattlePage;
	
	import net.wg.infrastructure.base.AbstractView;
	
	import net.wg.data.Aliases;
	import net.wg.data.constants.generated.LAYER_NAMES;
	import net.wg.data.constants.generated.BATTLE_VIEW_ALIASES;
	
	import net.wg.gui.components.containers.MainViewContainer;
	
	import net.wg.infrastructure.managers.impl.ContainerManagerBase;
	import net.wg.infrastructure.interfaces.IManagedContent;
	import net.wg.infrastructure.interfaces.IView;
	import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
	import net.wg.infrastructure.events.LoaderEvent;
	import net.wg.infrastructure.interfaces.IDAAPIModule;
	
	import omnilab.wotclassic.battle.LegacyBattleTimer;
	import omnilab.wotclassic.battle.LegacyPreBattleTimer;
	import omnilab.wotclassic.battle.LegacyFragCorrelationBar;
	import COMMON;
	
	public class LegacyBattlePage extends AbstractView
	{
		public var legacyBattleTimer: LegacyBattleTimer;
		public var legacyPreBattleTimer: LegacyPreBattleTimer;
		public var legacyFragCorrelationBar: LegacyFragCorrelationBar;
		
		public var onAppResized: Function;
		
		public var baseBattlePage: BaseBattlePage;
		
		private var _componentsStorage: Object;
		
		public function LegacyBattlePage()
		{
			this._componentsStorage = {};
			super();
		}
		
		public function appResized(e: Event = null): void {
			var app_width: Number = Number(App.appWidth)
			var app_height: Number = Number(App.appHeight)
			
			this.onAppResized(app_width, app_height);
			this.legacyBattleTimer.x = app_width - 44;
			this.legacyPreBattleTimer.x = app_width / 2;
			this.legacyFragCorrelationBar.x = app_width / 2;
		}
		
		public function as_setComponentsVisibility(component: String, isVisible): void {
			this._componentsStorage[component].visible = isVisible;
		}
		
		override protected function onPopulate() : void {
			super.onPopulate();
			
			this.registerComponent(this.legacyBattleTimer, "LegacyBattleTimerUI");
			this.registerComponent(this.legacyPreBattleTimer, "LegacyPreBattleTimerUI");
			this.registerComponent(this.legacyFragCorrelationBar, "LegacyFragCorrelationBarUI");
			
			App.stage.addEventListener(Event.RESIZE, this.appResized);
			
			this.appResized();
		}
		
		override protected function configUI():void {
			super.configUI();
			
			
			try{
				var viewContainer:MainViewContainer = _getContainer(LAYER_NAMES.VIEWS) as MainViewContainer;
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
			
			try {
				baseBattlePage = view as BaseBattlePage;
				baseBattlePage.addChild(this);
			}
			catch(e: Error) {
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
			
		}
		
		protected function registerComponent(param1:IDAAPIModule, param2:String) : void
		{
			this._componentsStorage[param2] = param1;
			registerFlashComponentS(param1, param2);
		}
		
		override public function unregisterComponent(param1:String) : void
		{
			delete this._componentsStorage[param1];
			super.unregisterComponent(param1);
		}
		
	}

}