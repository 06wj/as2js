"""
Converts some ActionScript3 to a JavaScript file.
Usage:  python as2js.py actionscriptFile.as [...]
Overwrites each .js file parallel to each .as file.
Usage:  python as2js.py --test
Just run unit tests.
Forked from 06\_jw as2js by Ethan Kennerly.
"""

import codecs
import os
import re

import as2js_cfg as cfg

namespace = '(?:private|protected|public|internal)'
argumentSave = '(\w+)\s*(:\w+)?(\s*=\s*\w+)?'
localVariable = r'\bvar\s+' + argumentSave + ';?'

var = 'var'
varKeyword = r'\b' + var + r'\b'
varEscape = '&'
varEscapeEscape = '<varEscapeEscape>'
localVariableEscaped = '(' + varEscape + '\s+)' + argumentSave
notStatic = '(?<!static\s)'
staticNamespace = '(?:' + 'static\s+' + namespace \
                  + '|' + namespace + '\s+static' + ')'

noteP = re.compile('\*\*([\t\r\n][\s\S]+?)\*/', re.S)

staticPropP =  re.compile(staticNamespace
    + '\s+' + localVariable, re.S)


def staticProps(klassName, klassContent):
    """
    Declared, defined variable without a space.
    >>> staticProps('FlxBasic', 'static internal var _VISIBLECOUNT:uint= 5;')
    'var FlxBasic._VISIBLECOUNT= 5;'

    Declared, undefined variable.
    >>> staticProps('FlxBasic', 'static internal var _ACTIVECOUNT:uint;')
    'var FlxBasic._ACTIVECOUNT;'

    Namespace first
    >>> staticProps('FlxBasic', 'private static var _VISIBLECOUNT:uint= 5;')
    'var FlxBasic._VISIBLECOUNT= 5;'

    Declared, undefined variable.
    >>> staticProps('FlxBasic', 'public static var _ACTIVECOUNT:uint;')
    'var FlxBasic._ACTIVECOUNT;'

    No namespace not supported.
    >>> staticProps('FlxBasic', 'static var _ACTIVECOUNT:uint;')
    ''
    """
    staticProps = staticPropP.findall(klassContent)
    strs = []
    for name, dataType, definition in staticProps:
        line = 'var ' + klassName + '.' + name + definition + ';'
        strs.append(line)
    return '\n'.join(strs)


varKeywordP = re.compile(varKeyword)

def _escape(original):
    return original \
        .replace(commentEndEscape, commentEndEscapeEscape) \
        .replace(commentEnd, commentEndEscape) \
        .replace(functionEndEscape, functionEndEscapeEscape) \
        .replace(functionEnd, functionEndEscape)


def _unescape(safe):
    return safe.replace(commentEndEscape, commentEnd) \
        .replace(commentEndEscapeEscape, commentEndEscape) \
        .replace(functionEndEscapeEscape, functionEndEscape) \
        .replace(functionEndEscape, functionEnd)


def _escapeLocal(original):
    r"""
    >>> _escapeLocal('var ivar:uint = 0;\nvar varj:uint = cameras.length;')
    '& ivar:uint = 0;\n& varj:uint = cameras.length;'
    """
    escaped = original.replace(varEscape, varEscapeEscape)
    return re.sub(varKeywordP, varEscape, escaped)


def _unescapeLocal(safe):
    return safe.replace(varEscapeEscape, varEscape) \
        .replace(varEscape, var)


localVariableP = re.compile(localVariableEscaped)

def localVariables(funcContent):
    r"""
    >>> print localVariables('var i:uint = 0;;')
    var i = 0;;

    Remove data type from each local variable.
    >>> print localVariables('var ivar:uint = 0;\nvar varj:uint = cameras.length;')
    var ivar = 0;
    var varj = cameras.length;
    >>> print localVariables('f();\nvar ivar:uint = 0;\ng();')
    f();
    var ivar = 0;
    g();
    """
    escaped = _escapeLocal(funcContent)
    variables = localVariableP.findall(escaped)
    dataTypes = [dataType
        for keyword, declaration, dataType, definition in variables]
    parts = localVariableP.split(escaped)
    # print parts, dataTypes
    content = ''
    for part in parts:
        if part not in dataTypes:
            if part:
                content += part
    content = _unescapeLocal(content)
    return content


