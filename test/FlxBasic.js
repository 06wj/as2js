
/**
 * This is a useful "generic" Flixel object.
 * Both <code>FlxObject</code> and <code>FlxGroup</code> extend this class,
 * as do the plugins.  Has no size, position or graphical data.
 * 
 * @author	Adam Atomic
 */
var FlxBasic = cc.Class.extend({
    /**
     * IDs seem like they could be pretty useful, huh?
     * They're not actually used for anything yet though.
     */
    ID: undefined,
    /**
     * Controls whether <code>update()</code> and <code>draw()</code> are automatically called by FlxState/FlxGroup.
     */
    exists: undefined,
    /**
     * Controls whether <code>update()</code> is automatically called by FlxState/FlxGroup.
     */
    active: undefined,
    /**
     * Controls whether <code>draw()</code> is automatically called by FlxState/FlxGroup.
     */
    visible: undefined,
    /**
     * Useful state for many game objects - "dead" (!alive) vs alive.
     * <code>kill()</code> and <code>revive()</code> both flip this switch (along with exists, but you can override that).
     */
    alive: undefined,
    /**
     * An array of camera objects that this object will use during <code>draw()</code>.
     * This value will initialize itself during the first draw to automatically
     * point at the main camera list out in <code>FlxG</code> unless you already set it.
     * You can also change it afterward too, very flexible!
     */
    cameras: undefined,
    /**
     * Setting this to true will prevent the object from appearing
     * when the visual debug mode in the debugger overlay is toggled on.
     */
    ignoreDrawDebug: undefined,

    /**
     * Instantiate the basic flixel object.
     */
    ctor: function()
    {
        this.ID = -1;
        this.exists = true;
        this.active = true;
        this.visible = true;
        this.alive = true;
        this.ignoreDrawDebug = false;
    },

    /**
     * Override this function to null out variables or manually call
     * <code>destroy()</code> on class members if necessary.
     * Don't forget to call <code>super.destroy()</code>!
     */
    destroy: function()
    {
    },

    /**
     * Pre-update is called right before <code>update()</code> on each object in the game loop.
     */
    preUpdate: function()
    {
        FlxBasic._ACTIVECOUNT++;
    },

    /**
     * Override this function to update your class's position and appearance.
     * This is where most of your game rules and behavioral code will go.
     */
    update: function()
    {
    },

    /**
     * Post-update is called right after <code>update()</code> on each object in the game loop.
     */
    postUpdate: function()
    {
    },

    /**
     * Override this function to control how the object is drawn.
     * Overriding <code>draw()</code> is rarely necessary, but can be very useful.
     */
    draw: function()
    {
        if(this.cameras == null)
        	this.cameras = FlxG.cameras;
        var camera;
        var i = 0;
        var l = this.cameras.length;
        while(i < l)
        {
        	camera = this.cameras[i++];
        	FlxBasic._VISIBLECOUNT++;
        	if(FlxG.visualDebug && !this.ignoreDrawDebug)
        		this.drawDebug(camera);
        }
    },

    /**
     * Override this function to draw custom "debug mode" graphics to the
     * specified camera while the debugger's visual mode is toggled on.
     * 
     * @param	Camera	Which camera to draw the debug visuals to.
     */
    drawDebug: function(Camera)
    {
        if (undefined === Camera) {
            Camera=null;
        }
    },

    /**
     * Handy function for "killing" game objects.
     * Default behavior is to flag them as nonexistent AND dead.
     * However, if you want the "corpse" to remain in the game,
     * like to animate an effect or whatever, you should override this,
     * setting only alive to false, and leaving exists true.
     */
    kill: function()
    {
        this.alive = false;
        this.exists = false;
    },

    /**
     * Handy function for bringing game objects "back to life". Just sets alive and exists back to true.
     * In practice, this function is most often called by <code>FlxObject.reset()</code>.
     */
    revive: function()
    {
        this.alive = true;
        this.exists = true;
    },

    /**
     * Convert object to readable string name.  Useful for debugging, save games, etc.
     */
    toString: function()
    {
        return FlxU.getClassName(this,true);
    }
});

var FlxBasic._ACTIVECOUNT;
var FlxBasic._VISIBLECOUNT;

