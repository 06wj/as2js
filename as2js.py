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

argument = '(\w+)\s*(:\w+)?(\s*=\s*\w+)?'
argumentP =  re.compile(argument, re.S)

commentEnd = '*/'
commentEndEscape = '~'
commentEndEscapeEscape = 'commentEndEscapeEscape'

comment =  '/\*[^' + commentEndEscape + ']+' + commentEndEscape
commentPrefix = '(\s*' + comment + '\s*)?'
functionPrefix = commentPrefix + '(?:override\s+)?' 
functionEnd = '}'
functionEndEscape = '@'
functionEndEscapeEscape = 'functionEndEscapeEscape'
function = 'function\s+(\w+)\s*\(([^\)]*)\)\s*(?::\s*\w+)?\s*{([^' + functionEndEscape + ']*?)' + functionEndEscape

staticPropP =  re.compile(commentPrefix
    + staticNamespace
    + '\s+' + localVariable, re.S)


def staticProps(klassName, klassContent):
    r"""
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

    Block comment.
    >>> print staticProps('FlxBasic', '/* how many */\npublic static const ACTIVECOUNT:uint;')
    /* how many */
    var FlxBasic.ACTIVECOUNT;

    Block comment.
    >>> print staticProps('FlxBasic', '/* not me */\npublic const NOTME:uint;/* how many */\npublic static const ACTIVECOUNT:uint;')
    /* how many */
    var FlxBasic.ACTIVECOUNT;
    """
    staticProps = _parseProps(klassContent, staticPropP)
    strs = []
    for comment, name, dataType, definition in staticProps:
        line = ''
        if comment:
            line = comment
        line += 'var ' + klassName + '.' + name + definition + ';'
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
    """Comment, function end.
    Escape comment end, because non-greedy becomes greedy in context.  Example:
    blockCommentNonGreedy = '(\s*/\*[\s\S]+?\*/\s*){0,1}?'
    """
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
    """
    Preserve '&&'
    >>> _unescapeLocal(varEscapeEscape)
    '&'
    """
    return safe \
        .replace(varEscape, var) \
        .replace(varEscapeEscape, varEscape)


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
propP =  re.compile(commentPrefix
    + notStatic
    + namespace + '\s+' + localVariable, re.S)


def props(klassContent, inConstructor = False):
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
    >>> props('/** comment */\nstatic public var _ACTIVECOUNT:uint;')
    ''
    >>> props('public static var _ACTIVECOUNT:uint;')
    ''
    >>> props('static  public var _ACTIVECOUNT:uint;')
    '    _ACTIVECOUNT: undefined,'

    >>> print props('/** excluded */\nstatic public var _ACTIVECOUNT:uint;\n/** comment included */\npublic var x:int;')
    <BLANKLINE>
        /** comment included */
        x: undefined,

    Exclude undefined, indented twice.
    >>> props('public var ID:int = 1;\npublic var exists:Boolean;',
    ...     inConstructor = True)
    '    ID = 1;'

    Preserve block comment, if not in constructor.
    >>> print props('/** active */\n\npublic var _ACTIVECOUNT:uint;')
        /** active */
    <BLANKLINE>
        _ACTIVECOUNT: undefined,
    """
    props = _parseProps(klassContent, propP)
    strs = []
    for comment, declaration, dataType, definition in props:
        if definition:
            if not inConstructor:
                definition = definition.replace(' =', ':').replace('=', ':')
            include = True
        else:
            definition = ': undefined'
            include = False
        line = ''
        if not inConstructor:
            if comment:
                line = comment
        line += declaration + definition
        if not inConstructor or include:
            strs.append(line)
    str = ''
    if inConstructor:
        separator = ';'
    else:
        separator = ','
    if strs:
        lineSeparator = separator + '\n'
        str = lineSeparator.join(strs)
        str = indent(str, 1)
        str += separator
    return str


def _parseProps(klassContent, propP):
    escaped = _escapeEnds(klassContent)
    props = propP.findall(escaped)
    formatted = []
    for blockComment, name, dataType, definition in props:
        if blockComment:
            blockComment = _unescapeEnds(blockComment)
            blockComment += '\n'
            blockComment = indent(blockComment, 0)
        formatted.append([blockComment, name, dataType,
            definition])
    return formatted


def _parseFuncs(klassContent, methodP):
    """
    Preserve '&&'
    >>> klassContent = 'public static function no(){return 0 && 1}'
    >>> funcs = _parseFuncs(klassContent, staticMethodP)
    >>> print funcs[0]['content']
        return 0 && 1
    """
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
            content = trace(content)
            content = superClass(content)
        content = indent(content, 1)
        content = defaultArgumentText + content
        formatted.append({'blockComment': blockComment, 
            'name': name, 
            'argumentText': argumentText, 
            'content': content, 
            'defaultArguments': defaultArguments})
    return formatted


def indent(text, indents=1):
    r"""Standardize indent to a number of indents.
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
            space = cfg.indent * indents
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


