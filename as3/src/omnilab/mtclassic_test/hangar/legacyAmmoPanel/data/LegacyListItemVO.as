package omnilab.mtclassic_test.hangar.legacyAmmoPanel.data
{
    import net.wg.data.daapi.base.DAAPIDataClass;

    public class LegacyListItemVO extends DAAPIDataClass 
    {
        public var title: String = "";
        public var descr: String = "";
        public var moduleIcon: String = "";
        public var level: int = 0;
        public var target: String = "";
        public var targetVisible: Boolean = false;
        public var disabled: Boolean = false;
        public var isSelected: Boolean = false;
        
        public function LegacyListItemVO(param1:Object)
        {
            super(param1);
        }
    }
}