package omnilab.wotclassic.battle 
{
	import flash.display3D.textures.Texture;
	import net.wg.infrastructure.base.BaseDAAPIComponent;
	import flash.text.TextField;
	
	public class LegacyFragCorrelationBar extends BaseDAAPIComponent 
	{
		private const TEXT_DRAW_COLOR: uint = 11168256;
		private const TEXT_LOOSE_COLOR: uint = 16058368;
		private const TEXT_WIN_COLOR: uint = 8121399;
		
		public var alliesFragsTF: TextField;
		public var enemiesFragsTF: TextField;
		public var indicator: TextField;
		
		public function LegacyFragCorrelationBar() 
		{
			super();
		}
		
		public function updateFrags(allies: int, enemies: int): void {
			this.alliesFragsTF.text = String(allies);
			this.enemiesFragsTF.text = String(enemies);
			this.indicator.text = allies != enemies ? (allies <= enemies ? "<" : ">") : ":";
			this.indicator.textColor = allies != enemies ? (allies <= enemies ? TEXT_LOOSE_COLOR : TEXT_WIN_COLOR) : TEXT_DRAW_COLOR;
		}
	}
}