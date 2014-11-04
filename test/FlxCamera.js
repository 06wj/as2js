var FlxCamera = function() {
	x = X;
	y = Y;
	width = Width;
	height = Height;
	target = null;
	deadzone = null;
	scroll = new FlxPoint();
	_point = new FlxPoint();
	bounds = null;
	screen = new FlxSprite();
	screen.makeGraphic(width, height, 0, true);
	screen.setOriginToCorner();
	buffer = screen.pixels;
	bgColor = FlxG.bgColor;
	_color = 0xffffff;

	_flashBitmap = new Bitmap(buffer);
	_flashBitmap.x = -width * 0.5;
	_flashBitmap.y = -height * 0.5;
	_flashSprite = new Sprite();
	zoom = Zoom; //sets the scale of flash sprite, which in turn loads flashoffset values
	_flashOffsetX = width * 0.5 * zoom;
	_flashOffsetY = height * 0.5 * zoom;
	_flashSprite.x = x + _flashOffsetX;
	_flashSprite.y = y + _flashOffsetY;
	_flashSprite.addChild(_flashBitmap);
	_flashRect = new Rectangle(0, 0, width, height);
	_flashPoint = new Point();

	_fxFlashColor = 0;
	_fxFlashDuration = 0.0;
	_fxFlashComplete = null;
	_fxFlashAlpha = 0.0;

	_fxFadeColor = 0;
	_fxFadeDuration = 0.0;
	_fxFadeComplete = null;
	_fxFadeAlpha = 0.0;

	_fxShakeIntensity = 0.0;
	_fxShakeDuration = 0.0;
	_fxShakeComplete = null;
	_fxShakeOffset = new FlxPoint();
	_fxShakeDirection = 0;

	_fill = new BitmapData(width, height, true, 0);
};
FlxCamera.defaultZoom = Number


/**
 * Clean up memory.
 */
FlxCamera.prototype.destroy = function() {
	screen.destroy();
	screen = null;
	target = null;
	scroll = null;
	deadzone = null;
	bounds = null;
	buffer = null;
	_flashBitmap = null;
	_flashRect = null;
	_flashPoint = null;
	_fxFlashComplete = null;
	_fxFadeComplete = null;
	_fxShakeComplete = null;
	_fxShakeOffset = null;
	_fill = null;
}


/**
 * Updates the camera scroll as well as special effects like screen-shake or fades.
 */
