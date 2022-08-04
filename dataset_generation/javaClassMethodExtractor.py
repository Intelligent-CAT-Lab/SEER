import sys
sys.path.append("../")

import os
import utils

fixedLocation = sys.argv[1]
buggyLocation = sys.argv[2]
outputLocation = sys.argv[3]
funcNumber = 0
foundMethods = []

def extract_method(src_code):
    method = ""
    curlyCount = 0
    
    inString = False
    
    for index, char in enumerate(src_code):
        method += char
        
        if index + 1 < len(src_code):
            if src_code[index-1] == "'" and src_code[index] == "{" and src_code[index+1] == "'":
                curlyCount -= 1
            elif src_code[index-1] == "'" and src_code[index] == "}" and src_code[index+1] == "'":
                curlyCount += 1
            elif src_code[index-1] == "'" and src_code[index] == '"' and src_code[index+1] == "'":
                continue

        if index - 1 > 0:
            if src_code[index-1] == "\\" and src_code[index] == '"':
                continue

        #to avoid counting curly brackets inside a string or character.
        if char == '"' and inString == False:
            inString = True
        elif char == '"' and inString==True:
            inString = False

        elif char == "{" and inString==False:
            curlyCount +=1
        elif char == "}" and curlyCount == 1 and inString==False:
            break
        elif char == "}" and curlyCount != 1 and inString==False:
            curlyCount -=1

    return method

def processAdd(lineNum, diffFile):
    global funcNumber
    global foundMethods

    line = diffFile[lineNum]
    old, new = line.split("a")
    startIndex = list(map(int,new.split(",")))[0] -1
    st = startIndex
    lineNum+=1

    isThereMethod = False 

    while lineNum < len(diffFile):
        line = diffFile[lineNum]

        if line[0] != ">":
            break
        
        line = line[1:].strip()
        if utils.is_method_sig(line):
            isThereMethod = True
            break
        
        lineNum+=1
        st+=1

    if isThereMethod and utils.extract_method_name(diffFile[lineNum]) not in foundMethods:
        methodName = utils.extract_method_name(diffFile[lineNum])
        src_code = "".join(fixedFile[st:])
        method = extract_method(src_code)

        
        f = open(outputLocation + str(funcNumber) + str(funcNumber) + ".txt", "w") #fixed classes 00.txt
        f.write(method)
        f.close()

        f = open(outputLocation + str(funcNumber) + ".txt", "w") # since not existing method empty file and 0.txt 
        f.write("")
        f.close()
        funcNumber+=1
        foundMethods.append(methodName)

    else:
        isThereMethod = False
        found_method_sig_fixed = ''
        while startIndex >= 0:
            line = fixedFile[startIndex].strip()

            st = startIndex
            while True:
                res = utils.is_method_sig_format(line)
                if res == 1 or res == 2:
                    break
                elif res == 3:
                    line = line + " " + fixedFile[st].strip()
                    st += 1
                    continue

            if utils.is_method_sig(line):
                found_method_sig_fixed = line
                isThereMethod = True
                break
            
            startIndex-=1

        if isThereMethod  and startIndex != -1 and utils.extract_method_name(found_method_sig_fixed) not in foundMethods:
            methodName = utils.extract_method_name(found_method_sig_fixed)
            src_code = "".join(fixedFile[startIndex:])
            method = extract_method(src_code) 
            f = open(outputLocation + str(funcNumber) + str(funcNumber) + ".txt", "w") #fixed classes 00.txt
            f.write(method)
            f.close()

            found_method_sig_buggy = ''
            old = int(old) -1
            while old >= 0:
                line = buggyFile[old].strip()

                bst = old
                while True:
                    res = utils.is_method_sig_format(line)
                    if res == 1 or res == 2:
                        break
                    elif res == 3:
                        line = line + " " + buggyFile[bst].strip()
                        bst += 1
                        continue

                if utils.is_method_sig(line):
                    found_method_sig_buggy = line
                    break
                    
                old-=1

            methodName = utils.extract_method_name(found_method_sig_buggy)
            src_code = "".join(buggyFile[old:])
            method = extract_method(src_code)

            f = open(outputLocation + str(funcNumber) + ".txt", "w") # since not existing method empty file and 0.txt 
            f.write(method)
            f.close()
            funcNumber+=1
            foundMethods.append(methodName)


    return lineNum
    


