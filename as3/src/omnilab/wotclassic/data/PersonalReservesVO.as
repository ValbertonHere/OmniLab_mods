package omnilab.wotclassic.data 
{
	import net.wg.data.daapi.base.DAAPIDataClass;
	
	public class PersonalReservesVO extends DAAPIDataClass
	{
		public var personalCount: int;
		public var personalStorageCount: int;
		public var clanCount: int;
		public var usageTime: int;
		
		public function PersonalReservesVO(param1: Object) 
		{
			super(param1);
		}
		
        public function get hasActiveReserves() : Boolean
        {
            return this.personalCount != 0 || this.clanCount != 0;
        }
	}
}