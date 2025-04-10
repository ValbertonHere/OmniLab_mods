package 
{
	import flash.display.*;
	import flash.text.*;
	import net.wg.gui.components.crosshairPanel.CrosshairArcade;
	import net.wg.gui.components.crosshairPanel.constants.CrosshairConsts;
	
	public class CrosshairArcadeUI extends CrosshairArcade 
	{
		public var ownCassetMC:MovieClip = null;
		public var clipCount:MovieClip = null;
		
		private const RELOADING_BAR_FRAMERATE: Array = new Array(60, 60, 60, 60, 60)
		private const WHITE_TEXT_COLOR: uint = 16777215;
		private const YELLOW_TEXT_COLOR: uint = 16252080;
		private const RED_TEXT_COLOR: uint = 6908415;
		
		internal var _cacheData:Object = CommonV2._createCacheDataObj(DisplayObject(this));
		
		public function CrosshairArcadeUI() 
		{
			super();
		}
		
		override public function setReloadingAsPercent(param1:Number) : void
		{
			if(reloadingTime == param1)
			{
				return;
			}
        reloadingTime = param1;
        reloadingBar.gotoAndStop(this.RELOADING_BAR_FRAMERATE[netType] * reloadingTime);
      	}     

	  	override public function setReloadingState(param1:String) : void
    	{
        	if(reloadingState != param1)
        	{
				reloadingState = param1;
				this.setTimerReloadingState();
				if(reloadingState == CrosshairConsts.RELOADING_END)
				{
				reloadingAnimationMC.visible = true;
				}
				else if(this.reloadingState == CrosshairConsts.RELOADING_ENDED)
				{
				reloadingAnimationMC.visible = true;
				}
				else
				{
				reloadingAnimationMC.visible = false;
				}
        	}
    	}
		override public function setClipsParam(param1:Number, param2:Number, param3:Boolean = false) : void
    	{
		 super.setClipsParam(param1,param2,param3);
         this._cacheData.clipParams.clipCapacity = param1;
         if(param1 > 1)
         {
            this._cacheData.clipParams.enabled = !param3;
            this._cacheData.clipParams.burst = param2;
            this.ownCassetMC.visible = !param3;
            this.ownCassetMC.clipContainer.clipBG.gotoAndStop(param1 / param2 + 1);
			this.clipCount.fullclip.text = String(param1 / param2);
			this.clipCount.count.text = "0";
         }
    	}

      override public function setAmmoStock(param1:Number, param2:String, param3:Boolean = false) : void
      	{
         	super.setAmmoStock(param1,param2,param3);
			
			if(this._cacheData.clipParams.enabled)
			{
				if(param3)
				{
				this.ownCassetMC.clipContainer.gotoAndPlay("reloaded");
				}
				else
				{
				this.ownCassetMC.clipContainer.gotoAndStop(param2);
				}
				if(param1)
				{
				this.ownCassetMC.clipContainer.clip.gotoAndStop(param1 / this._cacheData.clipParams.burst + 1);
				var cc = param1 / this._cacheData.clipParams.burst
				if(cc > 1)
					{
						this.clipCount.fullclip.textColor = WHITE_TEXT_COLOR;
						this.clipCount.Slh.textColor = WHITE_TEXT_COLOR;
						this.clipCount.count.textColor = WHITE_TEXT_COLOR;
						this.clipCount.count.text = String(param1 / this._cacheData.clipParams.burst);
					}
				else
					{
						this.clipCount.fullclip.textColor = YELLOW_TEXT_COLOR;
						this.clipCount.Slh.textColor = YELLOW_TEXT_COLOR;
						this.clipCount.count.textColor = YELLOW_TEXT_COLOR;
						this.clipCount.count.text = "1";
					}
				}
				else
				{
					this.ownCassetMC.clipContainer.clip.gotoAndStop(1);
					this.clipCount.fullclip.textColor = RED_TEXT_COLOR;
					this.clipCount.Slh.textColor = RED_TEXT_COLOR;
					this.clipCount.count.textColor = RED_TEXT_COLOR;
					this.clipCount.count.text = "0";
				}
			}
      	}
	}
}