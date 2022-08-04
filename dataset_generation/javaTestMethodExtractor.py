import sys
sys.path.append('../')

import os
import utils

#python3 javaMethodExtractor.py JacksonXml 1 com.fasterxml.jackson.dataformat.xml.lists.NestedUnwrappedListsTest testNestedWithEmpty2 deneme.txt
#python3 javaMethodExtractor.py commonProjectName pathToFileWithDots methodNameInsideFileWeWantToExtract outputFileName

location = sys.argv[1]
methodName = sys.argv[2]
outputFile = sys.argv[3]

location = location.replace("$","\$")
os.system("cp " + location + " " + outputFile)

with open(outputFile, "r", encoding="ISO-8859-1", errors='ignore') as f:
    javaFile = f.readlines()

lineNumber = 0
isInComment = False
for i in range(len(javaFile)):
    line = javaFile[i].strip()
    if line.startswith("//"):
        lineNumber+=1
        continue 

    if line.startswith("/*") and line.endswith("*/"):
        lineNumber += 1
        continue

    if line.startswith("/*"):
        isInComment = True
        lineNumber+=1
        continue

    if line.endswith("*/") and isInComment:
        isInComment = False
        lineNumber+=1
        continue

    if isInComment:
        lineNumber+=1
        continue

    st = i + 1
    while True:
        res = utils.is_method_sig_format(line)
        if res == 1 or res == 2:
            break
        elif res == 3:
            line = line + " " + javaFile[st].strip()
            st += 1
            continue

    if line.find(methodName + "(") != -1 and utils.is_method_sig(line):
        break
    lineNumber+=1


outputString = ""

curlyCount = 0
finishFlag = 0
javaFile = javaFile[lineNumber:]

for line in javaFile:
    
    inString = False
    
    for index, char in enumerate(line):
        outputString += char

        if index + 1 < len(line):
            if line[index-1] == "'" and line[index] == "{" and line[index+1] == "'":
                curlyCount -= 1
            elif line[index-1] == "'" and line[index] == "}" and line[index+1] == "'":
                curlyCount += 1
            elif line[index-1] == "'" and line[index] == '"' and line[index+1] == "'":
                continue

        if index - 1 > 0:
            if line[index-1] == "\\" and line[index] == '"':
                continue

        #to avoid counting curly brackets inside a string or character.
        if char == '"' and inString == False:
            inString = True
        elif char == '"' and inString==True:
            inString = False

        elif char == "{" and inString==False:
            curlyCount +=1
        elif char == "}" and curlyCount == 1 and inString==False:
            finishFlag = 1
            break
        elif char == "}" and curlyCount != 1 and inString==False:
            curlyCount -=1

    outputString += "\n" ##Delete this if we want to make it one line
    if finishFlag == 1:
        break

f = open(outputFile, "w")
f.write(outputString)
f.close()

print("Test Method Extracted")
