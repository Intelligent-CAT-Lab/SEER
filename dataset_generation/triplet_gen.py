import sys
import json
import os

os.system("mkdir bug_ids")
counter = 0
triplets = {}
pr = 'projects'
type_ = sys.argv[1]
project_names = ["Chart", "Cli", "Closure", "Codec", "Collections", "Compress", "Csv", 
                 "Gson", "JacksonCore", "JacksonDatabind", "JacksonXml", "Jsoup", "JxPath", 
                 "Lang", "Math", "Mockito", "Time"]

os.makedirs("./triplets/{}".format(type_), exist_ok=True)

def get_bug_ids(project):
    out_path = "./bug_ids/" + project + ".txt"
    command = "defects4j query -p " + project + " -q bug.id > " + out_path
    os.system(command)
 
    with open(out_path) as f:
        bug_ids = f.readlines()
        bug_ids = list(map(lambda x: x.strip(), bug_ids))

    return bug_ids

def find_fp(project, bug_id):
    buggy_results_location = "./{}/{}/{}/buggy_test_results.txt".format(pr, project, bug_id)
    fixed_results_location = "./{}/{}/{}/fixed_test_results.txt".format(pr, project, bug_id)

    buggy_tests = []
    fixed_tests = []

    try:
        with open(buggy_results_location, "r", encoding="ISO-8859-1", errors='ignore') as f:
            buggy_tests = f.readlines()
            buggy_tests = list(map(lambda x: x.strip(), buggy_tests))[1:]

        with open(fixed_results_location, "r", encoding="ISO-8859-1", errors='ignore') as f:
            fixed_tests = f.readlines()
            fixed_tests = list(map(lambda x: x.strip(), fixed_tests))[1:]
    except FileNotFoundError:
        print(bug_id)

    passing_for_fc = list()
    for test in buggy_tests:
        if test not in fixed_tests:
            passing_for_fc.append(test.split('.')[-1].split('::')[-1])

    return passing_for_fc

def get_modified_classes(project_names, bug_id):
    class_location = "./{}/{}/{}/output/modified_classes/modified.txt".format(pr, project, bug_id)
    modified_classes = []

    try:
        with open(class_location, "r", encoding="ISO-8859-1", errors='ignore') as f:
            modified_classes = f.readlines()
            modified_classes = list(map(lambda x: x.strip().split('.')[-1], modified_classes))
    except FileNotFoundError:
        pass
    return modified_classes

def get_test_bodies(project, bug_id, passing_for_fc):
    test_bodies = list()
    try:
        for test in passing_for_fc:
            txt_location = "./{}/{}/{}/output/failed_BC/{}.txt".format(pr, project, bug_id, test)

            with open(txt_location, "r", encoding="ISO-8859-1", errors='ignore') as f:
                test_body = f.readlines()
                test_body = " ".join(test_body)
                test_bodies.append(test_body)
    except FileNotFoundError:
        pass
    return test_bodies

def get_modified_method_bodies(project, bug_id, modified_class):
    buggy_methods = list()
    fixed_methods = list()

    try:
        folder_location = "./{}/{}/{}/output/modified_classes/{}/".format(pr, project, bug_id, modified_class)
        modified_number = len(os.listdir(folder_location)) // 2

        for i in range(modified_number):
            buggy = folder_location + str(i) + ".txt"
            fixed = folder_location + str(i) + str(i) + ".txt"

            with open(buggy, "r", encoding="ISO-8859-1", errors='ignore') as f:
                buggy_code = f.readlines()
                buggy_code = " ".join(buggy_code)
                buggy_methods.append(buggy_code)
            
            with open(fixed, "r", encoding="ISO-8859-1", errors='ignore') as f:
                fixed_code = f.readlines()
                fixed_code = " ".join(fixed_code)
                fixed_methods.append(fixed_code)
    except FileNotFoundError:
        print(bug_id)

    return buggy_methods, fixed_methods