FlxCamera.prototype.update = function() {
	//Either follow the object closely, 
	//or doublecheck our deadzone and update accordingly.
	if (target != null) {
		if (deadzone == null)
			focusOn(target.getMidpoint(_point));
		else {
			var edge: Number;
			var targetX: Number = target.x + ((target.x > 0) ? 0.0000001 : -0.0000001);
			var targetY: Number = target.y + ((target.y > 0) ? 0.0000001 : -0.0000001);

			edge = targetX - deadzone.x;
			if (scroll.x > edge)
				scroll.x = edge;
			edge = targetX + target.width - deadzone.x - deadzone.width;
			if (scroll.x < edge)
				scroll.x = edge;

			edge = targetY - deadzone.y;
			if (scroll.y > edge)
				scroll.y = edge;
			edge = targetY + target.height - deadzone.y - deadzone.height;
			if (scroll.y < edge)
				scroll.y = edge;
		}


		/**
		 * Tells this camera object what <code>FlxObject</code> to track.
		 *
		 * @param	Target		The object you want the camera to track.  Set to null to not follow anything.
		 * @param	Style		Leverage one of the existing "deadzone" presets.  If you use a custom deadzone, ignore this parameter and manually specify the deadzone after calling <code>follow()</code>.
		 */
		FlxCamera.prototype.follow = function() {
			target = Target;
			var helper: Number;
			switch (Style) {
				case STYLE_PLATFORMER:
					var w: Number = width / 8;
					var h: Number = height / 3;
					deadzone = new FlxRect((width - w) / 2, (height - h) / 2 - h * 0.25, w, h);
					break;
				case STYLE_TOPDOWN:
					helper = FlxU.max(width, height) / 4;
					deadzone = new FlxRect((width - helper) / 2, (height - helper) / 2, helper, helper);
					break;
				case STYLE_TOPDOWN_TIGHT:
					helper = FlxU.max(width, height) / 8;
					deadzone = new FlxRect((width - helper) / 2, (height - helper) / 2, helper, helper);
					break;
				case STYLE_LOCKON:
				default:
					deadzone = null;
					break;
			}


			/**
			 * Move the camera focus to this location instantly.
			 *
			 * @param	Point		Where you want the camera to focus.
			 */
			FlxCamera.prototype.focusOn = function() {
				Point.x += (Point.x > 0) ? 0.0000001 : -0.0000001;
				Point.y += (Point.y > 0) ? 0.0000001 : -0.0000001;
				scroll.make(Point.x - width * 0.5, Point.y - height * 0.5);
			}


			/**
			 * Specify the boundaries of the level or where the camera is allowed to move.
			 *
			 * @param	X				The smallest X value of your level (usually 0).
			 * @param	Y				The smallest Y value of your level (usually 0).
			 * @param	Width			The largest X value of your level (usually the level width).
			 * @param	Height			The largest Y value of your level (usually the level height).
			 * @param	UpdateWorld		Whether the global quad-tree's dimensions should be updated to match (default: false).
			 */
			FlxCamera.prototype.setBounds = function() {
				if (bounds == null)
					bounds = new FlxRect();
				bounds.make(X, Y, Width, Height);
				if (UpdateWorld)
					FlxG.worldBounds.copyFrom(bounds);
				update();
			}


			/**
			 * The screen is filled with this color and gradually returns to normal.
			 *
			 * @param	Color		The color you want to use.
			 * @param	Duration	How long it takes for the flash to fade.
			 * @param	OnComplete	A function you want to run when the flash finishes.
			 * @param	Force		Force the effect to reset.
			 */
			FlxCamera.prototype.flash = function() {
				if (!Force && (_fxFlashAlpha > 0.0))
					return;
				_fxFlashColor = Color;
				if (Duration <= 0)
					Duration = Number.MIN_VALUE;
				_fxFlashDuration = Duration;
				_fxFlashComplete = OnComplete;
				_fxFlashAlpha = 1.0;
			}


			/**
			 * The screen is gradually filled with this color.
			 *
			 * @param	Color		The color you want to use.
			 * @param	Duration	How long it takes for the fade to finish.
			 * @param	OnComplete	A function you want to run when the fade finishes.
			 * @param	Force		Force the effect to reset.
			 */
			FlxCamera.prototype.fade = function() {
				if (!Force && (_fxFadeAlpha > 0.0))
					return;
				_fxFadeColor = Color;
				if (Duration <= 0)
					Duration = Number.MIN_VALUE;
				_fxFadeDuration = Duration;
				_fxFadeComplete = OnComplete;
				_fxFadeAlpha = Number.MIN_VALUE;
			}


			/**
			 * A simple screen-shake effect.
			 *
			 * @param	Intensity	Percentage of screen size representing the maximum distance that the screen can move while shaking.
			 * @param	Duration	The length in seconds that the shaking effect should last.
			 * @param	OnComplete	A function you want to run when the shake effect finishes.
			 * @param	Force		Force the effect to reset (default = true, unlike flash() and fade()!).
			 * @param	Direction	Whether to shake on both axes, just up and down, or just side to side (use class constants SHAKE_BOTH_AXES, SHAKE_VERTICAL_ONLY, or SHAKE_HORIZONTAL_ONLY).
			 */
			FlxCamera.prototype.shake = function() {
				if (!Force && ((_fxShakeOffset.x != 0) || (_fxShakeOffset.y != 0)))
					return;
				_fxShakeIntensity = Intensity;
				_fxShakeDuration = Duration;
				_fxShakeComplete = OnComplete;
				_fxShakeDirection = Direction;
				_fxShakeOffset.make();
			}


			/**
			 * Just turns off all the camera effects instantly.
			 */
			FlxCamera.prototype.stopFX = function() {
				_fxFlashAlpha = 0.0;
				_fxFadeAlpha = 0.0;
				_fxShakeDuration = 0;
				_flashSprite.x = x + width * 0.5;
				_flashSprite.y = y + height * 0.5;
			}


			/**
			 * Copy the bounds, focus object, and deadzone info from an existing camera.
			 *
			 * @param	Camera	The camera you want to copy from.
			 *
			 * @return	A reference to this <code>FlxCamera</code> object.
			 */
			FlxCamera.prototype.copyFrom = function() {
				if (Camera.bounds == null)
					bounds = null;
				else {
					if (bounds == null)
						bounds = new FlxRect();
					bounds.copyFrom(Camera.bounds);
				}


				/**
				 * The zoom level of this camera. 1 = 1:1, 2 = 2x zoom, etc.
				 */
				public
				function get zoom(): Number {
					return _zoom;
				}

				/**
				 * @private
				 */
				public
				function set zoom(Zoom: Number): void {
					if (Zoom == 0)
						_zoom = defaultZoom;
					else
						_zoom = Zoom;
					setScale(_zoom, _zoom);
				}

				/**
				 * The alpha value of this camera display (a Number between 0.0 and 1.0).
				 */
				public
				function get alpha(): Number {
					return _flashBitmap.alpha;
				}

				/**
				 * @private
				 */
				public
				function set alpha(Alpha: Number): void {
					_flashBitmap.alpha = Alpha;
				}

				/**
				 * The angle of the camera display (in degrees).
				 * Currently yields weird display results,
				 * since cameras aren't nested in an extra display object yet.
				 */
				public
				function get angle(): Number {
					return _flashSprite.rotation;
				}

				/**
				 * @private
				 */
				public
				function set angle(Angle: Number): void {
					_flashSprite.rotation = Angle;
				}

				/**
				 * The color tint of the camera display.
				 */
				public
				function get color(): uint {
					return _color;
				}

				/**
				 * @private
				 */
				public
				function set color(Color: uint): void {
					_color = Color;
					var colorTransform: ColorTransform = _flashBitmap.transform.colorTransform;
					colorTransform.redMultiplier = (_color >> 16) * 0.00392;
					colorTransform.greenMultiplier = (_color >> 8 & 0xff) * 0.00392;
					colorTransform.blueMultiplier = (_color & 0xff) * 0.00392;
					_flashBitmap.transform.colorTransform = colorTransform;
				}

				/**
				 * Whether the camera display is smooth and filtered, or chunky and pixelated.
				 * Default behavior is chunky-style.
				 */
				public
				function get antialiasing(): Boolean {
					return _flashBitmap.smoothing;
				}

				/**
				 * @private
				 */
				public
				function set antialiasing(Antialiasing: Boolean): void {
					_flashBitmap.smoothing = Antialiasing;
				}

				/**
				 * The scale of the camera object, irrespective of zoom.
				 * Currently yields weird display results,
				 * since cameras aren't nested in an extra display object yet.
				 */
				FlxCamera.prototype.getScale = function() {
					return _point.make(_flashSprite.scaleX, _flashSprite.scaleY);
				}


				/**
				 * @private
				 */
				FlxCamera.prototype.setScale = function() {
					_flashSprite.scaleX = X;
					_flashSprite.scaleY = Y;
				}


				/**
				 * Fetches a reference to the Flash <code>Sprite</code> object
				 * that contains the camera display in the Flash display list.
				 * Uses include 3D projection, advanced display list modification, and more.
				 * NOTE: We don't recommend modifying this directly unless you are
				 * fairly experienced.  For simple changes to the camera display,
				 * like scaling, rotation, and color tinting, we recommend
				 * using the existing <code>FlxCamera</code> variables.
				 *
				 * @return	A Flash <code>Sprite</code> object containing the camera display.
				 */
				FlxCamera.prototype.getContainerSprite = function() {
					return _flashSprite;
				}


				/**
				 * Fill the camera with the specified color.
				 *
				 * @param	Color		The color to fill with in 0xAARRGGBB hex format.
				 * @param	BlendAlpha	Whether to blend the alpha value or just wipe the previous contents.  Default is true.
				 */
				FlxCamera.prototype.fill = function() {
					_fill.fillRect(_flashRect, Color);
					buffer.copyPixels(_fill, _flashRect, _flashPoint, null, null, BlendAlpha);
				}