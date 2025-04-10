package omnilab.wotclassic.legacyAmmoPanel.data
{
	import net.wg.gui.lobby.modulesPanel.data.ModuleVO;
	import net.wg.gui.lobby.modulesPanel.data.ParamsItemVO;
	import net.wg.gui.components.controls.VO.ItemPriceVO;
	
   public class LegacyModuleVO extends ModuleVO
   {
      
      private static const PARAMS_ITEMS:String = "paramsItems";
       
      public function LegacyModuleVO(param1:Object)
      {
         super(param1);
      }
      
      override protected function onDataWrite(param1:String, param2:Object) : Boolean
      {
		  try{
			 var _loc3_:Array = null;
			 var _loc4_:Object = null;
			
			 if(param1 == "itemPrices")
			 {
				_loc3_ = param2 as Array;
				this.itemPrices = new Vector.<ItemPriceVO>(0);
				for each(_loc4_ in _loc3_)
				{
				   this.itemPrices.push(new ItemPriceVO(_loc4_));
				}
				return false;
			 }
			
			 if(param1 == PARAMS_ITEMS)
			 {
				_loc3_ = param2 as Array;
				this.paramsItems = new Vector.<ParamsItemVO>(0);
				for each(_loc4_ in _loc3_)
				{
				   this.paramsItems.push(new ParamsItemVO(_loc4_));
				}
				return false;
		  }
         } catch(e:Error) {
			 DebugUtils.LOG_ERROR(e.getStackTrace())
		 }
         return true;
      }
      
      override protected function onDispose() : void
      {
         var _loc1_:ParamsItemVO = null;
         if(this.paramsItems != null)
         {
            for each(_loc1_ in this.paramsItems)
            {
               _loc1_.dispose();
            }
            this.paramsItems = null;
         }
         super.onDispose();
      }
   }
}