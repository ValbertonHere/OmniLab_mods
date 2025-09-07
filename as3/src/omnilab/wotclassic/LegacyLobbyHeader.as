package omnilab.wotclassic
{
	import flash.text.*;
	import flash.display.*;
	import flash.events.Event;
	
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.utils.Constraints;
	
	import net.wg.data.Aliases;
    import net.wg.data.constants.IconsTypes;
	import net.wg.data.constants.generated.LAYER_NAMES;
	
	import net.wg.infrastructure.base.AbstractView;
	import net.wg.infrastructure.events.LoaderEvent;
	import net.wg.infrastructure.interfaces.IView;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	import net.wg.infrastructure.interfaces.IManagedContent;
	import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
	import net.wg.infrastructure.managers.impl.ContainerManagerBase;
	
	import net.wg.gui.components.advanced.ClanEmblem;
	import net.wg.gui.components.containers.MainViewContainer;
	import net.wg.gui.components.controls.IconText;
	import net.wg.gui.components.controls.IconTextButton;
	import net.wg.gui.components.controls.SoundButtonEx;
	
	import net.wg.gui.lobby.LobbyPage;
	import net.wg.gui.lobby.header.LobbyHeader;
	
	import net.wg.gui.tutorial.components.TutorialClip;
	
	import omnilab.wotclassic.controls.LegacyTasksButton;
	import omnilab.wotclassic.controls.LegacyTutorialButton;
	import omnilab.wotclassic.controls.LegacyBattleTypeSelectorButton;
	import omnilab.wotclassic.controls.PersonalReservesComponent;
	import omnilab.wotclassic.controls.LegacyFightButton;
	
	import net.wg.gui.lobby.header.vo.HBC_PersonalReservesVO;
	
	public class LegacyLobbyHeader extends AbstractView implements IPopOverCaller {

		public var crystalButt: IconTextButton;
		public var goldButt: IconTextButton;
		public var creditsButt: IconTextButton;
		public var freeXPButt: IconTextButton;
		public var menuButt: IconTextButton;
		public var inDevRestart: SoundButtonEx;
		public var userNickButt: SoundButtonEx;
		public var battSelectPopCaller: SoundButtonEx;
		public var clanButt: SoundButtonEx;
		
		public var lobbyHeaderView: LobbyHeader;
		
		public var tutorialButt: LegacyTutorialButton;
		public var tasksButt: LegacyTasksButton;
		public var battleSelector: LegacyBattleTypeSelectorButton;
		public var personalReservesComp: PersonalReservesComponent;
		public var fightBtn: LegacyFightButton;
		
		public var crystalMoney: IconText;
		public var goldMoney: IconText;
		public var creditsMoney: IconText;
		public var freeXPMoney: IconText;
		
		public var eliteStatus: Sprite;
		public var legacyResizeBg: Sprite;
		public var legacyCenterBg: MovieClip;
		public var legacyOnlineCounter: MovieClip;
		
		public var clanEmblem: ClanEmblem;
		
		public var userNickname: TextField;
		public var accountType: TextField;
		public var serverName: TextField;
		public var tankName: TextField;
		public var tankType: TextField;
		public var inDev: TextField;
		
		public var onClose: Function;
		public var onMenuClick: Function;
		public var onCrystalClick: Function;
		public var onGoldClick: Function;
		public var onCreditsClick: Function;
		public var onFreeXPClick: Function;
		public var onTasksClick: Function;
		public var onNickClick: Function;
		public var onAppResized: Function;
		public var onClanClicked: Function;
		public var onTutorialClick: Function;
		public var onResearchClick: Function;
		public var onInDevRestartClick: Function;
		public var fightClick: Function;

		public function LegacyLobbyHeader() {
			super();
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			registerFlashComponentS(this.personalReservesComp, "PersonalReservesComponentUI");
				
			this.menuButt.addEventListener(ButtonEvent.CLICK, this.onMenuClick);
			this.crystalButt.addEventListener(ButtonEvent.CLICK, this.onCrystalClick);
			this.goldButt.addEventListener(ButtonEvent.CLICK, this.onGoldClick);
			this.creditsButt.addEventListener(ButtonEvent.CLICK, this.onCreditsClick);
			this.freeXPButt.addEventListener(ButtonEvent.CLICK, this.onFreeXPClick);
			this.tutorialButt.addEventListener(ButtonEvent.CLICK, this.onTutorialClick);
			this.userNickButt.addEventListener(ButtonEvent.CLICK, this.onNickClick);
			this.tasksButt.addEventListener(ButtonEvent.CLICK, this.onTasksClickS);
			this.battleSelector.addEventListener(ButtonEvent.CLICK, this.onBattleSelectorClick);
			this.clanButt.addEventListener(ButtonEvent.CLICK, this.onClanClicked);
			this.inDevRestart.addEventListener(ButtonEvent.CLICK, this.onInDevRestartClick);
			this.fightBtn.addEventListener(ButtonEvent.CLICK,this.onFightBtnClick);
			App.stage.addEventListener(Event.RESIZE, this.guiReplace);
			
			guiReplace()
		}
		
		override protected function configUI():void {
			super.configUI();
			
			this.userNickButt.width = userNickname.textWidth
			this.userNickButt.alpha = 0;
			
			this.clanButt.width = 32;
			this.clanButt.height = 32;
			this.clanButt.alpha = 0;
			
			this.battSelectPopCaller.width = 149
			this.battSelectPopCaller.alpha = 0
			
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
			} catch (e: Error) {
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
		}
		
		private function guiReplace(param1:Event = null): void {
			var app_width: Number = Number(App.appWidth)
			var app_height: Number = Number(App.appHeight)
			
			this.legacyResizeBg.width = app_width;
			this.legacyCenterBg.x = app_width / 2 - 512;
			this.userNickname.x = (app_width / 2) + 155;
			this.userNickButt.x = (app_width / 2) + 155;
			this.accountType.x = (app_width / 2) + 155;
			this.clanEmblem.x = (app_width / 2) + 124;
			this.clanButt.x = (app_width / 2) + 124;
			this.fightBtn.x = (app_width / 2) - 128;
			this.battleSelector.x = (app_width / 2) - 6;
			this.battSelectPopCaller.x = (app_width / 2) - 80;
			this.tankName.x = (app_width / 2) - 419;
			this.tankType.x = (app_width / 2) - 293;
			this.eliteStatus.x = (app_width / 2) - 215;
			this.serverName.x = (app_width / 2) - 91;
			this.crystalButt.x = app_width - 203;
			this.crystalMoney.x = app_width - 423;
			this.goldButt.x = app_width - 203;
			this.goldMoney.x = app_width - 423;
			this.creditsButt.x = app_width - 203
			this.creditsMoney.x = app_width - 423;
			this.freeXPButt.x = app_width - 203;
			this.freeXPMoney.x = app_width - 423;
		}
		
		override protected function onDispose():void {
			this.menuButt.removeEventListener(ButtonEvent.CLICK, this.onMenuClick);
			this.crystalButt.removeEventListener(ButtonEvent.CLICK, this.onCrystalClick);
			this.goldButt.removeEventListener(ButtonEvent.CLICK, this.onGoldClick);
			this.creditsButt.removeEventListener(ButtonEvent.CLICK, this.onCreditsClick);
			this.freeXPButt.removeEventListener(ButtonEvent.CLICK, this.onFreeXPClick);
			this.tutorialButt.removeEventListener(ButtonEvent.CLICK, this.onTutorialClick);
			this.userNickButt.removeEventListener(ButtonEvent.CLICK, this.onNickClick);
			this.tasksButt.removeEventListener(ButtonEvent.CLICK, this.onTasksClickS);
			this.battleSelector.removeEventListener(ButtonEvent.CLICK, this.onBattleSelectorClick);
			this.clanButt.removeEventListener(ButtonEvent.CLICK, this.onClanClicked);
			this.inDevRestart.removeEventListener(ButtonEvent.CLICK, this.onInDevRestartClick);
			this.fightBtn.removeEventListener(ButtonEvent.CLICK, this.onFightBtnClick);
			App.stage.removeEventListener(Event.RESIZE, this.guiReplace);
			
			super.onDispose();
		}
		
		public function as_setOnline(usersStr: String):void {
			this.legacyOnlineCounter.textField.text = usersStr
		}
		
		public function as_setFightButtonLabel(label: String): void {
			this.fightBtn.label = label;
		}
		
		public function as_setFightButtonDisabled(isDisabled: Boolean): void {
			this.fightBtn.enabled = !isDisabled;
		}
		
		public function as_disableHeaderButtons(isDisabled: Boolean):void {
			this.battleSelector.as_disable(isDisabled);
			this.tasksButt.as_disable(isDisabled);
			this.tutorialButt.as_disable(isDisabled);
			this.userNickButt.enabled = !isDisabled;
			this.clanButt.enabled = !isDisabled;
			this.crystalButt.enabled = !isDisabled;
			this.goldButt.enabled = !isDisabled;
			this.creditsButt.enabled = !isDisabled;
			this.freeXPButt.enabled = !isDisabled;
			
		}
		
		public function as_setInDev(isInDev: Boolean):void {
			this.inDev.visible = isInDev;
			this.inDevRestart.visible = isInDev;
		}
		
		public function as_setClanEmblem(emblem: String):void {
			this.clanEmblem.setImage(emblem);
		}
		
		public function as_setServerName(htmlStr: String):void {
			this.serverName.htmlText = htmlStr;
		}
		
		public function as_setAccountType(htmlStr: String):void {
			this.accountType.htmlText = htmlStr
		}
		
		public function as_setUserNickname(name: String, isTeamKiller: Boolean):void {
			this.userNickname.text = name;
			this.userNickButt.width = userNickname.textWidth;
			if (isTeamKiller) {
				this.userNickname.textColor = 647935;
				return;
			}
			
			this.userNickname.textColor = 15327935;
		}
		
		public function as_setVehInfo(vehName: String, vehType: String, vehExp: String, isElite: Boolean):void {
			this.tankName.text = vehName;
			this.tankType.text = vehType;
			this.eliteStatus.visible = isElite;
		}
		
		public function as_setCrystal(curr: String):void {
			this.crystalMoney.text = curr;
		}
		
		public function as_setGold(curr: String):void {
			this.goldMoney.text = curr;
		}
		
		public function as_setCredits(curr: String):void {
			this.creditsMoney.text = curr;
		}
		
		public function as_setFreeXP(curr: String):void {
			this.freeXPMoney.text = curr;
		}
		
		private function onTasksClickS(param1:ButtonEvent):void {
			try {
				this.onTasksClick();
			}
			catch (e:Error){
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
		}
		
		public function onBattleSelectorClick(param1:ButtonEvent):void {
			try{
				App.popoverMgr.show(this, "battleTypeSelectPopover", null, this.battleSelector);
			}
			catch (e:Error){
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
		}
		
		public function onFightBtnClick(param1:ButtonEvent):void {
			this.fightClick(0, "");
		}
		
		public function getHitArea(): DisplayObject {
		   return this.battleSelector;
		}
			  
		public function getTargetButton(): DisplayObject {
		   return this.battSelectPopCaller;
		}
		
		public function as_setBattleType(bType: String):void {
			this.battleSelector.battleType.text = bType;
			this.battleSelector.battleType.invalidate("InvPosition");
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
			
			if (alias == Aliases.LOBBY)
			{
				lobbyHeaderView = (view as LobbyPage).header as LobbyHeader;
				lobbyHeaderView.mainMenuButtonBar.y = 100
				lobbyHeaderView.removeChild(lobbyHeaderView.fightBtn);
				lobbyHeaderView.removeChild(lobbyHeaderView.resizeBg);
				lobbyHeaderView.removeChild(lobbyHeaderView.centerMenuBg);
				lobbyHeaderView.removeChild(lobbyHeaderView.mainMenuGradient);
				lobbyHeaderView.removeChild(lobbyHeaderView.centerBg);
				lobbyHeaderView.removeChild(lobbyHeaderView.onlineCounter);
				
				lobbyHeaderView.addChild(DisplayObject(this));
				lobbyHeaderView.constraints.addElement("LegacyLobbyHeaderUI", DisplayObject(this), Constraints.LEFT);
				lobbyHeaderView.swapChildren(lobbyHeaderView.mainMenuButtonBar, DisplayObject(this));
			}
		}
	}
}