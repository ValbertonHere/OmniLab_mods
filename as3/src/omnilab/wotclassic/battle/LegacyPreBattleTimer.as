package omnilab.wotclassic.battle 
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import net.wg.gui.battle.components.BattleDisplayable;
	
	import net.wg.data.Aliases;
	import net.wg.data.constants.generated.LAYER_NAMES;
	
	import net.wg.gui.components.containers.MainViewContainer;
	
	import net.wg.gui.battle.views.BaseBattlePage;
	import net.wg.gui.battle.views.prebattleTimer.PrebattleTimerBase;
	
	import net.wg.infrastructure.managers.impl.ContainerManagerBase;
	import net.wg.infrastructure.interfaces.IManagedContent;
	import net.wg.infrastructure.interfaces.IView;
	import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
	import net.wg.infrastructure.events.LoaderEvent;
	
	import net.wg.infrastructure.base.meta.IPrebattleTimerBaseMeta;
	import net.wg.gui.battle.interfaces.IPrebattleTimerBase;
	import net.wg.infrastructure.base.meta.impl.PrebattleTimerBaseMeta;
	
	public class LegacyPreBattleTimer extends PrebattleTimerBaseMeta implements IPrebattleTimerBase, IPrebattleTimerBaseMeta
	{
		public var background: MovieClip;
		public var timer: MovieClip;
		
		public function LegacyPreBattleTimer() 
		{
			super();
		}
		
		public function hideBackground () : void {
			return
		}

		public function updateStage (param0:Number, param1:Number) : void {
			return
		}

		public function as_setTimer(totalTime: int):void {
			gotoAndStop("normal");
			if (totalTime < 60) {
				this.timer.secondsTF.text = doubleDigitFormat(totalTime);
			} else {
				this.timer.secondsTF.text = doubleDigitFormat(totalTime % 60);
				this.timer.minutesTF.text = doubleDigitFormat(Math.floor((totalTime % 3600 ) / 60));
			}
		}
		
		public function as_setMessage(message:String):void {
			this.background.message.text = message;
		}
		
		public function as_setWinText(message:String):void {
			this.background.winText.text = message;
		}
		
		public function as_setWinConditionText(winText:String):void {
			return
		}
		
		public function as_setTimerPeriod(isWaiting: Boolean) {
			this.timer.visible = !isWaiting
		}
		
		public function as_hideAll(isFade: Boolean):void {
			if (isFade) {
				gotoAndPlay("hide");
			} else {
				gotoAndStop("hidden");
			}
		}
		
		private function doubleDigitFormat(number:uint):String
		{
			if (number < 10) 
			{
				return ("0" + number);
			}
			return String(number);
		}
		
	}

}