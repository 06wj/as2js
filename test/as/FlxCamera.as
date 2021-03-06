package org.flixel
{
    import flash.display.Bitmap;
    import flash.display.BitmapData;
    import flash.display.Sprite;
    import flash.geom.ColorTransform;
    import flash.geom.Point;
    import flash.geom.Rectangle;

    public class FlxCamera
    {
        public static var STYLE_LOCKON = 0;
        public static var STYLE_PLATFORMER = 1;
        public static var STYLE_TOPDOWN = 2;
        public static var STYLE_TOPDOWN_TIGHT = 3;
        public static var SHAKE_BOTH_AXES = 0;
        public static var SHAKE_HORIZONTAL_ONLY = 1;
        public static var SHAKE_VERTICAL_ONLY = 2;
        public static var defaultZoom;


        public var x;
        public var y;
        public var width;
        public var height;
        public var target;
        public var deadzone;
        public var bounds;
        public var scroll;
        public var buffer;
        public var bgColor;
        public var screen;
        public var _zoom;
        public var _point;
        public var _color;
        public var _flashBitmap;
        public var _flashSprite;
        public var _flashOffsetX;
        public var _flashOffsetY;
        public var _flashRect;
        public var _flashPoint;
        public var _fxFlashColor;
        public var _fxFlashDuration;
        public var _fxFlashComplete;
        public var _fxFlashAlpha;
        public var _fxFadeColor;
        public var _fxFadeDuration;
        public var _fxFadeComplete;
        public var _fxFadeAlpha;
        public var _fxShakeIntensity;
        public var _fxShakeDuration;
        public var _fxShakeComplete;
        public var _fxShakeOffset;
        public var _fxShakeDirection;
        public var _fill;



        /**
         * Instantiates a new camera at the specified location, with the specified size and zoom level.
         * 
         * @param X			X location of the camera's display in pixels. Uses native, 1:1 resolution, ignores zoom.
         * @param Y			Y location of the camera's display in pixels. Uses native, 1:1 resolution, ignores zoom.
         * @param Width		The width of the camera display in pixels.
         * @param Height	The height of the camera display in pixels.
         * @param Zoom		The initial zoom level of the camera.  A zoom level of 2 will make all pixels display at 2x resolution.
         */
        public function FlxCamera(X = undefined, Y = undefined, Width = undefined, Height = undefined, Zoom=0)
        {
            this.x = X;
            this.y = Y;
            this.width = Width;
            this.height = Height;
            this.target = null;
            this.deadzone = null;
            this.scroll = new FlxPoint();
            this._point = new FlxPoint();
            this.bounds = null;
            this.screen = new FlxSprite();
            this.screen.makeGraphic(width,height,0,true);
            this.screen.setOriginToCorner();
            this.buffer = this.screen.pixels;
            this.bgColor = FlxG.bgColor;
            this._color = 0xffffff;

            this._flashBitmap = new Bitmap(buffer);
            this._flashBitmap.x = -width*0.5;
            this._flashBitmap.y = -height*0.5;
            this._flashSprite = new Sprite();
            zoom = Zoom; //sets the scale of this.flash sprite, which in turn loads flashoffset values
            this._flashOffsetX = this.width*0.5*zoom;
            this._flashOffsetY = this.height*0.5*zoom;
            this._flashSprite.x = this.x + this._flashOffsetX;
            this._flashSprite.y = this.y + this._flashOffsetY;
            this._flashSprite.addChild(_flashBitmap);
            this._flashRect = new Rectangle(0,0,width,height);
            this._flashPoint = new Point();

            this._fxFlashColor = 0;
            this._fxFlashDuration = 0.0;
            this._fxFlashComplete = null;
            this._fxFlashAlpha = 0.0;

            this._fxFadeColor = 0;
            this._fxFadeDuration = 0.0;
            this._fxFadeComplete = null;
            this._fxFadeAlpha = 0.0;

            this._fxShakeIntensity = 0.0;
            this._fxShakeDuration = 0.0;
            this._fxShakeComplete = null;
            this._fxShakeOffset = new FlxPoint();
            this._fxShakeDirection = 0;

            this._fill = new BitmapData(width,height,true,0);
        }



        /**
         * Clean up memory.
         */
        public function destroy()
        {
            this.screen.destroy();
            this.screen = null;
            this.target = null;
            this.scroll = null;
            this.deadzone = null;
            this.bounds = null;
            this.buffer = null;
            this._flashBitmap = null;
            this._flashRect = null;
            this._flashPoint = null;
            this._fxFlashComplete = null;
            this._fxFadeComplete = null;
            this._fxShakeComplete = null;
            this._fxShakeOffset = null;
            this._fill = null;
        }



        /**
         * Updates the camera scroll as well as special effects like screen-shake or fades.
         */
        public function update()
        {
            //Either this.follow the object closely, 
            //or doublecheck our this.deadzone and this.update accordingly.
            if(target != null)
            {
            	if(deadzone == null)
            		this.focusOn(target.getMidpoint(_point));
            	else
            	{
            		var edge;
            		var targetX = this.target.x + ((target.x > 0)?0.0000001:-0.0000001);
            		var targetY = this.target.y + ((target.y > 0)?0.0000001:-0.0000001);

            		edge = targetX - this.deadzone.x;
            		if(scroll.x > edge)
            			this.scroll.x = edge;
            		edge = targetX + this.target.width - this.deadzone.x - this.deadzone.width;
            		if(scroll.x < edge)
            			this.scroll.x = edge;

            		edge = targetY - this.deadzone.y;
            		if(scroll.y > edge)
            			this.scroll.y = edge;
            		edge = targetY + this.target.height - this.deadzone.y - this.deadzone.height;
            		if(scroll.y < edge)
            			this.scroll.y = edge;
            	}
            }

            //Make sure we didn't go outside the camera's this.bounds
            if(bounds != null)
            {
            	if(scroll.x < this.bounds.left)
            		this.scroll.x = this.bounds.left;
            	if(scroll.x > this.bounds.right - this.width)
            		this.scroll.x = this.bounds.right - this.width;
            	if(scroll.y < this.bounds.top)
            		this.scroll.y = this.bounds.top;
            	if(scroll.y > this.bounds.bottom - this.height)
            		this.scroll.y = this.bounds.bottom - this.height;
            }

            //Update the "flash" special effect
            if(_fxFlashAlpha > 0.0)
            {
            	this._fxFlashAlpha -= FlxG.elapsed/_fxFlashDuration;
            	if((_fxFlashAlpha <= 0) && (_fxFlashComplete != null))
            		this._fxFlashComplete();
            }

            //Update the "fade" special effect
            if((_fxFadeAlpha > 0.0) && (_fxFadeAlpha < 1.0))
            {
            	this._fxFadeAlpha += FlxG.elapsed/_fxFadeDuration;
            	if(_fxFadeAlpha >= 1.0)
            	{
            		this._fxFadeAlpha = 1.0;
            		if(_fxFadeComplete != null)
            			this._fxFadeComplete();
            	}
            }

            //Update the "shake" special effect
            if(_fxShakeDuration > 0)
            {
            	this._fxShakeDuration -= FlxG.elapsed;
            	if(_fxShakeDuration <= 0)
            	{
            		this._fxShakeOffset.make();
            		if(_fxShakeComplete != null)
            			this._fxShakeComplete();
            	}
            	else
            	{
            		if((_fxShakeDirection == SHAKE_BOTH_AXES) || (_fxShakeDirection == SHAKE_HORIZONTAL_ONLY))
            			this._fxShakeOffset.x = (FlxG.random()*_fxShakeIntensity*width*2-_fxShakeIntensity*width)*_zoom;
            		if((_fxShakeDirection == SHAKE_BOTH_AXES) || (_fxShakeDirection == SHAKE_VERTICAL_ONLY))
            			this._fxShakeOffset.y = (FlxG.random()*_fxShakeIntensity*height*2-_fxShakeIntensity*height)*_zoom;
            	}
            }
        }



        /**
         * Tells this camera object what <code>FlxObject</code> to track.
         * 
         * @param	Target		The object you want the camera to track.  Set to null to not follow anything.
         * @param	Style		Leverage one of the existing "deadzone" presets.  If you use a custom deadzone, ignore this parameter and manually specify the deadzone after calling <code>follow()</code>.
         */
        public function follow(Target = undefined, Style=STYLE_LOCKON)
        {
            this.target = Target;
            var helper;
            switch(Style)
            {
            	case STYLE_PLATFORMER:
            		var w = this.width/8;
            		var h = this.height/3;
            		this.deadzone = new FlxRect((width-w)/2,(height-h)/2 - h*0.25,w,h);
            		break;
            	case STYLE_TOPDOWN:
            		helper = FlxU.max(width,height)/4;
            		this.deadzone = new FlxRect((width-helper)/2,(height-helper)/2,helper,helper);
            		break;
            	case STYLE_TOPDOWN_TIGHT:
            		helper = FlxU.max(width,height)/8;
            		this.deadzone = new FlxRect((width-helper)/2,(height-helper)/2,helper,helper);
            		break;
            	case STYLE_LOCKON:
            	default:
            		this.deadzone = null;
            		break;
            }
        }



        /**
         * Move the camera focus to this location instantly.
         * 
         * @param	Point		Where you want the camera to focus.
         */
        public function focusOn(Point = undefined)
        {
            Point.x += (Point.x > 0)?0.0000001:-0.0000001;
            Point.y += (Point.y > 0)?0.0000001:-0.0000001;
            this.scroll.make(Point.x - this.width*0.5,Point.y - this.height*0.5);
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
        public function setBounds(X=0, Y=0, Width=0, Height=0, UpdateWorld=false)
        {
            if(bounds == null)
            	this.bounds = new FlxRect();
            this.bounds.make(X,Y,Width,Height);
            if(UpdateWorld)
            	FlxG.worldBounds.copyFrom(bounds);
            this.update();
        }



        /**
         * The screen is filled with this color and gradually returns to normal.
         * 
         * @param	Color		The color you want to use.
         * @param	Duration	How long it takes for the flash to fade.
         * @param	OnComplete	A function you want to run when the flash finishes.
         * @param	Force		Force the effect to reset.
         */
        public function flash(Color=0xffffffff, Duration=1, OnComplete=null, Force=false)
        {
            if(!Force && (_fxFlashAlpha > 0.0))
            	return;
            this._fxFlashColor = Color;
            if(Duration <= 0)
            	Duration = Number.MIN_VALUE;
            this._fxFlashDuration = Duration;
            this._fxFlashComplete = OnComplete;
            this._fxFlashAlpha = 1.0;
        }



        /**
         * The screen is gradually filled with this color.
         * 
         * @param	Color		The color you want to use.
         * @param	Duration	How long it takes for the fade to finish.
         * @param	OnComplete	A function you want to run when the fade finishes.
         * @param	Force		Force the effect to reset.
         */
        public function fade(Color=0xff000000, Duration=1, OnComplete=null, Force=false)
        {
            if(!Force && (_fxFadeAlpha > 0.0))
            	return;
            this._fxFadeColor = Color;
            if(Duration <= 0)
            	Duration = Number.MIN_VALUE;
            this._fxFadeDuration = Duration;
            this._fxFadeComplete = OnComplete;
            this._fxFadeAlpha = Number.MIN_VALUE;
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
        public function shake(Intensity=0, 05 = undefined, Duration=0, 5 = undefined, OnComplete=null, Force=true, Direction=SHAKE_BOTH_AXES)
        {
            if(!Force && ((_fxShakeOffset.x != 0) || (_fxShakeOffset.y != 0)))
            	return;
            this._fxShakeIntensity = Intensity;
            this._fxShakeDuration = Duration;
            this._fxShakeComplete = OnComplete;
            this._fxShakeDirection = Direction;
            this._fxShakeOffset.make();
        }



        /**
         * Just turns off all the camera effects instantly.
         */
        public function stopFX()
        {
            this._fxFlashAlpha = 0.0;
            this._fxFadeAlpha = 0.0;
            this._fxShakeDuration = 0;
            this._flashSprite.x = this.x + this.width*0.5;
            this._flashSprite.y = this.y + this.height*0.5;
        }



        /**
         * Copy the bounds, focus object, and deadzone info from an existing camera.
         * 
         * @param	Camera	The camera you want to copy from.
         * 
         * @return	A reference to this <code>FlxCamera</code> object.
         */
        public function copyFrom(Camera = undefined)
        {
            if(Camera.bounds == null)
            	this.bounds = null;
            else
            {
            	if(bounds == null)
            		this.bounds = new FlxRect();
            	this.bounds.copyFrom(Camera.bounds);
            }
            this.target = Camera.target;
            if(target != null)
            {
            	if(Camera.deadzone == null)
            		this.deadzone = null;
            	else
            	{
            		if(deadzone == null)
            			this.deadzone = new FlxRect();
            		this.deadzone.copyFrom(Camera.deadzone);
            	}
            }
            return this;
        }



        /**
         * The scale of the camera object, irrespective of zoom.
         * Currently yields weird display results,
         * since cameras aren't nested in an extra display object yet.
         */
        public function getScale()
        {
            return this._point.make(_flashSprite.scaleX,_flashSprite.scaleY);
        }



        /**
         * @private
         */
        public function setScale(X = undefined, Y = undefined)
        {
            this._flashSprite.scaleX = X;
            this._flashSprite.scaleY = Y;
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
        public function getContainerSprite()
        {
            return this._flashSprite;
        }



        /**
         * Fill the camera with the specified color.
         * 
         * @param	Color		The color to fill with in 0xAARRGGBB hex format.
         * @param	BlendAlpha	Whether to blend the alpha value or just wipe the previous contents.  Default is true.
         */
        public function fill(Color = undefined, BlendAlpha=true)
        {
            this._fill.fillRect(_flashRect,Color);
            this.buffer.copyPixels(_fill,_flashRect,_flashPoint,null,null,BlendAlpha);
        }



        /**
         * Internal helper function, handles the actual drawing of all the special effects.
         */
        public function drawFX()
        {
            var alphaComponent;

            //Draw the "flash" special effect onto the this.buffer
            if(_fxFlashAlpha > 0.0)
            {
            	alphaComponent = this._fxFlashColor>>24;
            	this.fill((uint(((alphaComponent <= 0)?0xff:alphaComponent)*_fxFlashAlpha)<<24)+(_fxFlashColor&0x00ffffff));
            }

            //Draw the "fade" special effect onto the this.buffer
            if(_fxFadeAlpha > 0.0)
            {
            	alphaComponent = this._fxFadeColor>>24;
            	this.fill((uint(((alphaComponent <= 0)?0xff:alphaComponent)*_fxFadeAlpha)<<24)+(_fxFadeColor&0x00ffffff));
            }

            if((_fxShakeOffset.x != 0) || (_fxShakeOffset.y != 0))
            {
            	this._flashSprite.x = this.x + this._flashOffsetX + this._fxShakeOffset.x;
            	this._flashSprite.y = this.y + this._flashOffsetY + this._fxShakeOffset.y;
            }
        }
    }
}