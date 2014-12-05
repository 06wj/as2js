as2js
=====

Converts ActionScript3 to JavaScript.

Forked from 06\_jw as2js by Ethan Kennerly.

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

Todo
====

 * Constructor member variable reassignment.

 * Convert import to node.js require.

 * Auto prefix member usage with this.

 * Auto prefix static usage with class name.

 * Intermediate untyped, explicit scope ActionScript format.

 * Class comment.

 * Constants.


Not supported
=============

 * Apply Math.floor to float converted to an int or uint.

 * Auto prefix private variables with underscore.

 * Vim in-place:  Read text from standard input and return text for use in vim 

    :%!python -m as2js/convert

 * Variable or method with undeclared namespace.

 * Multiple classes per file.
 
 * Nonalphanumeric variable and function characters like '$'.

 * Globals.

 * Anything else not mentioned in features above.