#                       private                     var    a       :  int

# http://revxatlarge.blogspot.com/2011/05/regular-expressions-excluding-strings.html
propP =  re.compile(notStatic
    + namespace + '\s+' + localVariable, re.S)


def props(klassContent):
    r"""As object members, indented by 4-spaces, with trailing comma.
    Undefined.
    >>> props('  public var ID:int;\n        public var exists:Boolean;')
    '    ID: undefined,\n    exists: undefined,'

    Defined.
    >>> props('    public var ID:int = 1;\n    public var exists:Boolean = true;')
    '    ID: 1,\n    exists: true,'

    Exclude static if exactly one space, because lookbehind only supports fixed-width
    >>> props('public var _ACTIVECOUNT:uint;')
    '    _ACTIVECOUNT: undefined,'
    >>> props('static public var _ACTIVECOUNT:uint;')
    ''
    >>> props('public static var _ACTIVECOUNT:uint;')
    ''
    >>> props('static  public var _ACTIVECOUNT:uint;')
    '    _ACTIVECOUNT: undefined,'
    """
    props = propP.findall(klassContent)
    strs = []
    for name, dataType, definition in props:
        if definition:
            definition = definition.replace(' =', ':').replace('=', ':')
        else:
            definition = ': undefined'
        line = name + definition
        strs.append(line)
    separator = ',\n' + cfg.indent
    str = separator.join(strs)
    if strs:
        str = cfg.indent + str
        str += ','
    return str


argument = '(\w+)\s*(:\w+)?(\s*=\s*\w+)?'
argumentP =  re.compile(argument, re.S)

commentEnd = '*/'
commentEndEscape = '~'
commentEndEscapeEscape = 'commentEndEscapeEscape'

comment =  '/\*[^' + commentEndEscape + ']+' + commentEndEscape
functionPrefix = '(\s*' + comment + '\s+){0,1}(?:override\s+)?' 
functionEnd = '}'
functionEndEscape = '@'
functionEndEscapeEscape = 'functionEndEscapeEscape'
function = 'function\s+(\w+)\s*\(([^\)]*)\)\s*(?::\s*\w+)?\s*{([\s\S]*?)' + functionEndEscape


def _parseFuncs(klassContent, methodP):
    escaped = _escape(klassContent)
    funcs = methodP.findall(escaped)
    formatted = []
    for blockComment, name, argumentText, content in funcs:
        blockComment = _unescape(blockComment)
        arguments = argumentP.findall(argumentText)
        arguments = [declaration + definition 
            for declaration, dataType, definition in arguments]
        argumentFormatted = ', '.join(arguments)
        if not content or content.isspace():
            content = ''
        else:
            content = '\n' + content
            content = localVariables(content)
        formatted.append([blockComment, name, argumentFormatted, content])
    return formatted


#                                                     override        private                     function    func    (int a    )      :    int    {         }  
methodP =  re.compile(functionPrefix
    + notStatic
    + namespace 
    + '\s+' + function, re.S)