def add_triplets(project, bug_id):
    global counter
    global triplets

    passing_for_fc = find_fp(project, bug_id) #get names of failing test for bc, passing test for fc as a list
    test_bodies = get_test_bodies(project, bug_id, passing_for_fc) # get all test bodies through a list of strings
    modified_classes = get_modified_classes(project, bug_id) # get modified class names as a list

    for test in test_bodies:
        for modified_class in modified_classes:
            buggy_method_bodies, fixed_method_bodies = get_modified_method_bodies(project, bug_id, modified_class)

            for i in range(len(buggy_method_bodies)):
                buggy_code = buggy_method_bodies[i]
                fixed_code = fixed_method_bodies[i]

                if buggy_code == '' or fixed_code == '':
                    continue

                fixed_code = fixed_code.split('\n')
                fixed_code = list(map(lambda x: x.strip(), fixed_code))
                fixed_code = "\n".join(fixed_code)

                buggy_code = buggy_code.split('\n')
                buggy_code = list(map(lambda x: x.strip(), buggy_code))
                buggy_code = "\n".join(buggy_code)

                with open('fixed_code.txt', 'w') as g:
                    g.write(fixed_code)

                with open('buggy_code.txt', 'w') as h:
                    h.write(buggy_code)

                # process diff
                os.system("diff fixed_code.txt buggy_code.txt > diff.txt")
                # < comes from fixed_code
                # > comes from buggy_code
                with open("diff.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
                    diff = f.readlines()
                    diff = list(map(lambda x: x.strip(), diff))

                cp_diff, cm_diff = list(), list()

                index = 0
                while index < len(diff):
                    line = diff[index]
                    #if there is change
                    curr_cp_diff, curr_cm_diff = str(), str()
                    if line.find('c') != -1:
                        index+=1

                        while index < len(diff):
                            line = diff[index]
                            if line[0] == '<':
                                curr_cp_diff+= line[1:].strip() + " "
                                index+=1

                            elif line[0] == '>':
                                curr_cm_diff+= line[1:].strip() + " "
                                index+=1

                            elif line[0] == '-':
                                index+=1
                            else:
                                break
                        

                    elif line.find('a') != -1:
                        index+=1

                        while index < len(diff):
                            line = diff[index]
                            if line[0] == '>':
                                curr_cm_diff+= line[1:].strip() + " "
                                index+=1
                            else:
                                break
                        
                    elif line.find('d') != -1:
                        index+=1

                        while index < len(diff):
                            line = diff[index]
                            if line[0] == '<':
                                curr_cp_diff+= line[1:].strip() + " "
                                index+=1
                            else:
                                break
                    else:
                        index+=1

                    if (curr_cp_diff == '' and curr_cm_diff == '') or ("".join(curr_cp_diff.split()) == "".join(curr_cm_diff.split())):
                        continue

                    cp_diff.append(curr_cp_diff)
                    cm_diff.append(curr_cm_diff)
                
                triplets[counter] = dict()
                triplets[counter]['bug_id'] = bug_id
                triplets[counter]['T'] = test
                triplets[counter]['C+'] = fixed_code
                triplets[counter]['C-'] = buggy_code
                triplets[counter]['diff_C+'] = cp_diff
                triplets[counter]['diff_C-'] = cm_diff 
                triplets[counter]['project'] = project
                triplets[counter]['dataset'] = 'Real Faults' if type_ in ['fcbc_dev', 'fcbc_randoop'] else 'Syntactic Faults'
                counter+=1

                os.system("rm diff.txt buggy_code.txt fixed_code.txt")


for project in project_names:
    triplets = dict()
    counter = 0
    bug_ids = get_bug_ids(project)
    for bug_id in bug_ids:
        add_triplets(project, bug_id)

    triplets = json.dumps(triplets, indent = 3)
    with open("./triplets/{}/{}_{}.json".format(type_, project, type_), "w") as out_f:
        out_f.write(triplets)

os.system("rm -rf bug_ids")
