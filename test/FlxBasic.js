var FlxBasic = cc.Class.extend({
			ID = -1;
			exists = true;
			active = true;
			visible = true;
			alive = true;
			ignoreDrawDebug = false;
		});
var FlxBasic._ACTIVECOUNT;
var FlxBasic._VISIBLECOUNT;


		/**
		 * Override this function to null out variables or manually call
		 * <code>destroy()</code> on class members if necessary.
		 * Don't forget to call <code>super.destroy()</code>!
		 */
		FlxBasic.prototype.destroy = function(){}

		
		/**
		 * Pre-update is called right before <code>update()</code> on each object in the game loop.
		 */
		FlxBasic.prototype.preUpdate = function(){
			_ACTIVECOUNT++;
		}

		
		/**
		 * Override this function to update your class's position and appearance.
		 * This is where most of your game rules and behavioral code will go.
		 */
		FlxBasic.prototype.update = function(){
		}

		
		/**
		 * Post-update is called right after <code>update()</code> on each object in the game loop.
		 */
		FlxBasic.prototype.postUpdate = function(){
		}

		
		/**
		 * Override this function to control how the object is drawn.
		 * Overriding <code>draw()</code> is rarely necessary, but can be very useful.
		 */
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

		
		/**
		 * Override this function to draw custom "debug mode" graphics to the
		 * specified camera while the debugger's visual mode is toggled on.
		 * 
		 * @param	Camera	Which camera to draw the debug visuals to.
		 */
		FlxBasic.prototype.drawDebug = function(){
		}

		
		/**
		 * Handy function for "killing" game objects.
		 * Default behavior is to flag them as nonexistent AND dead.
		 * However, if you want the "corpse" to remain in the game,
		 * like to animate an effect or whatever, you should override this,
		 * setting only alive to false, and leaving exists true.
		 */
		FlxBasic.prototype.kill = function(){
			alive = false;
			exists = false;
		}

		
		/**
		 * Handy function for bringing game objects "back to life". Just sets alive and exists back to true.
		 * In practice, this function is most often called by <code>FlxObject.reset()</code>.
		 */
		FlxBasic.prototype.revive = function(){
			alive = true;
			exists = true;
		}

		
		/**
		 * Convert object to readable string name.  Useful for debugging, save games, etc.
		 */
		FlxBasic.prototype.toString = function(){
			return FlxU.getClassName(this,true);
		}