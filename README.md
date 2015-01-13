as2js
=====

Reformat ActionScript 3 class files to JavaScript.

Forked from 06\_jw as2js by Ethan Kennerly.


Usage
=====

* Manually conform ActionScript to JavaScript by each item in not supported.

* Reformat:

    python as2js.py file.as [file.as ...]

* Manually conform JavaScript requires and libraries.


Features
========

 * Static functions.

 * Windows or Unix line endings.

 * Print text.

 * Declared, undefined variable.

 * Either order of declaring static.

 * Declare member variables.

 * Extend class idiom.

 * Methods in extend idiom.

 * Static methods.

 * Specify multiple files.

 * Configuration class to extend.

 * Remove data type from each local variable.

 * Nested brackets.

 * Dedent methods.

 * Default arguments.

 * Constants.

 * Constructor member variable reassignment.

 * Reformat import statement as node.js require.

 * Auto prefix member access with this.

 * Auto prefix static access with class name.

 * Reformat AS3 to untyped, explicit scope to test.

 * Trace statement to a log message.

 * Reformat super to this.\_super.

 * Preserve class comment.

 * Preserve variable comment.

 * Configure substitute require paths.

 * Override default configurations.

 * Remove data type from Try/catch.

 * Simple type casting with "as" operator.  
 
 * Simple pattern of "is" into "instanceof".

 * Typecasting with int(float) syntax using Math.floor.


Not supported
=============

Vim commands are listed for some of these manual translations.

 * Block comment on a single line.

 * Set undefined static property to undefined.

 * Static-only class needs no extend, so "extend" part could be replaced with an empty object {}.

 * Scoping is unaware of quoted string context.

 * Multiple variables assigned with a comma.

    :lvimgrep / var [^;]*, [^;]*:[A-Za-z\*]/ *.as

 * Extending a base class other than the configuration baseClass.

    :lvimgrep / extends / *.as

 * Reformat super call to another function to this.\_super.

    :lvimgrep /\<super\>/ *.as

 * Typecasting with MyType(variable) syntax.  Replace with "instanceof".

    :lvimgrep / uint(/ *.as

 * Preserve line comment before a member variable or function.

    :lvimgrep /^        \/\/ / *.as

 * Integer constants, such as "int.MIN\_VALUE"

    :lvimgrep /\<int\./ *.as

 * Auto prefix private variables with underscore.

    :args *.as
    :argdo %s/private var /private var _/gIce

 * Apply Math.floor to float converted to an int or uint.  Such as during random index.

    :args *.as
    :argdo %s/\(:int = \)\([^;]*random[^;]*;\)/\1Math.floor(\2)/gIce | update

 * Comments or parentheses in function arguments or variable definitions.

 * Vim in-place:  Read text from standard input and return text for use in vim 

    :%!python -m as2js/as2js.py

 * Variable or method with undeclared namespace.

    :lvimgrep /^        var / *.as
    :lvimgrep /^        function / *.as

 * Translate for each.  Example:  "for each(a in b){...}" into "for (var i = 0; i < b.length; i++) { var a = b[i]; ...}

    :lvimgrep /\<for each\>/ *.as

 * Include comment on return type and parameter type.

    :lvimgrep / function/ *.as

 * ActionScript 'get' and 'set' functions.

    :lvimgrep / function [gs]et / *.as

 * Require classes in same folder as this class.  Can explicitly include import.

    :lvimgrep /MyClass/ *.as

 * Does not tolerate missing semicolon after a variable definition.

    :lvimgrep / var .*[^;]$/ *.as

 * Multiple classes per file.

 * Nonalphanumeric variable and function characters like '$'.

    :lvimgrep /\$/ *.js

 * Static is defined first in ActionScript but last in this idiom of JavaScript.  So default assignments won't be found.

 * Globals.

 * References to classes created by Flash Professional.  
   ActionScript compiler needs the literal class to avoid pruning.  
   Strings are more portable than classes.
   These class references could be quoted, for example:

    :'a,'zs/\([A-Za-z0-9]\+\)/"\1"/g

 * Preprocessor directives such as "include".

    :argdo /\#include 

 * Flash utilities like Dictionary, getTimer, setTimeout, and others.

 * Anything else not mentioned in features above.



Not supported Flash: to Cocos2D v2
==================================

 * .parent: getParent() or setParent()

    :args *.js
    :argdo %s/\.parent\>/.getParent()/gIce | update

 * .visible: isVisible() or setVisible()

    :args *.js
    :%s/\.visible = /.setVisible(/gIce | update
    :%s/\.visible\>/.isVisible(/gIce | update

 * .mouseEnabled:  isEnabled(), setEnabled()

 * .numChildren: getChildCount() or getChildren()

 * .addChildAt(child, z):  addChild(child, z)

 * Custom function on parent:  parent.removeAllChildren()

 * addEventListener(MouseEvent.CLICK: Control button callback.


Not supported Flash: to SpriteBuilder-Reader-js
===============================================

See <http://github.com/ethankennerly/SpriteBuilder-Reader-js>

 * .name: getName() or setName()  (v3)

 * .gotoAndPlay:  animationManager.runAnimations

    :%s/gotoAndPlay/animationManager.runAnimations/gIce

 * .currentLabel:  .animationManager.getRunningSequenceName()

    :args *.js
    :argdo %s/\.currentLabel/.animationManager.getRunningSequenceName()/gIce | update
