package
{
   import net.wg.gui.components.popovers.PopOver;
   import net.wg.infrastructure.base.SmartPopOverView;
   
   public class OLPopOverTest extends SmartPopOverView
   {
      
      public function OLPopOverTest()
      {
         super();
      }
      
      override protected function configUI() : void
      {
         super.configUI();
		 visible = true;
		 width = 540;
		 height = 500;
		 setData();
      }
	  
	  override protected function onPopulate(): void 
	  {
		  super.onPopulate();
	  }
	  
	  private function setData(): void {
		  
		var popoverWrapper:PopOver = PopOver(wrapper);
		popoverWrapper.title = "Выбор оборудования";
		popoverWrapper.isCloseBtnVisible = true;
		popoverLayout.preferredLayout = 2;
		
	  }
   }
}