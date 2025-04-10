package omnilab.wotclassic.legacyAmmoPanel 
{
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.events.MouseEvent;
	
	import scaleform.clik.events.ButtonEvent;
	import scaleform.gfx.MouseEventEx;
	
	import net.wg.data.Aliases;
	import net.wg.data.constants.generated.LAYER_NAMES;
	
	import net.wg.gui.components.advanced.ShellButton;
	import net.wg.gui.lobby.hangar.Hangar;
	import net.wg.gui.lobby.hangar.ResearchPanel;
	import net.wg.gui.lobby.components.data.DeviceSlotVO;
	import net.wg.gui.lobby.modulesPanel.components.ModuleSlot;
	import net.wg.gui.lobby.hangar.ammunitionPanel.EquipmentSlot;
	import net.wg.gui.lobby.hangar.ammunitionPanel.AmmunitionPanel;
	import net.wg.gui.components.containers.MainViewContainer;
	
	import net.wg.infrastructure.base.BaseDAAPIComponent;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	import net.wg.infrastructure.managers.impl.ContainerManagerBase;
	import net.wg.infrastructure.interfaces.IManagedContent;
	import net.wg.infrastructure.interfaces.IView;
	import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
	import net.wg.infrastructure.events.LoaderEvent;
	
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyModulePopoverVO;
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyModuleVO;
	import omnilab.wotclassic.legacyAmmoPanel.data.LegacyOptDeviceVO;
	import omnilab.wotclassic.legacyAmmoPanel.components.OptDeviceSlot;
	import omnilab.wotclassic.legacyAmmoPanel.components.BattleAbilitySlot;
	
	public class LegacyAmmoPanel extends BaseDAAPIComponent
	{
		private const SLOT_GROUPS_SPACING = 17;
		private const SLOT_SPACING = 3;
		private const SLOT_WIDTH = 47;
		private const PANEL_WIDTH = 807;
		private const PANEL_DEF_X = -268;
		
		public var gun: ModuleSlot = new ModuleSlot();
		public var turret: ModuleSlot = new ModuleSlot();
		public var chassis: ModuleSlot = new ModuleSlot();
		public var engine: ModuleSlot = new ModuleSlot();
		public var radio: ModuleSlot = new ModuleSlot();
		
		public var optDev1: OptDeviceSlot = new OptDeviceSlot();
		public var optDev2: OptDeviceSlot = new OptDeviceSlot();
		public var optDev3: OptDeviceSlot = new OptDeviceSlot();
		
		public var shell1: ShellButton = new ShellButton();
		public var shell2: ShellButton = new ShellButton();
		public var shell3: ShellButton = new ShellButton();
		
		public var shellBg1: MovieClip;
		public var shellBg2: MovieClip;
		public var shellBg3: MovieClip;
		
		public var equipment1: EquipmentSlot = new EquipmentSlot();
		public var equipment2: EquipmentSlot = new EquipmentSlot();
		public var equipment3: EquipmentSlot = new EquipmentSlot();
		
		public var reserve1: BattleAbilitySlot = new BattleAbilitySlot();
		public var reserve2: BattleAbilitySlot = new BattleAbilitySlot();
		public var reserve3: BattleAbilitySlot = new BattleAbilitySlot();
		
		public var booster: EquipmentSlot = new EquipmentSlot();
		
		public var modificator: BattleAbilitySlot = new BattleAbilitySlot();
		
		public var showModuleInfo: Function;
		public var showBoosterInfo: Function;
		public var onCloseBtnClicked: Function;
		public var callTechnicalMaintenance: Function;
		
		private var _modulesSlots: Vector.<ModuleSlot> = new Vector.<ModuleSlot>();
		private var _optDevicesSlots: Vector.<OptDeviceSlot> = new Vector.<OptDeviceSlot>();
		private var _shellsSlots: Vector.<ShellButton> = new Vector.<ShellButton>();
		private var _shellBgs: Vector.<MovieClip> = new Vector.<MovieClip>();
		private var _equipSlots: Vector.<EquipmentSlot> = new Vector.<EquipmentSlot>();
		private var _battleAbilitySlots: Vector.<BattleAbilitySlot> = new Vector.<BattleAbilitySlot>();
		
		private var _slotIndex: int = 0;
		private var _moduleData: DeviceSlotVO;
		private var _optDeviceData: DeviceSlotVO;
		private var _equipData: DeviceSlotVO;
		private var _boosterData: DeviceSlotVO;
		private var _battleAbilityData: DeviceSlotVO = null;
		private var _modificatorData: DeviceSlotVO = null;
		
		private var _import1: LegacyModuleVO;
		private var _import2: LegacyOptDeviceVO;
		
		public function LegacyAmmoPanel() 
		{
			super();
		}
		
		override protected function initialize(): void {
			super.initialize();
			
			_modulesSlots.push(this.gun, this.turret, this.chassis, this.engine, this.radio)
			_optDevicesSlots.push(this.optDev1, this.optDev2, this.optDev3);
			_shellsSlots.push(this.shell1, this.shell2, this.shell3);
			_shellBgs.push(this.shellBg1, this.shellBg2, this.shellBg3);
			_equipSlots.push(this.equipment1, this.equipment2, this.equipment3);
			_battleAbilitySlots.push(this.reserve1, this.reserve2, this.reserve3);
			subscribeSlots();
		}
		
		override protected function configUI():void {
			super.configUI();
		}
		
		public function setupSlots(param0: Object):void{
			for each (var module in _modulesSlots){
				module.enabled = true;
				_moduleData = new DeviceSlotVO(param0["modules"][module.slotIndex]);
				if (_moduleData.slotLocked) {
					module.enabled = false;
				}
				module.update(_moduleData);
				}
				
			for each (var optDevice in _optDevicesSlots){
				optDevice.enabled = true;
				_optDeviceData = new DeviceSlotVO(param0["optionalDevice"][optDevice.slotIndex]);
				if (_optDeviceData.slotLocked){
					optDevice.enabled = false;
					}
				optDevice.update(_optDeviceData);
				}
				
			for each (var shell in _shellsSlots){
				shell.enabled = true;
				if (param0["shells"][shell.slotIndex]["slotLocked"]){
					shell.enabled = false;
					}
				if (param0["shells"][shell.slotIndex]["id"] == -999){
					shell.clear();
					continue;
				}
				shell.id = param0["shells"][shell.slotIndex]["id"];
				shell.type = param0["shells"][shell.slotIndex]["type"];
				shell.label = param0["shells"][shell.slotIndex]["label"];
				shell.icon = param0["shells"][shell.slotIndex]["icon"];
				shell.count = param0["shells"][shell.slotIndex]["count"];
				shell.tooltip = param0["shells"][shell.slotIndex]["tooltip"];
				shell.tooltipType = param0["shells"][shell.slotIndex]["tooltipType"];
				}
				
			for each (var equip in _equipSlots){
				equip.enabled = true;
				_equipData = new DeviceSlotVO(param0["equipment"][equip.slotIndex]);
				if (_equipData.slotLocked){
					equip.enabled = false;
					}
				equip.update(_equipData);
				}
			
			booster.enabled = true;
			_boosterData = new DeviceSlotVO(param0["booster"]);
			if (_boosterData.slotLocked){
				booster.enabled = false;
				}
			booster.update(_boosterData);
			
			modificator.enabled = false;
			_modificatorData = new DeviceSlotVO(param0["modificator"]);
			modificator.update(_modificatorData);
			
			for each (var battleAbility in _battleAbilitySlots){
				battleAbility.enabled = true;
				_battleAbilityData = new DeviceSlotVO(param0["battleAbilities"][battleAbility.slotIndex]);
				if (_battleAbilityData.slotLocked) {
					battleAbility.enabled = false;
				}
				battleAbility.update(_battleAbilityData);
			}
		}
		
		public function onCloseBtnClickedS(param0: ButtonEvent): void {
			this.onCloseBtnClicked();
		}
		
		public function callTechnicalMaintenanceS(param1:ButtonEvent):void {
            if (param1.buttonIdx == MouseEventEx.RIGHT_BUTTON)
            {
				try {
					showModuleInfo(param1.target.slotData.id);
				} catch (e: Error) {
					showModuleInfo(param1.target.id);
				}
			} else if (param1.buttonIdx == MouseEventEx.LEFT_BUTTON) {
				callTechnicalMaintenance();
			}
		}
		
		public function as_setModificationVisible(isVisible: Boolean){
			modificator.visible = isVisible
			
			if (isVisible){
				var _loc1_: int = SLOT_GROUPS_SPACING + SLOT_WIDTH
				this.x = -268 - (_loc1_/2);
			} else {
				this.x = -268
			}
		}
		
		public function as_setBattleAbilitiesVisible(isVisible: Boolean){
			for each (var battleAbility in _battleAbilitySlots){
				battleAbility.visible = isVisible;
			}
			if (isVisible){
				var _loc1_: int = SLOT_GROUPS_SPACING + (SLOT_WIDTH*3) + (SLOT_SPACING*2)
				this.x = -268 - (_loc1_/2);
			} else {
				this.x = -268
			}
		}
		
		private function subscribeSlots(): void {
				
			for each (var moduleSlot in _modulesSlots) {
				moduleSlot.addEventListener(ButtonEvent.CLICK, this.onClickHandler);
			}
			
			for each (var optDeviceSlot in _optDevicesSlots) {
				optDeviceSlot.addEventListener(ButtonEvent.CLICK, this.onClickHandler);
			}
				
			_slotIndex = 0;
			
			for each (var shellSlot in _shellsSlots) {
				shellSlot.slotIndex = _slotIndex
				shellSlot.addEventListener(ButtonEvent.CLICK, this.callTechnicalMaintenanceS);
				shellSlot.addEventListener(MouseEvent.ROLL_OVER,this.handleMouseRollOverS);
				shellSlot.addEventListener(MouseEvent.ROLL_OUT,this.handleMouseRollOutS);
				shellSlot.addEventListener(MouseEvent.MOUSE_DOWN,this.handleMouseDownS);
				shellSlot.addEventListener(MouseEvent.MOUSE_UP,this.handleMouseReleaseS);
				_slotIndex += 1
				}
				
			for each (var equipSlot in _equipSlots) {
				equipSlot.addEventListener(ButtonEvent.CLICK, this.callTechnicalMaintenanceS);
			}
			
			booster.addEventListener(ButtonEvent.CLICK, this.onClickHandler);
			
			for each (var battleAbility in _battleAbilitySlots) {
				battleAbility.addEventListener(ButtonEvent.CLICK, this.onClickHandler);
			}
		}
		
		override protected function onDispose():void {
				
			for each (var moduleSlot in _modulesSlots) {
				moduleSlot.removeEventListener(ButtonEvent.CLICK, this.onClickHandler);
			}
			
			for each (var optDeviceSlot in _optDevicesSlots) {
				optDeviceSlot.removeEventListener(ButtonEvent.CLICK, this.onClickHandler);
			}
				
			_slotIndex = 0;
			
			for each (var shellSlot in _shellsSlots) {
				shellSlot.removeEventListener(ButtonEvent.CLICK, this.callTechnicalMaintenanceS);
				shellSlot.removeEventListener(MouseEvent.ROLL_OVER,this.handleMouseRollOverS);
				shellSlot.removeEventListener(MouseEvent.ROLL_OUT,this.handleMouseRollOutS);
				shellSlot.removeEventListener(MouseEvent.MOUSE_DOWN,this.handleMouseDownS);
				shellSlot.removeEventListener(MouseEvent.MOUSE_UP,this.handleMouseReleaseS);
				}
				
			for each (var equipSlot in _equipSlots) {
				equipSlot.removeEventListener(ButtonEvent.CLICK, this.callTechnicalMaintenanceS);
			}
			
			booster.addEventListener(ButtonEvent.CLICK, this.onClickHandler);
			
			for each (var battleAbility in _battleAbilitySlots) {
				battleAbility.removeEventListener(ButtonEvent.CLICK, this.onClickHandler);
			}
			
			super.onDispose();
		}
		
		private function onClickHandler(param1:ButtonEvent):void {
            if (param1.buttonIdx == MouseEventEx.RIGHT_BUTTON)
            {
				if (param1.target.slotData.slotType != "battleBooster") {
					showModuleInfo(param1.target.slotData.id);
				}
            } else if (param1.buttonIdx == MouseEventEx.LEFT_BUTTON) {
				var data: LegacyModulePopoverVO = new LegacyModulePopoverVO({
					"preferredLayout": 2,
					"slotIndex": param1.target.slotIndex,
					"slotType": param1.target.slotData.slotType
				})
				App.popoverMgr.show(IPopOverCaller(param1.target), "fittingSelectPopover", data);
			}
		}
		
		private function handleMouseDownS(param1: MouseEvent): void {
			this._shellBgs[param1.target.slotIndex].gotoAndPlay("down");
		}
		
		private function handleMouseReleaseS(param1: MouseEvent): void {
			this._shellBgs[param1.target.slotIndex].gotoAndPlay("release");
		}
		
		private function handleMouseRollOverS(param1: MouseEvent): void {
			this._shellBgs[param1.target.slotIndex].gotoAndPlay("over");
		}
		
		private function handleMouseRollOutS(param1: MouseEvent): void {
			this._shellBgs[param1.target.slotIndex].gotoAndPlay("out");
		}
		
	}

}