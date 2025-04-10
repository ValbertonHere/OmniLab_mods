package omnilab.wotclassic.controls.test.data 
{
	import net.wg.data.daapi.base.DAAPIDataClass;
	
	public class LegacyVehParamVO extends DAAPIDataClass 
	{
		public var title:String = "";
		public var value:String = "";
		
		public function LegacyVehParamVO(param1:Object=null) 
		{
			super(param1);
		}
	}
}