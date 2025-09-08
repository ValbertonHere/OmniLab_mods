package omnilab.wotclassic.battle 
{
	import flash.text.TextField;
	
	import net.wg.infrastructure.base.BaseDAAPIComponent;
	import net.wg.infrastructure.events.ColorSchemeEvent;
	
	public class LegacyFragCorrelationBar extends BaseDAAPIComponent 
	{
		// private const TEXT_DRAW_COLOR: uint = 11168256;
		// private const TEXT_LOOSE_COLOR: uint = 16058368;
		// private const TEXT_WIN_COLOR: uint = 8121399;
		
		public var alliesFragsTF: TextField;
		public var enemiesFragsTF: TextField;
		public var indicator: TextField;
		
		private var _alliesCount: int = 0;
		private var _enemiesCount: int = 0;
		
		public function LegacyFragCorrelationBar() 
		{
			super();
		}
		
		override protected function configUI() : void {
			super.configUI();
			App.colorSchemeMgr.addEventListener(ColorSchemeEvent.SCHEMAS_UPDATED, this.onColorSchemasUpdated);
		}
		
		override protected function onDispose() : void {
			App.colorSchemeMgr.removeEventListener(ColorSchemeEvent.SCHEMAS_UPDATED, this.onColorSchemasUpdated);
			super.onDispose();
		}
		
		public function updateFrags(allies: int, enemies: int): void {
			this._alliesCount = allies;
			this._enemiesCount = enemies;
			this.updateColors();
		}
		
		private function updateColors(): void {
			this.alliesFragsTF.text = String(this._alliesCount);
			this.enemiesFragsTF.text = String(this._enemiesCount);
			this.indicator.text = this._alliesCount != this._enemiesCount ? (this._alliesCount <= this._enemiesCount ? "<" : ">") : ":";
			var colorScheme = this._alliesCount != this._enemiesCount ? (this._alliesCount <= this._enemiesCount ? "FragCorrelationLoose" : "FragCorrelationWin") : "FragCorrelationDraw";
			this.indicator.textColor = App.colorSchemeMgr.getRGB(colorScheme);
		}
		
		private function onColorSchemasUpdated(event: ColorSchemeEvent): void {
			this.updateColors()
		}
		
	}
}