def _findDeclarations(klassContent, propP):
    props = propP.findall(klassContent)
    declarations = []
    for comment, declaration, dataType, definition in props:
        declarations.append(declaration)
    return declarations


superClassP = re.compile(r'(\s+)super\s*(\()')

def superClass(funcContent):
    r"""Does not support call to another function.
    >>> print superClass('var a; super(a);\nsuper.f(1)');
    var a; this._super(a);
    super.f(1)
    """
    return re.sub(superClassP, r'\1' + cfg.superClass + r'\2', funcContent)


traceP = re.compile(r'(\s+)trace\s*(\()')

def trace(funcContent):
    r"""
    >>> print trace('var a; trace(a);\ntrace(1)');
    var a; cc.log(a);
    cc.log(1)
    """
    return re.sub(traceP, r'\1' + cfg.log + r'\2', funcContent)


def _findLocalDeclarations(funcContent):
    escaped = _escapeLocal(funcContent)
    variables = localVariableP.findall(escaped)
    declarations = [declaration
        for keyword, declaration, dataType, definition in variables]
    return declarations


def exclude(list, exclusions):
    """New list
    >>> exclude(['a', 'b', 'c'], ['b'])
    ['a', 'c']
    """
    included = []
    for item in list:
        if not item in exclusions:
            included.append(item)
    return included


identifierP = re.compile(r'\s+(\w+)\b')

