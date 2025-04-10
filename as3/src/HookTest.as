package 
{
	import flash.text.*;
	import flash.display.*;
	
	import net.wg.data.Aliases;
	import net.wg.data.constants.generated.LAYER_NAMES;
	
	import net.wg.gui.components.containers.MainViewContainer;
	import net.wg.gui.lobby.techtree.TechTreePage;
	
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.infrastructure.base.AbstractView;
	import net.wg.infrastructure.managers.impl.ContainerManagerBase;
	import net.wg.infrastructure.interfaces.IManagedContent;
	import net.wg.infrastructure.interfaces.IView;
	import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
	import net.wg.infrastructure.events.LoaderEvent;
	
	public class HookTest extends AbstractWindowView
	{
		
		public var root_view: AbstractView;
		public var viewPyComp: TechTreePage;
		
		public function HookTest() 
		{
			super();
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			
			width = 1280;
			height = 720;
		}
		
		override protected function configUI():void {
			super.configUI();
			
			root_view.visible = true;
			
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
			
			try{
				root_view.removeChildren()
				
				if (alias == Aliases.TECHTREE)
				{
					viewPyComp = view as TechTreePage;
					window.title = viewPyComp.title.titleTF.text
					viewPyComp.title.visible = false;
					viewPyComp.vehicleCollectionBtn.visible = false;
					viewPyComp.background.visible = false;
					viewPyComp.footerBg.visible = false;
					viewPyComp.updateStage(window.width-20, window.height-75);
					viewPyComp.y = 25;
					
					root_view.addChild(viewPyComp);
				}
			} catch (e:Error) {
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
			
		}
	}
}