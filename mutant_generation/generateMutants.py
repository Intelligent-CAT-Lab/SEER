import sys
sys.path.append('../')

import os
import pathlib
import random
import json
import ast
from re import T
import utils
from dataset_generation import tuple_gen
import subprocess

d4j_path = str(pathlib.Path.home()/"defects4j")
toi_path = str(pathlib.Path.home()/"defects4j/SEER/mutant_generation")
if os.path.isdir(toi_path+"/syntacticFaultsProjects") == False:
    os.mkdir("syntacticFaultsProjects")

projects_path = str(pathlib.Path.home()/"defects4j/SEER/mutant_generation/syntacticFaultsProjects")
which_modif_class = {}
method_params = {}
method_file_paths = {}


def get_operators(operator_dictionary,project,bug,method):
    try:
        return operator_dictionary[project+"-"+bug+"-"+method]
    except:
        return []
    

def generate_higher_order_mutants(operator_dictionary,project,bug,elem_method,max_order):
    for order in range(2,max_order+2):
        print("Project:",project, "Bug:", bug, "Method:",elem_method)
        print("Mutation order:", order)
        os.chdir(projects_path+"/"+ project + "/" + bug +"/HOM/"+ elem_method+ "/order_"+str(order-1))
        prev_order_mutants = os.listdir(projects_path+"/"+ project + "/" + bug +"/HOM/"+ elem_method+ "/order_"+str(order-1)) 
        chosen_mutant_list = choose_random_compilable_mutants(prev_order_mutants,1,project,bug,elem_method,order)
        print("Chosen mutant from previous order:",chosen_mutant_list)

        os.chdir(projects_path+"/"+ project + "/" + bug +"/HOM/"+ elem_method+ "/order_"+str(order-1))
        for mutant in prev_order_mutants:
            if mutant not in chosen_mutant_list:
                os.system("rm -rf "+mutant)
    
        operators = get_operators(operator_dictionary,project,bug,elem_method)
        print("Mutation Operators:",operators)
        for chosen_mutant in chosen_mutant_list:
            mutant_path = projects_path+"/"+ project + "/" + bug +"/HOM/"+ elem_method+ "/order_"+str(order-1)+"/"+chosen_mutant
            os.chdir(mutant_path+ "/buggy")
            mutators_path = str(pathlib.Path.home()/"defects4j/SEER/mutation_operators")
            print("Applying mutation to",chosen_mutant, "with operator:", operators[order%len(operators)])
            os.system("defects4j mutation -m "+ mutators_path + "/"+ operators[order%len(operators)]+".txt")
            if os.path.isdir("mutants"):
                filter_mutants_by_methods(method_list,project,bug,order,elem_method)
                related_mutants = os.listdir(mutant_path + "/buggy/mutants")
                print("Related mutants on ", elem_method)
                print(related_mutants)
                for elem in related_mutants:
                    os.system("mv " +mutant_path + "/buggy/mutants/"+elem + " "+ projects_path+"/"+ project + "/" + bug + "/HOM/" + elem_method + "/order_"+str(order))
        print("Order",order,"HOMs are generated")

def create_mutant_folders(project,bug,methodList):
    os.chdir(projects_path+"/"+project+"/"+bug)
    os.mkdir("HOM")
    os.system("cd HOM")
    for elem in methodList:
        os.chdir("HOM")
        if os.path.isdir(elem) == False:
            os.mkdir(elem)
            os.chdir(elem)
            for i in range(1,6):
                os.mkdir("order_"+str(i))
            os.chdir("..")
        os.chdir("..")

def does_match(param_list,line):
    flag = True
    param_list = param_list[1:len(param_list)-1]
    param_list = param_list.split(",")

    if param_list== [''] and line == "()":
        flag = True
    else:
        for elem in param_list:
            if param_list.count(elem) != line.count(elem):
                flag = False
                break
    return flag

def does_match_any_method(methodList, line):
    does_match = False
    line = line.strip()
    for method in methodList:
        flag = True
        param_list = method_params[method]
        param_list = param_list[1:len(param_list)-1]
        param_list = param_list.split(",")
        if param_list== [''] and line == "()":
            flag = True
        else:
            for elem in param_list:
                if param_list.count(elem) != line.count(elem):
                    flag = False
                    break
        if flag == True:
            does_match = True
            break

    return does_match