def scopeMembers(memberDeclarations, funcContent, scope):
    r"""
    >>> print scopeMembers(['x', 'y', 'f'], 'var x:int = 0;\nx += y;\nf();\nfunction g(){}; g()', 'this')
    var x:int = 0;
    x += this.y;
    this.f();
    function g(){}; g()

    Include comments.
    >>> print scopeMembers(['x', 'y', 'f'], 'var x:int = 0;\n//x += y;', 'FlxCamera')
    var x:int = 0;
    //x += FlxCamera.y;
    """
    scoped = funcContent
    localDeclarations = _findLocalDeclarations(funcContent)
    memberDeclarations = exclude(memberDeclarations, localDeclarations)
    identifiers = identifierP.findall(funcContent)
    memberIdentifiers = [identifier
        for identifier in identifiers 
            if identifier in memberDeclarations]
    for identifier in memberIdentifiers:
        memberIdentifierP = re.compile(r'(\s+)(%s)\b' % identifier)
        scoped = re.sub(memberIdentifierP, r'\1%s.\2' % scope, scoped)
    return scoped


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

    Arguments.  Convert default value.
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
    >>> print methods('FlxCamera', 'internal function f(){\nvar i:uint=1;\ni++}')
        f: function()
        {
            var i=1;
            i++
        }

    Explicitly include defaults into constructor.
    >>> print methods('FlxCamera', '/** comment */\npublic var ID:int = 0;private var x:int;private var f:Function;/* var ~ */\npublic function FlxCamera(X:int,Y:int,Width:int,Height:int,Zoom:Number=0){\nx=X\nf()}')
        /* var ~ */
        ctor: function(X, Y, Width, Height, Zoom)
        {
            this.ID = 0;
            if (undefined === Zoom) {
                Zoom=0;
            }
            this.x=X
            this.f()
        }
    """
    funcs = _parseFuncs(klassContent, methodP)
    functionNames = [func['name'] for func in funcs]
    declarations = _findDeclarations(klassContent, propP) + functionNames
    strs = []
    for func in funcs:
        if klassName == func['name']:
            func['name'] = 'ctor'
            defaults = props(klassContent, True)
            if defaults:
                func['content'] = '\n' + defaults + func['content']
        func['content'] = scopeMembers(declarations, func['content'], 'this')
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
    >>> print staticMethods('FlxCamera', '/** comment */\npublic static var x:int;private static function f(){}/* var ~ */\npublic static function create(X:int,Y:int,Width:int,Height:int,Zoom:Number=0){\nf();\nx=X}')
    FlxCamera.f = function()
    {
    }
    <BLANKLINE>
    /* var ~ */
    FlxCamera.create = function(X, Y, Width, Height, Zoom)
    {
        if (undefined === Zoom) {
            Zoom=0;
        }
        FlxCamera.f();
        FlxCamera.x=X
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
    functionNames = [func['name'] for func in funcs]
    declarations = _findDeclarations(klassContent, staticPropP) + functionNames
    strs = []
    for func in funcs:
        func['name'] = klassName + '.' + func['name']
        func['content'] = scopeMembers(declarations, func['content'], klassName)
        str = _formatFunc(func, ' = ')
        strs.append(str)
    return '\n\n'.join(strs)


requireP = re.compile(r'\s*\bimport\s+([\w\.]+)')

def requires(text):
    r"""Reformat import statement as node.js require.
    >>> requires(' import flash.display.Bitmap;\nprivate var i:int;')
    'require("flash/display/Bitmap.js");\n\n'
    >>> requires('public var j:uint;\n import flash.display.Bitmap;\nprivate var i:int;')
    'require("flash/display/Bitmap.js");\n\n'
    """
    modules = requireP.findall(text)
    requiresText = ''
    if modules:
        requires = ['require("%s");' % (module.replace('.', '/') + '.js') 
            for module in modules]
        requiresText = '\n'.join(requires) + '\n\n'
    return requiresText


#                     package   org.pkg   {       class   ClasA    extends   Clas{        }}
klassCommentP =  re.compile('package\s*[\w\.]*\s*{[\s\S]*?' 
    + commentPrefix
    + namespace + '?\s*' + '(?:\s+final\s+)?'
    + 'class\s+\w+', re.S)

klassP =  re.compile('package\s*[\w\.]*\s*{[\s\S]*' 
    + 'class\s+(\w+)' 
    + '(?:\s+extends\s+\w+\s*)?\s*{([\s\S]*)}\s*}', re.S)

def findClassAndContent(text):
    r"""Return (blockComment, name, content)
    >>> findClassAndContent('package{\nclass Newline\n{}\n}')
    ['', 'Newline', '']

    Line comment not preserved.
    >>> findClassAndContent('package{class Oneline{}}')
    ['', 'Oneline', '']

    Line comment not preserved.
    >>> findClassAndContent('package{// line\nclass LineComment{}}')
    ['', 'LineComment', '']

    Block comment preserved.
    >>> findClassAndContent('package{/*comment*/public final class BlockComment{}}')
    ['/*comment*/', 'BlockComment', '']
    """
    escaped = _escapeEnds(text)
    # print escaped
    comments = klassCommentP.findall(escaped)
    nameContents = klassP.findall(text)
    if nameContents:
        commentNameContents = []
        if comments and comments[0]:
            comments[0] = _unescapeEnds(comments[0])
            commentNameContents.append(comments[0])
        else:
            commentNameContents.append('')
        commentNameContents.append(nameContents[0][0])
        commentNameContents.append(nameContents[0][1])
        return commentNameContents


def convert(text):
    klassComment, klassName, klassContent = findClassAndContent(text)

    str = '';
    str += requires(text)
    if klassComment:
        str += indent(klassComment, 0) + '\n'
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
    # Tests expect indent 4-spaces.
    cfg.indent = '    '
    import doctest
    doctest.testmod()

