package omnilab.wotclassic.maintenance.gui.lobby.components.maintenance.data
{
    import net.wg.data.constants.generated.CURRENCIES_CONSTANTS;
    import net.wg.data.constants.generated.EQUIPMENT_ITEM_TARGET;
    import net.wg.data.daapi.base.DAAPIDataClass;
    import net.wg.gui.components.controls.VO.ActionPriceVO;
	import net.wg.gui.components.controls.VO.ItemPriceVO;
    
    public class ModuleVO extends DAAPIDataClass
    {
        
        private static const ACTION_PRICE_DATA:String = "actionPriceData";
         
        
        public var id:String = "";
        
        public var name:String = "";
        
        public var desc:String = "";
        
        public var target:int;
        
        public var compactDescr:int;
        
        public var prices:Array = null;
        
        public var currency:String = "";
        
        public var icon:String = "";
        
        public var index:int;
        
        public var slotIndex:int = 0;
		
		public var itemPrices:Vector.<ItemPriceVO>;
		
		public var nullItemPrices:Vector.<ItemPriceVO>;
        
        public var inventoryCount:int;
        
        public var vehicleCount:int;
        
        public var count:int;
        
        public var fits:Array = null;
        
        public var goldEqsForCredits:Boolean;
        
        public var userCredits:Object = null;
        
        public var actionPriceData:Object = null;
        
        public var actionPriceVo:ActionPriceVO = null;
        
        public var moduleLabel:String = "empty";
        
        public var highlightType:String = "";
        
        public var builtIn:Boolean = false;
        
        public var disabledOption:Boolean = false;
        
        public var disabled:Boolean = false;
		
		public var inSetup:Boolean = false;
		
		public var isActionPrice:Boolean = false;
        
        public function ModuleVO(param1:Object = null)
        {
            super(param1);
        }
        
        override protected function onDispose() : void
        {
            if(this.actionPriceVo != null)
            {
                this.actionPriceVo.dispose();
                this.actionPriceVo = null;
            }
            this.userCredits = App.utils.data.cleanupDynamicObject(this.userCredits);
            this.actionPriceData = App.utils.data.cleanupDynamicObject(this.actionPriceData);
            this.prices.splice(0);
            this.fits.splice(0);
            super.onDispose();
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
				
				else if(param1 == "nullItemPrices")
				{
					_loc3_ = param2 as Array;
					this.nullItemPrices = new Vector.<ItemPriceVO>(0);
					for each(_loc4_ in _loc3_)
					{
					   this.nullItemPrices.push(new ItemPriceVO(_loc4_));
					}
					return false;
				}
			} catch (e: Error) {
				DebugUtils.LOG_ERROR(e.getStackTrace())
			}
			return true;
        }
        
        public function get isInstalled() : Boolean
        {
            return this.target == EQUIPMENT_ITEM_TARGET.INSTALLED;
        }
        
        public function get isInInventory() : Boolean
        {
            return this.target == EQUIPMENT_ITEM_TARGET.IN_INVENTORY;
        }
        
        public function get status() : String
        {
            return this.inSetup && this.slotIndex != this.index ? MENU.MODULEFITS_WRONG_SLOT : String(this.fits[this.slotIndex]);
        }
        
        public function get price() : int
        {
            return this.prices[this.currency == CURRENCIES_CONSTANTS.CREDITS ? 0 : 1];
        }
    }
}
