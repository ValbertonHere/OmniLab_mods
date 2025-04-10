package 
{
	import flash.text.*;
	import flash.display.*;
	import flash.utils.Timer;
	import net.wg.data.constants.generated.EQUIPMENT_ITEM_TARGET;
	import net.wg.gui.components.advanced.ButtonBarEx;
	import net.wg.gui.lobby.modulesPanel.components.DeviceSlot;
	import omnilab.wotclassic.test.TestItemRendererVO;
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyOptDeviceVO;
	import scaleform.clik.controls.ScrollingList
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.infrastructure.base.AbstractWindowView;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.events.IndexEvent;
	import scaleform.clik.controls.ScrollingList;
	import net.wg.gui.components.controls.IconText;
    import net.wg.data.constants.IconsTypes;
	import scaleform.clik.events.ButtonEvent;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	import net.wg.gui.lobby.components.data.DeviceSlotVO;
	import net.wg.gui.components.advanced.ClanEmblem;
	import net.wg.gui.lobby.modulesPanel.components.ModuleSlot;
	import net.wg.gui.components.advanced.ShellButton;
	import net.wg.gui.components.advanced.ModuleIcon;
	import net.wg.gui.lobby.hangar.ammunitionPanel.EquipmentSlot;
	import flash.events.TimerEvent;
	import scaleform.clik.interfaces.IListItemRenderer;
	import net.wg.gui.components.controls.SoundListItemRenderer;
	import net.wg.gui.components.controls.TableRenderer;
    import net.wg.gui.lobby.battleResults.data.TeamMemberItemVO;
	import net.wg.gui.lobby.modulesPanel.data.ListOverlayVO;
	
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyModulePopoverVO;
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyModuleVO;
	
	
	public class OLTestWindow extends AbstractWindowView implements IPopOverCaller
	{
		public var tabs: ButtonBarEx;
		public var onClick: Function;
		public var textField: TextField;
		public var button: SoundButtonEx;
		public var list: ScrollingList;
		public var deviceSlot: EquipmentSlot = new EquipmentSlot();
		public var optDevicesData: Vector.<DeviceSlotVO> = new Vector.<DeviceSlotVO>();
		
		private var tabDataP: DataProvider = null;
		
		public function OLTestWindow() 
		{
			super();
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			
			width = 921;
			height = 425;
		}
		
		override protected function configUI():void {
			super.configUI();
			try
			{
				var data:Array = new Array();
				data.push({"label":"Командные достижения"});
				data.push({"label":"Личные достижения"});
				data.push({"label":"Герои битвы"});
				tabs.autoSize = "center";
				tabs.dataProvider = new DataProvider(data);
				tabs.itemRendererName = "TabButtonUI";
				tabs.enableOversize = true;
				tabs.paddingHorizontal = 1;
				tabs.centerTabs = false;
				tabs.addEventListener(IndexEvent.INDEX_CHANGE, this.onTabIndexChangeHandler)
				
				textField.text = "Победа! Все вражеские танки уничтожены.";
				
				deviceSlot.addEventListener(ButtonEvent.CLICK, this.onClickHandler);
			}
			catch (e:Error)
			{
				DebugUtils.LOG_ERROR(e.getStackTrace());
			}
		}
		
		private function onTabIndexChangeHandler(param1:IndexEvent) : void {
			DebugUtils.LOG_ERROR(param1);
		}
		
		public function setSlots(param0: Object):void{
			var optDeviceData: DeviceSlotVO = new DeviceSlotVO(param0);
			optDevicesData.push(optDeviceData);
			deviceSlot.update(optDeviceData);
		}
		
		public function onClickHandler(param1:ButtonEvent):void {
			try{
				var data: LegacyModulePopoverVO = new LegacyModulePopoverVO({
					"preferredLayout": 2,
					"slotIndex": 0,
					"slotType": "optionalDevice"
				})
				App.popoverMgr.show(this, "fittingSelectPopover", data);
			}
			catch (e:Error){
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
		}
		
		public function getHitArea(): DisplayObject {
		   return this.deviceSlot;
		}
			  
		public function getTargetButton(): DisplayObject {
		   return this.deviceSlot;
		}
	}
}