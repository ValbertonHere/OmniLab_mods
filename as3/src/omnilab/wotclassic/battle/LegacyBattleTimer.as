package omnilab.wotclassic.battle 
{
	import net.wg.gui.battle.views.battleTimer.BattleTimer;
	
	public class LegacyBattleTimer extends BattleTimer 
	{
		
		public function LegacyBattleTimer() 
		{
			super();
		}
		
		override protected function configUI() : void {
			super.configUI();
			this.dotsTF.text = ":";
		}
		
	}

}