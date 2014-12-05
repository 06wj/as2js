#coding: utf-8
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
import textwrap

import as2js_cfg as cfg

namespace = '(?:private|protected|public|internal)'
argumentSave = '(\w+)\s*(:\w+)?(\s*=\s*\w+)?'

var = 'var'
varKeyword = r'(?:\bvar\b|\bconst\b)'
varEscape = '&'
varEscapeEscape = '<varEscapeEscape>'
localVariable = varKeyword + '\s+' + argumentSave + ';?'
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

    Constant.
    >>> staticProps('FlxBasic', 'public static const ACTIVECOUNT:uint;')
    'var FlxBasic.ACTIVECOUNT;'
    """
    staticProps = staticPropP.findall(klassContent)
    strs = []
    for name, dataType, definition in staticProps:
        line = 'var ' + klassName + '.' + name + definition + ';'
        strs.append(line)
    return '\n'.join(strs)


def _escapeFunctionEnd(klassContent):
    """
    Escape end of outermost scope function.
    This makes a regular expression simple search until next character.
    Stack each open bracket and escape 0th stack closing bracket.
    >>> _escapeFunctionEnd('private static function f(){function g(){}}')
    'private static function f(){function g(){}@'

    Escape escape the raw escape character.
    >>> _escapeFunctionEnd('private static function f(@){function g(){}}')
    'private static function f(functionEndEscapeEscape){function g(){}@'

    Assumes matching parentheses.
    >>> _escapeFunctionEnd('}{function g(){}}')
    '}{function g(){@}'
    """
    escaped = klassContent.replace(functionEndEscape, functionEndEscapeEscape)
    characters = []
    characters += escaped
    blockBegin = '{'
    depth = 0
    for c, character in enumerate(characters):
        if blockBegin == character:
            depth += 1
        elif functionEnd == character:
            depth -= 1
            if 0 == depth:
                characters[c] = functionEndEscape
    return ''.join(characters)


def _escapeEnds(original):
    """Comment, function end."""
    commentEscaped = original \
        .replace(commentEndEscape, commentEndEscapeEscape) \
        .replace(commentEnd, commentEndEscape)
    return _escapeFunctionEnd(commentEscaped)


def _unescapeEnds(safe):
    """Comment, function end.
    >>> _unescapeEnds('functionEndEscapeEscape{@')
    '@{}'
    """
    return safe.replace(commentEndEscape, commentEnd) \
        .replace(commentEndEscapeEscape, commentEndEscape) \
        .replace(functionEndEscape, functionEnd) \
        .replace(functionEndEscapeEscape, functionEndEscape)


varKeywordP = re.compile(varKeyword)

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
function = 'function\s+(\w+)\s*\(([^\)]*)\)\s*(?::\s*\w+)?\s*{([^' + functionEndEscape + ']*?)' + functionEndEscape


def _parseFuncs(klassContent, methodP):
    escaped = _escapeEnds(klassContent)
    funcs = methodP.findall(escaped)
    formatted = []
    for blockComment, name, argumentAS, content in funcs:
        if blockComment:
            blockComment = _unescapeEnds(blockComment)
            blockComment += '\n'
        blockComment = indent(blockComment, 0)
        name = indent(name, 0)
        arguments = argumentP.findall(argumentAS)
        argumentsJS = []
        defaultArguments = []
        for declaration, dataType, definition in arguments:
            argumentsJS.append(declaration)
            if definition:
                defaultArguments.append('if (undefined === ' + declaration + ') {')
                defaultArguments.append(cfg.indent + declaration + definition + ';')
                defaultArguments.append('}')
        argumentText = ', '.join(argumentsJS)
        defaultArgumentText = '\n'.join(defaultArguments)
        if defaultArgumentText:
            defaultArgumentText = '\n' + indent(defaultArgumentText, 1)
        if not content or content.isspace():
            content = ''
        else:
            content = localVariables(content)
        content = indent(content, 1)
        content = defaultArgumentText + content
        formatted.append({'blockComment': blockComment, 
            'name': name, 
            'argumentText': argumentText, 
            'content': content, 
            'defaultArguments': defaultArguments})
    return formatted


def indent(text, tabs=1):
    r"""Standardize indent to a number of tabs.
    >>> print indent('             ab\n                 c', 1)
        ab
            c
    >>> print indent('             ab\n                 c', 2)
            ab
                c
    >>> print indent('                 ab\n                 c', 1)
        ab
        c
    >>> print indent('                 ab\n                 c', 0)
    ab
    c
    """
    text = textwrap.dedent(text.replace('\r\n', '\n'))
    lines = []
    for line in text.splitlines():
        if line:
            space = cfg.indent * tabs
        else:
            space = ''
        lines.append(space + line)
    text = '\n'.join(lines)
    return text


def _formatFunc(func, operator):
    return func['blockComment'] + func['name'] + operator + 'function(' \
        + func['argumentText'] \
        + ')\n{' \
        + func['content'] + '\n}'


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
    >>> print methods('FlxCamera', '/** comment */\npublic var ID:int;/* var ~ */\npublic function FlxCamera(X:int,Y:int,Width:int,Height:int,Zoom:Number=0){\nx=X}')
        /* var ~ */
        ctor: function(X, Y, Width, Height, Zoom)
        {
            if (undefined === Zoom) {
                Zoom=0;
            }
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
    >>> print methods('FlxCamera', 'internal function f(){\nvar i:uint=1}')
        f: function()
        {
            var i=1
        }
    """
    funcs = _parseFuncs(klassContent, methodP)
    strs = []
    for func in funcs:
        if klassName == func['name']:
            func['name'] = 'ctor'
        str = _formatFunc(func, ': ')
        str = indent(str, 1)
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
    >>> print staticMethods('FlxCamera', '/** comment */\npublic var ID:int;/* var ~ */\npublic static function create(X:int,Y:int,Width:int,Height:int,Zoom:Number=0){\nx=X}')
    /* var ~ */
    FlxCamera.create = function(X, Y, Width, Height, Zoom)
    {
        if (undefined === Zoom) {
            Zoom=0;
        }
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
    >>> print staticMethods('C', 'private static function f(){\nfunction g(){}}')
    C.f = function()
    {
        function g(){}
    }
    """ 
    funcs = _parseFuncs(klassContent, staticMethodP)
    strs = []
    for func in funcs:
        func['name'] = klassName + '.' + func['name']
        str = _formatFunc(func, ' = ')
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