def filter_mutants_by_methods(methodList,project,bug,order,currentMethod):
    #checks the mutants.log file and removes mutants if changes not in methods appear in diff.
    with open("mutants.log") as logFile:
        for line in logFile:
            
            pos = line.index(":")
            mutant = line[0:pos]
            if "@" not in line:
                os.chdir("mutants")
                os.system("rm -rf " + mutant)
                os.chdir("..")
            else:
                start = line.index("@")
                method= ""
                for i in range(start+1, len(line)):
                    if line[i] == "(":
                        break
                    else:
                        method+=line[i]
                if order ==1:
                    if method not in methodList or does_match_any_method(methodList, line[line.index("("):line.index(")")+1]) == False:
                        os.chdir("mutants")
                        os.system("rm -rf " + mutant)
                        os.chdir("..")
                    else:
                        os.system("mv " + projects_path+"/"+ project + "/" + bug + "/buggy/mutants/" + mutant+ 
                            " "+ projects_path+"/"+ project + "/" + bug + "/HOM/" + method + "/order_"+str(order))
                else:
                    if method != currentMethod or does_match(method_params[method],line[line.index("("):line.index(")")+1]) == False:
                        os.chdir("mutants")
                        os.system("rm -rf " + mutant)
                        os.chdir("..") 

def create_folders(bug):
    # for each bug in the project, create a dir and checkout buggy version inside that dir.
    os.mkdir(bug)
    os.chdir(bug)
    if os.path.isdir(projects_path + "/"+ project+"/"+bug+"/buggy") == False:
        os.system("defects4j checkout -p " + project + " -v " + bug+ "b -w ./buggy")
    if os.path.isdir(projects_path + "/"+ project+"/"+bug+"/randoop_tests") == False:
         os.mkdir("randoop_tests")

    os.chdir("..")

def restore_buggy_folder(project,bug):
    os.chdir(projects_path+"/"+ project + "/" + bug + "/buggy")
    os.system("rm -rf mutants")
    os.system("rm -rf target")
    # os.system("rm mutants.log")

def delete_previous_orders(project,bug,method,max_order):
    path_to_orders = (projects_path+"/"+ project + "/" + bug + "/HOM/"+method)
    for order in range(1,max_order):
        os.system("rm -rf "+path_to_orders+"/order_"+str(order))

