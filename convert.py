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

#                        package   org.pkg   {       class   className{        }}
klassP =  re.compile('package\s+[\w\.]+\s+{[\s\S]*class\s+(\w+)\s+{([\s\S]+)}\s*}', re.S)

#                       private                     var    a       :  int
propP =  re.compile('(?:private|protected|public|internal)\s+var\s+(\w+)\s*:\s*(\w+)', re.S)

#                       private                     function    func    (    )   :    int    {         }  
funcP =  re.compile('(?:private|protected|public)\s+function\s+(\w+)\s*\(\s*\)\s*(?::\s*(\w+))?\s*{([\s\S]*?)}', re.S)

staticPropP = re.compile('static\s+(?:private|protected|public|internal)\s+var\s+(\w+)\s*:\s*(\w+)', re.S)

noteP = re.compile('\*\*([\t\n][\s\S]+?)\*/', re.S)


klass = klassP.findall(text)[0]
klassName = klass[0]
klassContent = klass[1]

props = propP.findall(klassContent)   
funcs = funcP.findall(klassContent)
staticProps = staticPropP.findall(klassContent)

str = "";

str += "var " + klass[0] + " = function(){};"

for prop in staticProps:
    str += "\n" + klassName + "." + prop[0] + " = " + prop[1]

for func in funcs:
    str += "\n" + klassName + ".prototype." + func[0] + " = function(){" + func[2] + "}"

print(str)

f = codecs.open(jsPath, "w", "utf-8")
f.write(str)
f.close()   








    
        


