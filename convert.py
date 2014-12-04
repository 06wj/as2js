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

#                     package   org.pkg   {       class   ClasA    extends   Clas{        }}
klassP =  re.compile('package\s+[\w\.]+\s+{[\s\S]*class\s+(\w+)\s+(?:extends\s+\w+\s+)?{([\s\S]+)}\s*}', re.S)

namespace = '(?:private|protected|public|internal)'

prop = 'var\s+(\w+)\s*(:\w+)?\s*(\s*=\s*\w+)?'

#                       private                     var    a       :  int
propP =  re.compile(namespace + '\s+' + prop, re.S)

#                                                     override        private                     function    func    (int a    )      :    int    {         }  
funcP =  re.compile('(\s+/\*\*[\t\r\n][\s\S]+?\*/\s+)(?:override\s+)?(?:private|protected|public|internal)\s+function\s+(\w+)\s*\([\s\S]*?\)\s*(?::\s*(\w+))?\s*{([\s\S]*?)}', re.S)

noteP = re.compile('\*\*([\t\r\n][\s\S]+?)\*/', re.S)

staticPropP =  re.compile(
    '(?:' + 'static\s+' + namespace 
        + '|' + namespace + '\s+static' + ')'
    + '\s+' + prop, re.S)


def staticProp(klassName, klassContent):
    """
    Declared, defined variable without a space.
    >>> staticProp('FlxBasic', 'static internal var _VISIBLECOUNT:uint= 5;')
    'var FlxBasic._VISIBLECOUNT= 5;'

    Declared, undefined variable.
    >>> staticProp('FlxBasic', 'static internal var _ACTIVECOUNT:uint;')
    'var FlxBasic._ACTIVECOUNT;'

    Namespace first
    >>> staticProp('FlxBasic', 'private static var _VISIBLECOUNT:uint= 5;')
    'var FlxBasic._VISIBLECOUNT= 5;'

    Declared, undefined variable.
    >>> staticProp('FlxBasic', 'public static var _ACTIVECOUNT:uint;')
    'var FlxBasic._ACTIVECOUNT;'
    """
    staticProps = staticPropP.findall(klassContent)
    strs = []
    for prop in staticProps:
        line = 'var ' + klassName + '.' + prop[0] + prop[2] + ';'
        strs.append(line)
    return '\n'.join(strs)


def convert(text):
    klass = klassP.findall(text)[0]
    klassName = klass[0]
    klassContent = klass[1]

    props = propP.findall(klassContent)   
    funcs = funcP.findall(klassContent)

    for func in funcs:
        if func[1] == klassName:
            constructor = func[3]
            funcs.remove(func)

    str = '';
    str += 'var ' + klassName + ' = ' + cfg.baseClass + '.extend({' + constructor + '});'

    str += '\n' + staticProp(klassName, klassContent)

    for func in funcs:
        str += '\n' + func[0] + klassName + '.prototype.' + func[1] + ' = function(){' + func[3] + '}'
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

