# coding:utf-8
import codecs
import os
import re
import json
import shutil
from os.path import getsize, splitext

filePath = os.path.join("test", "FlxBasic")
asPath = filePath + ".as"
jsPath = filePath + ".js"

text = codecs.open(asPath, "r", "utf-8").read()

#                     package   org.pkg   {       class   ClasA    extends   Clas{        }}
klassP =  re.compile('package\s+[\w\.]+\s+{[\s\S]*class\s+(\w+)\s+(?:extends\s+\w+\s+)?{([\s\S]+)}\s*}', re.S)

#                       private                     var    a       :  int
propP =  re.compile('(?:private|protected|public|internal)\s+var\s+(\w+)\s*:\s*(\w+)', re.S)

#                                                     override        private                     function    func    (int a    )      :    int    {         }  
funcP =  re.compile('(\s+/\*\*[\t\n][\s\S]+?\*/\s+)(?:override\s+)?(?:private|protected|public)\s+function\s+(\w+)\s*\([\s\S]*?\)\s*(?::\s*(\w+))?\s*{([\s\S]*?)}', re.S)

staticPropP = re.compile('static\s+(?:private|protected|public|internal)\s+var\s+(\w+)\s*:\s*(\w+)', re.S)

noteP = re.compile('\*\*([\t\n][\s\S]+?)\*/', re.S)


klass = klassP.findall(text)[0]
klassName = klass[0]
klassContent = klass[1]

props = propP.findall(klassContent)   
funcs = funcP.findall(klassContent)
staticProps = staticPropP.findall(klassContent)

for func in funcs:
	if func[1] == klassName:
		constructor = func[3]
		funcs.remove(func)

str = "";
str += "var " + klass[0] + " = function(){" + constructor + "};"

for prop in staticProps:
    str += "\n" + klassName + "." + prop[0] + " = " + prop[1]

for func in funcs:
    str += "\n" + func[0] + klassName + ".prototype." + func[1] + " = function(){" + func[3] + "}"

print(str)

f = codecs.open(jsPath, "w", "utf-8")
f.write(str)
f.close()   








    
        


