package 
{
	import flash.text.*;
	import flash.display.*;
	import flash.events.MouseEvent;
	import omnilab.wotclassic.test.TestDropDown;
	
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.data.managers.impl.ToolTipParams;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	import scaleform.clik.data.DataProvider;
	import net.wg.data.constants.Linkages;
	import flash.geom.Rectangle;
	import net.wg.gui.components.interfaces.ISparksManager;
	
	
	
	// --------- HOOK TEST------------
	import net.wg.data.Aliases;
	import net.wg.data.constants.generated.LAYER_NAMES;
	import net.wg.gui.components.containers.MainViewContainer;
	import net.wg.infrastructure.managers.impl.ContainerManagerBase;
	import net.wg.infrastructure.interfaces.IManagedContent;
	import net.wg.infrastructure.interfaces.IView;
	import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
	import net.wg.infrastructure.events.LoaderEvent;
	import net.wg.gui.login.impl.LoginPage;
	
	import net.wg.data.constants.generated.TOOLTIPS_CONSTANTS;
	
	
	public class TestWindow extends AbstractWindowView implements IPopOverCaller
	{
		public var button: SoundButtonEx;
		public var onClicked: Function;
		public var testDD: TestDropDown;
		public var _sparksMc:Sprite = null;
		
		private var viewPyComp: LoginPage;
		private var _sparksManager: ISparksManager = null;
		private var data: Array = [{"title": "Cum1", "desc": "Penis1"}, {"title": "Cum2", "desc": "Penis2"}, {"title": "Cum3", "desc": "Penis3"}];
		private var _isTestDDOpened: Boolean = false;
		
		public function TestWindow() 
		{
			super();
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			
			width = 921;
			height = 425;
			window.title = "Тестовое UwU"
		}
		
		override protected function configUI():void {
			super.configUI();
			this.button.addEventListener(MouseEvent.CLICK, this.onButtonClicked);
			var dataProv: DataProvider = new DataProvider(data);
			this.testDD.menuRowCount = dataProv.length;
			this.testDD.dataProvider = dataProv;
			
			
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
		
		private function createSparks() : void {
			
		}

		private function processView(view:IView) : void
		{
			var alias:String = view.as_config.alias;
			
			try{
				if (alias == Aliases.LOGIN)
				{
					viewPyComp = view as LoginPage;
					this._sparksMc = new Sprite();
					DebugUtils.LOG_ERROR(viewPyComp.numChildren);
					DebugUtils.LOG_ERROR(viewPyComp.getChildIndex(viewPyComp.shadowImage) + 1);
					viewPyComp.addChildAt(this._sparksMc, 0);
					DebugUtils.LOG_ERROR(viewPyComp.getChildAt(0).name);
					DebugUtils.LOG_ERROR(viewPyComp.numChildren);
					if(this._sparksManager == null)
					{
						this._sparksManager = ISparksManager(App.utils.classFactory.getObject(Linkages.SPARKS_MGR));
						this._sparksManager.zone = new Rectangle(100,0,stage.width + -200,stage.height + -100);
						this._sparksManager.scope = this._sparksMc;
						this._sparksManager.sparkQuantity = 150;
						this._sparksManager.createSparks();
					}
					this._sparksMc.visible = true;
					
				}
			} catch (e:Error) {
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
			
		}
		
		public function onButtonClicked(param1:MouseEvent):void {
			DebugUtils.LOG_WARNING("Clicked");
			// this.onClicked();
			// App.popoverMgr.show(this, "OmniSessionStatsPopoverUI");
		}
      
		public function getHitArea() : DisplayObject
		{
			return button;
		}
		  
		public function getTargetButton() : DisplayObject
		{
			return button;
		}
	}
}