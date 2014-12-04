# coding:utf-8

"""
Converts ActionScript3 to JavaScript.

Forked from 06\_jw as2js by Ethan Kennerly.
"""

import codecs
import os
import re
import json
import shutil
from os.path import getsize, splitext

import convert_cfg as cfg

namespace = '(?:private|protected|public|internal)'
argumentSave = '(\w+)\s*(:\w+)?\s*(\s*=\s*\w+)?'
prop = 'var\s+' + argumentSave + ';?'

noteP = re.compile('\*\*([\t\r\n][\s\S]+?)\*/', re.S)

staticPropP =  re.compile(
    '(?:' + 'static\s+' + namespace 
        + '|' + namespace + '\s+static' + ')'
    + '\s+' + prop, re.S)


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
    """
    staticProps = staticPropP.findall(klassContent)
    strs = []
    for name, dataType, definition in staticProps:
        line = 'var ' + klassName + '.' + name + definition + ';'
        strs.append(line)
    return '\n'.join(strs)


#                       private                     var    a       :  int

# http://revxatlarge.blogspot.com/2011/05/regular-expressions-excluding-strings.html
propP =  re.compile('(?<!static\s)' 
    + namespace + '\s+' + prop, re.S)


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
            definition = definition.replace('=', ':')
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
commentEndEscapeEscape = 'CommentEndEscape'

comment =  '/\*[^' + commentEndEscape + ']+' + commentEndEscape

#                                                     override        private                     function    func    (int a    )      :    int    {         }  
funcP =  re.compile('(\s*' + comment
    + '\s+){0,1}(?:override\s+)?' 
    + namespace 
    + '\s+function\s+(\w+)\s*\(([^\)]*)\)\s*(?::\s*\w+)?\s*{([\s\S]*?)}', re.S)

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
    <BLANKLINE>
    /* var ~ */
        ctor: function(X, Y, Width, Height, Zoom=0)
        {
    x=X
        }
    """
    escaped = klassContent.replace(commentEndEscape, commentEndEscapeEscape) \
        .replace(commentEnd, commentEndEscape)
    funcs = funcP.findall(escaped)
    str = ''
    for blockComment, name, argumentText, content in funcs:
        blockComment = blockComment.replace(commentEndEscape, commentEnd) \
            .replace(commentEndEscapeEscape, commentEndEscape)
        arguments = argumentP.findall(argumentText)
        arguments = [var + definition 
            for var, dataType, definition in arguments]
        argumentStr = ', '.join(arguments)
        if klassName == name:
            name = 'ctor'
        str += '\n' + blockComment + cfg.indent + name + ': function(' \
            + argumentStr \
            + ')\n' + cfg.indent + '{\n' + content + '\n' + cfg.indent + '}'
    return str


#                     package   org.pkg   {       class   ClasA    extends   Clas{        }}
klassP =  re.compile('package\s+[\w\.]+\s+{[\s\S]*class\s+(\w+)\s+(?:extends\s+\w+\s+)?{([\s\S]+)}\s*}', re.S)

def convert(text):
    klass = klassP.findall(text)[0]
    klassName = klass[0]
    klassContent = klass[1]

    str = '';
    str += 'var ' + klassName + ' = ' + cfg.baseClass + '.extend({' 
    str += '\n' + props(klassContent) 
    str += '\n' + methods(klassName, klassContent)
    str += '\n});'
    str += '\n\n' + staticProps(klassName, klassContent)
    return str


def write(filePath):
    asPath = filePath + '.as'
    jsPath = filePath + '.js'
    text = codecs.open(asPath, 'r', 'utf-8').read()
    str = convert(text)
    f = codecs.open(jsPath, 'w', 'utf-8')
    # print(str)
    f.write(str)
    f.close()   

def main():
    filePath = os.path.join('test', 'FlxBasic')
    write(filePath)

if '__main__' == __name__:
    import sys
    if len(sys.argv) <= 1 or '--test' != sys.argv[1]:
        main()
    import doctest
    doctest.testmod()