def methods(klassName, klassContent):
    r"""
    Ignore member variables.
    >>> methods('FlxCamera', '/** var */\npublic var ID:int;')
    ''

    Escapes end comment character with tilde, which is not special to pattern.
    >>> re.compile(comment, re.S).findall('/** comment ~/** var ~')
    ['/** comment ~', '/** var ~']

    Arguments.  Does not convert default value.
    >>> print methods('FlxCamera', '/** comment */\npublic var ID:int;/* var ~ */\npublic function FlxCamera(X:int,Y:int,Width:int,Height:int,Zoom:Number=0){x=X}')
    /* var ~ */
        ctor: function(X, Y, Width, Height, Zoom=0)
        {
    x=X
        }

    Ignore static functions.
    >>> methods('FlxCamera', '/** var */\nstatic public function f(){}')
    ''

    Comma-separate.
    >>> print methods('FlxCamera', 'internal function f(){}internal function g(){}')
        f: function()
        {
        },
    <BLANKLINE>
        g: function()
        {
        }

    Local variables.
    >>> print methods('FlxCamera', 'internal function f(){var i:uint=1}')
        f: function()
        {
    var i=1
        }
    """
    funcs = _parseFuncs(klassContent, methodP)
    strs = []
    for blockComment, name, argumentText, content in funcs:
        if klassName == name:
            name = 'ctor'
        str = blockComment + cfg.indent + name + ': function(' \
            + argumentText \
            + ')\n' + cfg.indent + '{' + content + '\n' + cfg.indent + '}'
        strs.append(str)
    return ',\n\n'.join(strs)


staticMethodP =  re.compile(functionPrefix
    + staticNamespace
    + '\s+' + function, re.S)

def staticMethods(klassName, klassContent):
    r"""
    Ignore member variables.
    >>> staticMethods('FlxCamera', '/** var */\npublic static var ID:int;')
    ''

    Arguments.  Does not convert default value.
    >>> print staticMethods('FlxCamera', '/** comment */\npublic var ID:int;/* var ~ */\npublic static function create(X:int,Y:int,Width:int,Height:int,Zoom:Number=0){x=X}')
    /* var ~ */
    FlxCamera.create = function(X, Y, Width, Height, Zoom=0)
    {
    x=X
    }

    Ignore methods.
    >>> staticMethods('FlxCamera', '/** var */\npublic function f(){};')
    ''

    Multiple with 2 lines between.
    >>> print staticMethods('C', 'private static function f(){}private static function g(){}')
    C.f = function()
    {
    }
    <BLANKLINE>
    C.g = function()
    {
    }

    Nested local function brackets.
    >>> print staticMethods('C', 'private static function f(){function g(){}}')
    C.f = function()
    {
    g(){}
    }
    """ 
    funcs = _parseFuncs(klassContent, staticMethodP)
    strs = []
    for blockComment, name, argumentText, content in funcs:
        str = blockComment + klassName + '.' + name + ' = function(' \
            + argumentText \
            + ')\n{' + content + '\n}'
        strs.append(str)
    return '\n\n'.join(strs)

#                     package   org.pkg   {       class   ClasA    extends   Clas{        }}
klassP =  re.compile('package\s+[\w\.]+\s+{[\s\S]*class\s+(\w+)\s+(?:extends\s+\w+\s+)?{([\s\S]+)}\s*}', re.S)

def convert(text):
    klass = klassP.findall(text)[0]
    klassName = klass[0]
    klassContent = klass[1]

    str = '';
    str += 'var ' + klassName + ' = ' + cfg.baseClass + '.extend({' 
    str += '\n' + props(klassContent) 
    str += '\n\n' + methods(klassName, klassContent)
    str += '\n});'
    str += '\n\n' + staticProps(klassName, klassContent)
    str += '\n\n' + staticMethods(klassName, klassContent)
    return str


def convertFile(asPath, jsPath):
    text = codecs.open(asPath, 'r', 'utf-8').read()
    str = convert(text)
    f = codecs.open(jsPath, 'w', 'utf-8')
    # print(str)
    f.write(str)
    f.close()   


def convertFiles(asPaths):
    for asPath in asPaths:
        root, ext = os.path.splitext(asPath)
        jsPath = root + '.js'
        convertFile(asPath, jsPath)


if '__main__' == __name__:
    import sys
    if len(sys.argv) <= 1:
        print __doc__
    if 2 <= len(sys.argv) and '--test' != sys.argv[1]:
        convertFiles(sys.argv[1:])
    import doctest
    doctest.testmod()