def processChange(lineNum, diffFile):
    global foundMethods
    global funcNumber

    line = diffFile[lineNum]
    old, new = line.split("c")
    startIndex = list(map(int, new.split(",")))[0] -1
    buggyStartIndex = list(map(int, old.split(",")))[0] -1

    st = startIndex
    lineNum+=1

    isThereMethod = False 

    while lineNum < len(diffFile):
        line = diffFile[lineNum]

        if line[0] != "<":
            break
        
        line = line[1:].strip()
        if utils.is_method_sig(line):
            isThereMethod = True
            break

        st+=1
        lineNum+=1

    
    if isThereMethod and utils.extract_method_name(diffFile[lineNum]) not in foundMethods:
        methodName = utils.extract_method_name(diffFile[lineNum])
        src_code = "".join(fixedFile[st:])
        method = extract_method(src_code)

        
        f = open(outputLocation + str(funcNumber) + str(funcNumber) + ".txt", "w") #fixed classes 00.txt
        f.write(method)
        f.close()

        f = open(outputLocation + str(funcNumber) + ".txt", "w") # since not existing method empty file and 0.txt 
        f.write("")
        f.close()
        funcNumber+=1
        foundMethods.append(methodName)


    else:
        isThereMethod = False
        found_method_sig_fixed = ''
        while startIndex >= 0:
            line = fixedFile[startIndex].strip()

            st = startIndex
            while True:
                res = utils.is_method_sig_format(line)
                if res == 1 or res == 2:
                    break
                elif res == 3:
                    line = line + " " + fixedFile[st].strip()
                    st += 1
                    continue
                
            if utils.is_method_sig(line):
                found_method_sig_fixed = line
                isThereMethod = True
                break
            
            startIndex-=1

        if isThereMethod and startIndex != -1 and utils.extract_method_name(found_method_sig_fixed) not in foundMethods:
            methodName = utils.extract_method_name(found_method_sig_fixed)
            src_code = "".join(fixedFile[startIndex:])
            method = extract_method(src_code) 
            f = open(outputLocation + str(funcNumber) + str(funcNumber) + ".txt", "w") #fixed classes 00.txt
            f.write(method)
            f.close()

            found_method_sig_buggy = ''
            while buggyStartIndex >= 0:
                line = buggyFile[buggyStartIndex].strip()

                bst = buggyStartIndex
                while True:
                    res = utils.is_method_sig_format(line)
                    if res == 1 or res == 2:
                        break
                    elif res == 3:
                        line = line + " " + buggyFile[bst].strip()
                        bst += 1
                        continue

                if utils.is_method_sig(line):
                    found_method_sig_buggy = line
                    break
                    
                buggyStartIndex-=1

            methodName = utils.extract_method_name(found_method_sig_buggy)
            src_code = "".join(buggyFile[buggyStartIndex:])
            method = extract_method(src_code)

            f = open(outputLocation + str(funcNumber) + ".txt", "w") # since not existing method empty file and 0.txt 
            f.write(method)
            f.close()
            funcNumber+=1
            foundMethods.append(methodName)

    return lineNum

