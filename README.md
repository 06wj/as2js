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

Todo
====

 * Default arguments.

 * Constructor member variable reassignment.

 * Convert import to node.js require.

 * Prefix private variables with underscore.

 * Prefix member usage with this.

 * Prefix static usage with class name.

 * Intermediate untyped, explicit scope ActionScript format.

 * Vim in-place:  Read text from standard input and return text for use in vim 

    :%!python -m as2js/convert


Not supported
=============

 * Variable or method with undeclared namespace.

 * Multiple classes per file.
 
 * Anything else not mentioned in features above.

 * Globals.
