as2js
=====

Reformat ActionScript 3 class files to JavaScript.

Forked from 06\_jw as2js by Ethan Kennerly.


Usage
=====

* Manually conform ActionScript to JavaScript by each item in not supported.

* Reformat:

    python as2js.py file.as

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


Not supported
=============

 * Preserve variable comment.

 * Preserve class comment.

 * Reformat super to this.\_super.

 * Apply Math.floor to float converted to an int or uint.

 * Auto prefix private variables with underscore.

 * Vim in-place:  Read text from standard input and return text for use in vim 

    :%!python -m as2js/convert

 * Variable or method with undeclared namespace.
 * ActionScript 'get' and 'set' functions.

 * Multiple classes per file.

 * Classes without functions.
 
 * Nonalphanumeric variable and function characters like '$'.

 * Globals.

 * Preprocessor directives such as "include".

 * Anything else not mentioned in features above.