def check_compile(mutant_buggy_path):
    os.chdir(mutant_buggy_path)
    print("Checking compilation")
    output = subprocess.run(["defects4j","compile"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = output.stderr.decode("utf-8")
    num = output.count("... OK")
    print("Compilation output:")
    print(output)
    if num ==2:
        print("Compile checked")
        return True
    else:
        print("Cannot compile mutant")
        return False
  

def choose_random_compilable_mutants(mutant_list,n,project,bug, method,order):
    chosen = 0
    chosen_list = []
    tried_list = []
    modif_class = which_modif_class[method]
    while chosen < n:
        if len(mutant_list)>1:
            num = random.randint(0,len(mutant_list)-1)
        elif len(mutant_list) == 1:
            num = 0
        else:
            print("Method cannot be mutated in previous order.")
            break
        if mutant_list[num] not in tried_list:
            tried_list.append(mutant_list[num])
        else:
            continue
        path_to_mutants = projects_path +"/"+project+"/"+bug+"/HOM/"+method+"/order_"+str(order-1)
        os.chdir(path_to_mutants+"/"+mutant_list[num])
        os.system("defects4j checkout -p " + project + " -v " + bug+ "b -w ./buggy")
        
        modif_file= toi_path+ "/projects/"+project+"/"+bug+"/output/modified_classes/modified.txt"
        with open(modif_file, "r", encoding="ISO-8859-1",errors="ignore") as f:
            for line in f.readlines():
                line = line.strip()
                posDot = line.rindex(".")
                className = line[posDot+1:]
                if className == modif_class:
                    modif_class_path = line[:posDot].replace(".","/")
                    break

        path_mutant_file = path_to_mutants+"/"+mutant_list[num] +"/" +modif_class_path+"/"+modif_class+".java"
       
        os.system("find " + path_to_mutants+"/"+mutant_list[num] + "/buggy -name " + "'" + modif_class+".java"+ "'" + " > tf.txt")
        with open("tf.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
            found_path = f.readlines()
            for line in found_path:
                line = line.strip()
                pos = line.rindex("/")
                to_be_deleted = line[:pos]

        os.chdir(to_be_deleted)
        os.system("rm " + modif_class+".java")
        os.system("cp "+ path_mutant_file+" "+to_be_deleted)
        os.chdir(path_to_mutants+"/"+mutant_list[num])

        dirList = os.listdir(path_to_mutants+"/"+mutant_list[num])
        for elem in dirList:
            if elem != "buggy":
                os.system("rm -rf "+elem)
        mutant_buggy_path = path_to_mutants+"/"+mutant_list[num] + "/buggy"
        if check_compile(mutant_buggy_path) and mutant_list[num] not in chosen_list:
            chosen_list.append(mutant_list[num])
            chosen+=1
        if len(tried_list) == len(mutant_list):
            print("Not enough compilable mutants. Chosen mutants are only", chosen_list)
            break
    return chosen_list

def get_test_body(project,bug,test):
    test_body = ""
    os.chdir(toi_path + "/projects/"+ project+"/"+bug+"/output/relevant_tests")
    test_file = toi_path + "/projects/"+ project+"/"+bug+"/output/relevant_tests/"+ test+ ".txt"
    if os.path.isfile(test_file):
        with open(test_file, "r",encoding="ISO-8859-1",errors="ignore") as f:
            test_body = f.read()
    return test_body

def get_randoop_test_body(project,bug,test):
    os.chdir(toi_path + "/randoop_test_methods/"+ project+"/"+bug+"/randoop_tests")
    test_file = test +".txt"
    with open(test_file, "r",encoding="ISO-8859-1",errors="ignore") as f:
        test_body = f.read()
    return test_body

def extract_randoop_test_methods(project,bug,modif_class_path):
    os.chdir(modif_class_path)
    with open("modified.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
        randoop_path = f.readlines()[0]
        position_name = randoop_path.rindex(".")
        randoop_path = randoop_path[:position_name].replace(".","/")
    project_path = toi_path + "/randoop_test_methods/"+ project
    randoop = toi_path + "/randoop_test_methods/"+ project+"/"+bug
    all_randoop_tests = []
    if os.path.isdir(randoop) ==False:
        if os.path.isdir(project_path) == False:
            os.chdir(toi_path + "/randoop_test_methods")
            os.mkdir(project)
        os.chdir(project_path)
        os.mkdir(bug)
        os.chdir(bug)
        os.mkdir("randoop_tests")
        try:
            randoop_test_files = os.listdir(projects_path+"/"+project+"/"+bug+"/randoop_tests/"+randoop_path)
            os.chdir(projects_path+"/"+project+"/"+bug+"/randoop_tests/"+randoop_path)
            for elem in randoop_test_files:
                try:
                    methodFromEachFile = utils.extract_method_names(projects_path+"/"+project+"/"+bug+"/randoop_tests/"+randoop_path+"/"+elem)
                except:
                    continue
                for i in methodFromEachFile:
                    os.chdir(toi_path)
                    try:
                        os.system("python3 javaTestMethodExtractor.py " + projects_path+"/"+project+"/"+bug+"/randoop_tests/"+randoop_path+ "/"+elem + " "+i + " "+ d4j_path + "/SEER/randoop_test_methods"+"/"+project+"/"+bug+"/randoop_tests/"+i+".txt")
                        all_randoop_tests.append(i)
                    except:
                        continue
        except:
            pass
    else:
        temp= os.listdir(toi_path + "/randoop_test_methods/"+ project+"/"+bug+"/randoop_tests")
        for elem in temp:
            if elem != "org":
                all_randoop_tests.append(elem[:len(elem)-4])
    return all_randoop_tests                

def get_diff_method_body(modif_class_path,method,output_file):
    os.chdir(toi_path)
    path_to_method = method_file_paths[method]

    with open(path_to_method, "r",encoding="ISO-8859-1",errors="ignore") as f:
        modif_method = f.read()
        signature = modif_method[:modif_method.index(")")+1]
        signature_to_be_searched = ""
        for line in signature.splitlines():
            line = line.strip()
            signature_to_be_searched += line + "\n"
        signature_to_be_searched = signature_to_be_searched[:-1]


    modif_class_no_comment = ""
    with open(modif_class_path, "r",encoding="ISO-8859-1",errors="ignore") as f:
        modif_class = f.readlines()
        in_comment = False
        for line in modif_class:
            line = line.strip()
            if line.startswith("//"):
                continue
            if line.startswith("/*") and line.endswith("*/"):
                continue
            if line.startswith("/*") and line.endswith("*/") == False:
                in_comment = True
                continue
            if in_comment == True and line.endswith("*/"):
                in_comment = False
                continue
            if in_comment:
                continue
            if in_comment == False:
                modif_class_no_comment += line + "\n"



    output_string = signature_to_be_searched + "{"

    start_pos_signature = modif_class_no_comment.index(signature_to_be_searched)
    opening_curly = modif_class_no_comment.find("{", start_pos_signature)
    curlyCount = 1

    inString = False

    for index in range(opening_curly+1, len(modif_class_no_comment)):
        if curlyCount == 0:
            break
        char = modif_class_no_comment[index]
        if inString == False and char == "{":
            curlyCount +=1
        elif inString == False and char == "}":
            curlyCount -=1
        elif char == '"' and inString == False:
            inString = True
        elif char == '"' and inString==True:
            inString = False
        output_string+=char

    f = open(output_file, "w")
    f.write(output_string)
    f.close()
    return output_string

def generate_tuples(tuples,triplets,project,bug,fc,test_file,randoop_file,all_relevant_tests,all_randoop_tests,num_tuple,num_fc,mutant_path):
    failing_dev_tests= []
    failing_randoop_tests= []
    os.chdir(mutant_path+"/buggy")
    flag = False
    try:
        with open(test_file, "r",encoding="ISO-8859-1",errors="ignore") as f:
            lines = f.readlines()
            counter = 0
            for line in lines:
                if counter == 0:
                    counter+=1
                else:
                    line = line.strip()
                    line = line.replace("$","\$")
                    try:
                        pos = line.rindex(":")
                    except ValueError:
                        continue
                    test = line[pos+1:len(line)]
                    failing_dev_tests.append(test)
                    test_code = get_test_body(project,bug,test)
                    if test_code != "":
                        tuples[num_tuple] = {"project": project, "bug_id":bug,"code":fc,"test_name":test, "test_code":test_code, "label":"F", "type":"BC"}
                        triplets[num_tuple] = {"code":fc, "test_code":test_code, "label":"F"}
                        num_tuple+=1
    except:
        flag = True
        pass
                
    os.chdir(mutant_path+"/buggy")
    try:
        with open(randoop_file, "r",encoding="ISO-8859-1",errors="ignore") as f:
            lines = f.readlines()
            counter = 0
            for line in lines:
                if counter == 0:
                    counter+=1
                else:
                    line = line.strip()
                    line = line.replace("$","\$")
                    try:
                        pos = line.rindex(":")
                    except ValueError:
                        continue
                    test = line[pos+1:len(line)]
                    failing_randoop_tests.append(test)
                    test_code = get_randoop_test_body(project,bug,test)
                    if test_code != "":
                        tuples[num_tuple] = {"project": project, "bug_id":bug,"code":fc,"test_name":test, "test_code":test_code, "label":"F", "type":"BC"}
                        triplets[num_tuple] = {"code":fc, "test_code":test_code, "label":"F"}
                        num_tuple+=1
    except:
        pass
    
    if flag != True:
        for test in all_relevant_tests:
            if test not in failing_dev_tests:
                test_code = get_test_body(project,bug,test)
                tuples[num_tuple] = {"project": project, "bug_id":bug,"code":fc,"test_name":test, "test_code":test_code, "label":"P", "type":"BC"}
                triplets[num_tuple] = {"code":fc, "test_code":test_code, "label":"P"}
                num_tuple+=1
        if len(all_randoop_tests) != 0:
            samplePassingRandoop = 0
            while samplePassingRandoop <30:
                num = random.randint(0,len(all_randoop_tests)-1)
                chosen = all_randoop_tests[num]
                if chosen not in failing_randoop_tests:
                    test_code = get_randoop_test_body(project,bug,chosen)
                    tuples[num_tuple] = {"project": project, "bug_id":bug,"code":fc,"test_name":chosen, "test_code":test_code, "label":"P", "type":"BC"}
                    triplets[num_tuple] = {"code":fc, "test_code":test_code, "label":"P"}
                    num_tuple+=1
                    samplePassingRandoop+=1
        num_fc +=1
    return [num_fc,num_tuple]

def choose_final_mutants(project,bug,method,max_order):
    print("Starting to choose final mutants")
    os.chdir(projects_path + "/"+project+"/"+bug+"/HOM/"+ method + "/order_"+str(max_order+1))
    all_max_order_mutants = os.listdir(projects_path + "/"+project+"/"+bug+"/HOM/"+ method + "/order_"+str(max_order+1))
    print("All highest order mutants:", all_max_order_mutants)
    chosen = 0
    final_mutants = []
    if len(all_max_order_mutants) <=4:
        final_mutants = all_max_order_mutants
    else:
        final_mutants = random.sample(all_max_order_mutants,4)
  
    for mut in all_max_order_mutants:
        if mut not in final_mutants:
            os.system("rm -rf "+mut)

    print("Final", max_order+1," order mutants are:", final_mutants)

def copy_randoop_test_suite(project,bug,mutant_path):
    randoop_dir= str(pathlib.Path.home()/"defects4j/SEER/defects4j_randoop_tests")
    copy_to = mutant_path + "/buggy"
    if os.path.isdir(randoop_dir + "/" + project+"_randoop/"+project+"/randoop/"+bug):
        os.chdir(randoop_dir + "/" + project+"_randoop/"+project+"/randoop/"+bug)
        test = project+"-"+bug+"f-randoop."+bug+".tar.bz2"
        os.system("cp "+ test +" "+ copy_to)

def extract_randoop_tests(project,bug):
    os.chdir(projects_path+"/"+project+"/"+bug+"/randoop_tests")
    randoop_dir= str(pathlib.Path.home()/"defects4j/SEER/defects4j_randoop_tests")
    archive = randoop_dir + "/" + project+"_randoop/"+project+"/randoop/"+bug +"/"+project+"-"+bug+"f-randoop."+bug+".tar.bz2"
    if os.path.isfile(archive):
        os.system("tar -xf "+ archive)
        return True
    return False

def create_result_files(project, tuples,triplets):
    os.chdir(projects_path+ "/"+project)
    with open("tuples.json","w") as m:
        m.write(json.dumps(tuples, indent = 4))
    with open("triplets.json","w") as m:
        m.write(json.dumps(triplets, indent = 4))

    items = os.listdir(projects_path+ "/"+project)
    for item in items:
        if item != "tuples.json" and item != "triplets.json":
            os.system("rm -rf "+ item)

def get_diff_methods(modified_classes):
    method_list = []
    for modified_class in modified_classes:
        path = toi_path+ "/projects/" + project+ "/" +bug + "/output/modified_classes/" + modified_class+ "/foundMethods.txt"
        with open(path, "r", encoding="ISO-8859-1", errors='ignore') as f:
            mList = f.readlines()
            mList = list(map(lambda x: x.strip(), mList))
            line = 0
            for elem in mList:
                which_modif_class[elem] = modified_class
                path_to_file = toi_path+ "/projects/" + project+ "/" +bug + "/output/modified_classes/" + modified_class+"/"+str(line)+".txt"
                line +=1
                param_list = get_method_param_list(path_to_file)
                method_params[elem] = param_list
                method_file_paths[elem] = path_to_file
                method_list.append(elem)
    return method_list  

def get_relevant_tests(project,bug):
    all_relevant_tests = []
    temp_list = os.listdir(toi_path + "/projects/"+ project+"/"+bug+"/output/relevant_tests")
    for elem in temp_list:
        all_relevant_tests.append(elem[:len(elem)-4])
    return all_relevant_tests 

def removeDuplicates(method_list):
    temp = []
    for elem in method_list:
        if elem not in temp:
            temp.append(elem)
    return temp



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

#MAIN PROGRAM STARTS HERE

projects = ["Chart", "Cli", "Closure", "Codec", "Compress", "Csv", "Gson", 
            "JacksonCore", "JacksonDatabind", "JacksonXml", "Jsoup", "JxPath", 
            "Lang", "Math", "Time"]
os.chdir(toi_path)

for project in projects:
    file = open(f"{project}-mutators.txt","r")
    contents = file.read()
    operator_dictionary = ast.literal_eval(contents)
    os.chdir(projects_path)

    if os.path.isdir(projects_path + "/"+ project) == False:
        os.mkdir(project)
    os.chdir(project)
    tuples = {}
    triplets = {}
    num_fc = 1
    num_tuple =1
    os.chdir(toi_path)
    bugList = tuple_gen.export_project_bugs(project)

    for bug in bugList:
        os.chdir(projects_path+"/"+project)
        if os.path.isdir(projects_path+"/"+project+"/"+bug) == False:
            create_folders(bug)
            all_relevant_tests = get_relevant_tests(project,bug)
            doesRandoopExists = extract_randoop_tests(project,bug)
            os.chdir(projects_path+"/"+project+"/"+bug)
            mcp= toi_path+ "/projects/"+project+"/"+bug+"/output/modified_classes"
            modified_classes=os.listdir(mcp)
            modified_classes.remove("modified.txt")
            os.chdir(projects_path+"/"+project+"/"+bug)
            method_list=get_diff_methods(modified_classes)
            method_list = removeDuplicates(method_list)
            for elem in method_list:
                if len(elem) == 0:
                    method_list.remove(elem)
            os.chdir(projects_path+"/"+ project + "/" + bug)
            create_mutant_folders(project,bug,method_list)
            os.chdir(projects_path+"/"+ project + "/" + bug + "/buggy")
            print("First mutation for ", project, bug)
            os.system("defects4j mutation")

            filter_mutants_by_methods(method_list,project,bug,1,"dummy_param")
            restore_buggy_folder(project,bug)

            for diff_method in method_list:
                try:
                    max_order = len(get_operators(operator_dictionary,project,bug,diff_method))
                except:
                    continue
                if  max_order ==0:
                    print("Skipping",project, bug, diff_method, "because it is not mutable")
                    continue
                os.chdir(projects_path+"/"+project+"/"+bug)
                if doesRandoopExists:
                    all_randoop_tests = extract_randoop_test_methods(project,bug,mcp)
                else:
                    all_randoop_tests =  []
        
                generate_higher_order_mutants(operator_dictionary,project,bug,diff_method,max_order)
                delete_previous_orders(project,bug,diff_method,max_order)
                choose_final_mutants(project,bug,diff_method,max_order)
                order_max_path = projects_path + "/"+project+"/"+bug+"/HOM/"+ diff_method + "/order_" +str(max_order+1)
                os.chdir(order_max_path)
                final_mutants = os.listdir(order_max_path)

                for final_mutant in final_mutants:
                    mutant_path = order_max_path+"/"+final_mutant
                    os.chdir(mutant_path)
                    os.system("defects4j checkout -p " + project + " -v " + bug+ "b -w ./buggy")
                    modif_file= toi_path+ "/projects/"+project+"/"+bug+"/output/modified_classes/modified.txt"
                    modified_class = which_modif_class[diff_method]
                    with open(modif_file, "r", encoding="ISO-8859-1",errors="ignore") as f:
                        for line in f.readlines():
                            line = line.strip()
                            posDot = line.rindex(".")
                            className = line[posDot+1:]
                            if className == modified_class:
                                modif_class_path = line[:posDot].replace(".","/")
                                break

                    path_mutant_file = mutant_path + "/"+modif_class_path + "/"+ modified_class+".java"
                    os.system("find " + mutant_path+ "/buggy -name " + "'" + modified_class+".java"+ "'" + " > tf.txt")
                    with open("tf.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
                        found_path = f.readlines()
                        for line in found_path:
                            line = line.strip()
                            pos = line.rindex("/")
                        to_be_deleted= line[:pos]

                    os.chdir(to_be_deleted)
                    os.system("rm " + to_be_deleted+"/"+modified_class+".java")
                    os.system("cp "+ path_mutant_file+" "+to_be_deleted)
                    os.chdir(mutant_path)
                    dir_list = os.listdir(mutant_path)
                    for elem in dir_list:
                        if elem != "buggy":
                            os.system("rm -rf "+elem)
                    if check_compile(mutant_path+"/buggy") == False:
                        continue
                    print("Testing final mutant:", final_mutant)
                
                    return_status = os.system("timeout -s SIGKILL --preserve-status 7m defects4j test > ./test_results.txt")
                    with open("test_results.txt", "r", encoding="ISO-8859-1",errors="ignore") as f:
                            status = f.read()
                    if len(status) == 0:
                        print("Process is killed for", final_mutant)
                        os.chdir("..")
                        os.system("rm -rf "+final_mutant)
                        continue
                    else:
                        if doesRandoopExists:
                            copy_randoop_test_suite(project,bug,mutant_path)
                            os.chdir(mutant_path)
                            os.chdir("./buggy")
                            randoop_status = os.system("timeout -s SIGKILL --preserve-status 10m defects4j test -s " +project+"-"+  bug+"f-randoop."+bug+".tar.bz2"+ ">./randoop_results.txt")
                        else:
                            os.chdir(mutant_path)
                            os.chdir("./buggy")
                            os.system(">./randoop_results.txt")
                        output_file = mutant_path + "/buggy/"+ diff_method+".txt"
                        fc = get_diff_method_body(to_be_deleted+"/"+modified_class+".java",diff_method,output_file)
                        old_num_tuple = num_tuple
                        old_num_fc = num_fc
                        updateNums = generate_tuples(tuples,triplets,project,bug,fc,"test_results.txt","randoop_results.txt",all_relevant_tests,all_randoop_tests, old_num_tuple,old_num_fc,mutant_path)
                        num_tuple = updateNums[1]
                        num_fc = updateNums[0]
        else:
            method_list = os.listdir(projects_path + "/" + project + "/" + bug + "/HOM")
            flag = False
            for elem in method_list:
                max_order = len(get_operators(operator_dictionary,project,bug,elem))
                if max_order != 0:
                    flag = True
                    break
            if flag == False:
                print("Skipping",project, bug, "because it is not mutable")
            if flag:
                for method in method_list:
                    order_max_path = projects_path + "/"+project+"/"+bug+"/HOM/"+ method + "/order_" +str(max_order+1)
                    os.chdir(order_max_path)
                    final_mutants = os.listdir(order_max_path)
                    for final_mutant in final_mutants:
                        all_relevant_tests = get_relevant_tests(project,bug)
                        all_randoop_tests = []
                        try:
                            temp = os.listdir(toi_path + "/randoop_test_methods/"+ project+"/"+bug+"/randoop_tests")          
                            for elem in temp:
                                all_randoop_tests.append(elem[:-4])
                        except:
                            pass
                        mutant_path = order_max_path +"/"+ final_mutant
                        os.chdir(mutant_path)
                        try:
                            output_file = mutant_path + "/buggy/"+ method+".txt"
                            with open(output_file, "r", encoding="ISO-8859-1",errors="ignore") as f:
                                fc = f.read()
                        except:
                            continue
                        os.chdir(mutant_path+"/buggy")
                        old_num_tuple = num_tuple
                        old_num_fc = num_fc
                        updateNums = generate_tuples(tuples,triplets,project,bug,fc,"test_results.txt","randoop_results.txt",all_relevant_tests,all_randoop_tests, old_num_tuple,old_num_fc,mutant_path)
                        num_tuple = updateNums[1]
                        num_fc = updateNums[0]
                    
    create_result_files(project, tuples,triplets)