def processDelete(lineNum, diffFile):
    global funcNumber
    global foundMethods

    line = diffFile[lineNum]
    old, new = line.split("d")
    startIndex = list(map(int,old.split(",")))[0] -1
    st = startIndex
    lineNum+=1

    isThereMethod = False 

    while lineNum < len(diffFile):
        line = diffFile[lineNum]

        if line[0] != "<":
            break
        
        line = line[1:].strip()
        if utils.is_method_sig(line):
            isThereMethod = True
            break
        
        lineNum+=1
        st+=1

    if isThereMethod and utils.extract_method_name(diffFile[lineNum]) not in foundMethods:
        methodName = utils.extract_method_name(diffFile[lineNum])
        src_code = "".join(buggyFile[st:])
        method = extract_method(src_code)

        
        f = open(outputLocation + str(funcNumber) + ".txt", "w") #buggy classes 0.txt
        f.write(method)
        f.close()

        f = open(outputLocation + str(funcNumber) + str(funcNumber) + ".txt", "w") # since not existing method empty file and 00.txt 
        f.write("")
        f.close()
        funcNumber+=1
        foundMethods.append(methodName)

    else:
        isThereMethod = False
        found_method_sig_buggy = ''
        while startIndex >= 0:
            line = buggyFile[startIndex].strip()

            st = startIndex
            while True:
                res = utils.is_method_sig_format(line)
                if res == 1 or res == 2:
                    break
                elif res == 3:
                    line = line + " " + buggyFile[st].strip()
                    st += 1
                    continue

            if utils.is_method_sig(line):
                found_method_sig_buggy = line
                isThereMethod = True
                break
            
            startIndex-=1

        if isThereMethod and startIndex != -1 and utils.extract_method_name(found_method_sig_buggy) not in foundMethods:
            methodName = utils.extract_method_name(found_method_sig_buggy)
            src_code = "".join(buggyFile[startIndex:])
            method = extract_method(src_code) 
            f = open(outputLocation + str(funcNumber) + ".txt", "w") #buggy classes 0.txt
            f.write(method)
            f.close()

            new = int(new) -1
            found_method_sig_fixed = ''
            while new >= 0:
                line = fixedFile[new].strip()

                st = new
                while True:
                    res = utils.is_method_sig_format(line)
                    if res == 1 or res == 2:
                        break
                    elif res == 3:
                        line = line + " " + fixedFile[st].strip()
                        st += 1
                        continue

                if utils.is_method_sig(line):
                    found_method_sig_fixed = line
                    break
                    
                new-=1

            methodName = utils.extract_method_name(found_method_sig_fixed)
            src_code = "".join(fixedFile[new:])
            method = extract_method(src_code)

            f = open(outputLocation + str(funcNumber) + str(funcNumber) + ".txt", "w") #00.txt 
            f.write(method)
            f.close()
            funcNumber+=1
            foundMethods.append(methodName)

    return lineNum


buggyLocation = buggyLocation.replace("$","\$")
fixedLocation = fixedLocation.replace("$","\$")
os.system("cp " + buggyLocation + " ./buggy.txt")
os.system("cp " + fixedLocation + " ./fixed.txt")
os.system("diff " + buggyLocation + " " + fixedLocation + " > ./temp.txt")

with open("./temp.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
    diffFile = f.readlines()
    diffFile = list(map(lambda x: x.strip(), diffFile))

with open("./buggy.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
    buggyFile = f.readlines()

with open("./fixed.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
    fixedFile = f.readlines()

lineNum = 0

while lineNum < len(diffFile):
    line = diffFile[lineNum]
    if line[0].isnumeric() and line.find("a") != -1:
        lineNum = processAdd(lineNum, diffFile)
    elif line[0].isnumeric() and line.find("c") != -1:
        lineNum = processChange(lineNum, diffFile)
    elif line[0].isnumeric() and line.find("d") != -1:
        lineNum = processDelete(lineNum, diffFile)
    else:
        lineNum+=1
    
print(funcNumber)

methodsFile = open(outputLocation + "foundMethods.txt", "w")
methodsFile.write("\n".join(foundMethods))
os.system('rm temp.txt buggy.txt fixed.txt')


