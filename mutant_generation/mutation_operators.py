import os
import pathlib
import json

repo_path = str(pathlib.Path.home()/"defects4j/SEER/mutant_generation")

projects = ["Chart", "Cli", "Closure", "Codec", "Compress", "Csv", "Gson", 
            "JacksonCore", "JacksonDatabind", "JacksonXml", "Jsoup", "JxPath", 
            "Lang", "Math", "Time"]

def get_method_param_list(method_file):
    with open(method_file, "r", encoding="ISO-8859-1",errors="ignore") as f:
        method_body = f.read()
        try:
            open_param = method_body.index("(")
            close_param = method_body.index(")")
            param_list = method_body[open_param+1:close_param]
            if len(param_list) == 0:
                return "()"
            param_str = "("
            param_pairs = param_list.split(",")


            for i in range (len(param_pairs)):
                each_pair = param_pairs[i].split(" ")
                actual_pair =[]
                for elem in each_pair:
                    actual_elem = ""
                    for ch in elem:
                        if ch  != "\t"  and ch  != "\n"  and ch != " ":
                            actual_elem += ch
                    if len(actual_elem) >0:
                        actual_pair.append(actual_elem)
                param_str += actual_pair[0] + ","
            
            param_str = param_str[:len(param_str)-1] +")"

            return param_str
        except:
            return ""


def get_diff_methods(project_name, bug_id, class_name): 
    path = repo_path+ "/projects/" + project_name + "/" + str(bug_id) + "/output/modified_classes/" + class_name + "/foundMethods.txt"

    try:
        with open(path, "r", encoding="ISO-8859-1", errors='ignore') as f:
            found_methods = f.readlines()
            found_methods = list(map(lambda x: x.strip(), found_methods))

        return found_methods
        
    except FileNotFoundError:
        print("File is not available for", class_name)
        return []


def get_modified_classes(project_name, bug_id): 
    os.system("defects4j export -p classes.modified -w "+repo_path+ "/syntacticFaultsProjects/" + project_name + "/buggy" + str(bug_id) +" -o modified_classes.txt")
    with open("modified_classes.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
        modified_classes = f.readlines()
        modified_classes = list(map(lambda x: x.strip(), modified_classes))

    os.remove("modified_classes.txt")
    return modified_classes


def doesMatch(param_list,line):
    flag = True
    param_list = param_list[1:len(param_list)-1]
    param_list = param_list.split(",")

    if param_list== [''] and line == "()":
        return flag
   
    for elem in param_list:
        if param_list.count(elem) != line.count(elem):
            flag = False
            break
   
    return flag

os.chdir(repo_path)
os.mkdir("syntacticFaultsProjects")
projects_path = repo_path + "/syntacticFaultsProjects/"

operatorDictionary = {}

for project_name in projects:
    os.chdir(projects_path)
    print("Project:", project_name)
    os.mkdir(project_name) # created folder for the specific project
    os.chdir(projects_path + project_name)
    os.system("defects4j query -p " + project_name + " -q bug.id -o Bug_IDs.txt") #./syntacticFaultsProjects/Codec/Bug_IDs.txt

    with open("Bug_IDs.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
        bug_ids = f.readlines()
        bug_ids = list(map(lambda x: x.strip(), bug_ids))

    for bug_id in bug_ids:
        os.chdir(projects_path + project_name)

        checkout_path = projects_path + project_name + "/buggy" + str(bug_id) #./syntacticFaultsProjects/Codec/fixed1/
        os.system("defects4j checkout -p " + project_name + " -v " + bug_id + "b -w " + checkout_path)
        os.system("defects4j mutation -w " + checkout_path)
        os.chdir("buggy"+bug_id)

        modified_classes = get_modified_classes(project_name, bug_id)
        for class_name in modified_classes:
            class_name = class_name.split(".")[-1]
            diff_methods = get_diff_methods(project_name, bug_id, class_name) 

            for i in range (len(diff_methods)):
                method_name = diff_methods[i]
                method_file = repo_path +"/projects/" +project_name + "/"+ str(bug_id)+ "/output/modified_classes/"+class_name + "/" + str(i)+".txt"
                param_list = get_method_param_list(method_file)
                method_signature = method_name + param_list
                if method_signature == method_name:
                    continue
                print("Method Signature:",method_signature)
                print("")
                operatorDictionary[project_name + "-" + bug_id + "-" + method_name] = []
                mutantsLog_path = checkout_path + "/mutants.log"

                with open(mutantsLog_path, "r", encoding="ISO-8859-1", errors='ignore') as f:
                    for line in f.readlines():
                        line = line.strip()
                        pos = line.index(":")
                        mutant = line[0:pos]
                        if "@" not in line:
                            continue
                        else:
                            start = line.index("(")
                            method_params = ""
                            for i in range(start, len(line)):
                                if line[i] == ")":
                                    method_params+= line[i]
                                    break
                                else:
                                    method_params+= line[i]

                        if method_name in line and doesMatch(param_list,method_params) and len(param_list.split(",")) == len(method_params.split(",")):
                            line = line[pos+1:]  
                            pos = line.index(":")
                            oper = line[0:pos]
                            if oper not in operatorDictionary[project_name + "-" + bug_id + "-" + method_name]:
                                operatorDictionary[project_name + "-" + bug_id + "-" + method_name].append(oper) 

    os.chdir(repo_path)
    with open(f"{project_name}-mutators.txt","w") as m:
        m.write(json.dumps(operatorDictionary, indent = 4))

os.system("rm -rf syntacticFaultsProjects")
