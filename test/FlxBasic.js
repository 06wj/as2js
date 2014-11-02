var FlxBasic = function(){};
FlxBasic._ACTIVECOUNT = uint
FlxBasic._VISIBLECOUNT = uint
FlxBasic.prototype.FlxBasic = function(){
			ID = -1;
			exists = true;
			active = true;
			visible = true;
			alive = true;
			ignoreDrawDebug = false;
		}
FlxBasic.prototype.destroy = function(){}
FlxBasic.prototype.preUpdate = function(){
			_ACTIVECOUNT++;
		}
FlxBasic.prototype.update = function(){
		}
FlxBasic.prototype.postUpdate = function(){
		}
FlxBasic.prototype.draw = function(){
			if(cameras == null)
				cameras = FlxG.cameras;
			var camera:FlxCamera;
			var i:uint = 0;
			var l:uint = cameras.length;
			while(i < l)
			{
				camera = cameras[i++];
				_VISIBLECOUNT++;
				if(FlxG.visualDebug && !ignoreDrawDebug)
					drawDebug(camera);
			}
FlxBasic.prototype.kill = function(){
			alive = false;
			exists = false;
		}
FlxBasic.prototype.revive = function(){
			alive = true;
			exists = true;
		}
FlxBasic.prototype.toString = function(){
			return FlxU.getClassName(this,true);
		}