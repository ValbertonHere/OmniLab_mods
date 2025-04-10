package omnilab.wotclassic
{
	import flash.display.MovieClip;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.gui.interfaces.ISoundButtonEx;
	import net.wg.infrastructure.base.AbstractWindowView;
	
	public class BondsWindow extends AbstractWindowView 
	{
		public var closeBtn: SoundButtonEx;
		
		public function BondsWindow() 
		{
			super();
		}
		
		override protected function onPopulate():void {
			super.onPopulate();
			
			this.window.title = "#menu:crystals/promoWindow/title"
			this.window.formBgPadding.bottom = 40;
		}
		
	}

}