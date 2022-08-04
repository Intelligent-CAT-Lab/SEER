import sys
sys.path.append('../')

import argparse
import os
import shutil
import json
import random
import configs
import utils


def generate_tuples(args):
    config = configs.configs()
    projects = config['projects']

    if args.project_name != 'all':
        projects = [args.project_name]

    os.system("mkdir projects bug_ids")

    for project in projects:
        bug_ids = export_project_bugs(project)
        export_data_tuples(project, bug_ids, args.randoop_tests)
    
    os.system('rm -rf bug_ids')


def export_project_bugs(project):
    out_path = "./bug_ids/" + project + ".txt"
    command = "defects4j query -p " + project + " -q bug.id > " + out_path
    os.system(command)
 
    with open(out_path) as f:
        bug_ids = f.readlines()
        bug_ids = list(map(lambda x: x.strip(), bug_ids))

    return bug_ids


def export_data_tuples(project, bug_ids, randoop_available):
    os.system("mkdir ./projects/" + project)   # i.e., ./projects/Lang

    for bug_id in bug_ids:
        create_dirs(project, bug_id)   # create necessary dirs
        checkout_and_compile(project, bug_id)   #checkout and compile the specific bug
        tests = get_test_details(project, bug_id, randoop_available)   # get tests
        if tests == 1:
            remove_dirs(project, bug_id)
            continue
        tests = export_tests(project, bug_id, tests, randoop_available)    # export tests
        modified_classes = get_modified_classes(project, bug_id)   # return list of modified classes
        export_modified_classes(project, bug_id, modified_classes, tests)
        remove_dirs(project, bug_id)
        

def create_dirs(project, bug_id):
    command = "mkdir ./projects/" + project + "/" + bug_id
    os.system(command)   # i.e., ./projects/Lang/1
    os.system(command + "/compile")   # ./projects/Lang/1/compile
    os.system(command + "/output")   # ./projects/Lang/1/output
    os.system(command + "/output/relevant_tests")
    os.system(command + "/output/failed_BC")
    os.system(command + "/output/failed_FC")
    os.system(command + "/output/modified_classes")


def checkout_and_compile(project, bug_id):
    checkout_buggy = "defects4j checkout -p " + project + " -v " + bug_id + "b " + "-w ./projects/" + project + "/" + bug_id + "/compile/buggy"
    checkout_fixed = "defects4j checkout -p " + project + " -v " + bug_id + "f " + "-w ./projects/" + project + "/" + bug_id + "/compile/fixed"

    os.system(checkout_buggy)
    os.system(checkout_fixed)

    buggy_path = "./projects/" + project + "/" + bug_id + "/compile/buggy"
    fixed_path = "./projects/" + project + "/" + bug_id + "/compile/fixed"

    os.system("defects4j compile -w " + buggy_path)
    os.system("defects4j compile -w " + fixed_path)


def get_test_details(project, bug_id, randoop_available):
    randoop_methods = dict()
    buggy_path = "./projects/" + project + "/" + bug_id + "/compile/buggy"
    fixed_path = "./projects/" + project + "/" + bug_id + "/compile/fixed"
    relevant_test_path = ""
    # exporting relevant tests of either the buggy version or fixed version should suffice
    if not randoop_available:
        os.system("defects4j export -p tests.relevant -w " + buggy_path + " > ./projects/" + project + "/" + bug_id + "/relevant_tests.txt")
        os.system("defects4j test -w " + buggy_path + " > ./projects/" + project + "/" + bug_id + "/buggy_test_results.txt")
        os.system("defects4j test -w " + fixed_path + " > ./projects/" + project + "/" + bug_id + "/fixed_test_results.txt")
        relevant_test_path = "./projects/" + project + "/" + bug_id + "/relevant_tests.txt"
    else:
        randoop_test_path = "./defects4j_randoop_tests/{}_randoop/{}/randoop/{}/{}-{}f-randoop.{}.tar.bz2".format(project, project, bug_id, project, bug_id, bug_id)
        os.system("defects4j test -w " + buggy_path + " -s " + randoop_test_path + " > ./projects/" + project + "/" + bug_id + "/buggy_test_results.txt")
        os.system("defects4j test -w " + fixed_path + " -s " + randoop_test_path + " > ./projects/" + project + "/" + bug_id + "/fixed_test_results.txt")

    buggy_test_path = "./projects/" + project + "/" + bug_id + "/buggy_test_results.txt"
    fixed_test_path = "./projects/" + project + "/" + bug_id + "/fixed_test_results.txt"

    # there are some failing tests which also fails on FC
    with open(buggy_test_path, "r", encoding="ISO-8859-1", errors='ignore') as f:
        buggy_tests = f.readlines()[1:]
        buggy_tests = list(map(lambda x: x.strip()[2:], buggy_tests))

    with open(fixed_test_path, "r", encoding="ISO-8859-1", errors='ignore') as f:
        fixed_tests = f.readlines()[1:]
        fixed_tests = list(map(lambda x: x.strip()[2:], fixed_tests))

    if not randoop_available:
        with open(relevant_test_path, "r", encoding="ISO-8859-1", errors='ignore') as f:
            relevant_tests = f.readlines()
            relevant_tests = list(map(lambda x: x.strip(), relevant_tests))
    else:
        if extract_randoop_tests(project, bug_id):
            try:
                class_path = "/".join(get_modified_classes(project, bug_id)[0].split(".")[:-1])
                regression_folder = "./defects4j_randoop_tests/{}_randoop/{}/randoop/{}/{}".format(project, project, bug_id, class_path)
                regression_files = os.listdir(regression_folder)


                for file_name in regression_files:
                    if file_name != "RegressionTest.java": 
                        randoop_methods.setdefault(regression_folder + "/" + file_name, [])      
                        method_names = utils.extract_method_names(regression_folder + "/" + file_name)
                        randoop_methods[regression_folder + "/" + file_name] = method_names
            except:
                try:
                    class_path = "/".join(get_modified_classes(project, bug_id)[1].split(".")[:-1])
                    regression_folder = "./defects4j_randoop_tests/{}_randoop/{}/randoop/{}/{}".format(project, project, bug_id, class_path)
                    regression_files = os.listdir(regression_folder)


                    for file_name in regression_files:
                        if file_name != "RegressionTest.java": 
                            randoop_methods.setdefault(regression_folder + "/" + file_name, [])      
                            method_names = utils.extract_method_names(regression_folder + "/" + file_name)
                            randoop_methods[regression_folder + "/" + file_name] = method_names
                except:
                    return 1

    tests = {'relevant_tests': [], 'failed_BC': [], 'failed_FC': []}

    for test in set(buggy_tests + fixed_tests):
        if test in fixed_tests:
            tests['failed_FC'].append(test)
        tests['failed_BC'].append(test)

    if not randoop_available:
        tests['relevant_tests'] = [test for test in relevant_tests]
    else:
        tests['relevant_tests'] = randoop_methods

    return tests


def extract_randoop_tests(project,bug_id):
    archive = "./defects4j_randoop_tests/{}_randoop/{}/randoop/{}/{}-{}f-randoop.{}.tar.bz2".format(project, project, bug_id, project, bug_id, bug_id)
    
    if os.path.isfile(archive):
        os.system("tar -xf "+ archive + " -C ./defects4j_randoop_tests/{}_randoop/{}/randoop/{}".format(project, project, bug_id, project, bug_id, bug_id))
        return True
    return False


def export_tests(project, bug_id, tests, randoop_available):
    tests = export_test_body(project, bug_id, tests, 'failed_BC', randoop_available)
    tests = export_test_body(project, bug_id, tests, 'failed_FC', randoop_available)
    tests = export_test_body(project, bug_id, tests, 'relevant_tests', randoop_available)
    return tests


def export_test_body(project, bug_id, tests, version, randoop_available):
    relevant_tests_new = []
    for test in tests[version]:
        if not randoop_available:
            if version == 'relevant_tests':
                test_file_name = test.split(".")[-1] + ".java"
            else:
                test_file_name = test.split("::")[0].split(".")[-1] + ".java"

            currpwd = "./projects/" + project + "/" + bug_id + "/compile/fixed"
            os.system("find " + currpwd + " -name " + "'" + test_file_name + "'" + " > tf.txt")
            with open("tf.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
                found_paths = f.readlines()
                if len(found_paths) == 0:
                    continue
                substring = test.split("::")[0].replace(".", "/")
                test_file_location = ''
                for path in found_paths:
                    if substring in path:
                        test_file_location = path
                        break

                test_file_location = test_file_location.strip()
                test_file_location = test_file_location.replace("$","\$")
            os.system("rm tf.txt")

            if version == 'relevant_tests':
                method_names = utils.extract_method_names(test_file_location)
                for method_name in method_names:
                    relevant_tests_new.append(test + "::" + method_name)
                    output_file_location = "./projects/{}/{}/output/{}/{}.txt".format(project, bug_id, version, method_name)
                    os.system("python3 javaTestMethodExtractor.py " + test_file_location + " " + method_name + " " + output_file_location)
            else:
                method_name = test.split("::")[1]
                output_file_location = "./projects/{}/{}/output/{}/{}.txt".format(project, bug_id, version, method_name)
                os.system("python3 javaTestMethodExtractor.py " + test_file_location + " " + method_name + " " + output_file_location)

    if randoop_available:   
        if version == 'relevant_tests':
            relevant_dict = tests[version]
            locations = relevant_dict.keys()

            for location in locations:
                method_names = relevant_dict[location]
                method_names = random.sample(method_names, len(method_names))
                counter = 0
                for method_name in method_names:
                    if counter >= 10:
                        break

                    if method_name in list(map(lambda x: x.split("::")[-1], tests['failed_BC'])):
                        continue
                    
                    counter+=1
                    output_file_location = "./projects/{}/{}/output/{}/{}.txt".format(project, bug_id, version, method_name)
                    os.system("python3 javaTestMethodExtractor.py " + location + " " + method_name + " " + output_file_location)
                    location_temp = location.replace("./defects4j_randoop_tests/{}_randoop/{}/randoop/{}/".format(project, project, bug_id), "")
                    location_temp = location_temp.replace(".java", "")
                    location_temp = location_temp.replace("/", ".")
                    relevant_tests_new.append(location_temp + "::" + method_name)
        else:
            for test in tests[version]:
                method_name = test.split("::")[1]
                test_file = test.split("::")[0].replace(".", "/")
                test_file_location = "./defects4j_randoop_tests/{}_randoop/{}/randoop/{}/{}.java".format(project, project, bug_id, test_file)
                test_file_location = test_file_location.replace("$","\$")
                output_file_location = "./projects/{}/{}/output/{}/{}.txt".format(project, bug_id, version, method_name)
                os.system("python3 javaTestMethodExtractor.py " + test_file_location + " " + method_name + " " + output_file_location)
                

    if version == 'relevant_tests':
        tests[version] = relevant_tests_new

    return tests


def get_modified_classes(project, bug_id):
    fixed_path = "./projects/" + project + "/" + bug_id + "/compile/fixed"
    output_loc = "./projects/" + project + "/" + bug_id + "/output/modified_classes/modified.txt"
    os.system("defects4j export -p classes.modified -w " + fixed_path + " -o " + output_loc)

    with open(output_loc) as f:
        modified_classes = f.readlines()
        modified_classes = list(map(lambda x: x.strip(), modified_classes))
        
    return modified_classes


def export_modified_classes(project, bug_id, modified_classes, tests):
    for class_name in modified_classes:
        java_file_name = class_name.split(".")[-1] + ".java"
        class_fixed_pwd = "./projects/" + project + "/" + bug_id + "/compile/fixed"
        class_buggy_pwd = "./projects/" + project + "/" + bug_id + "/compile/buggy"
        os.system("find " + class_fixed_pwd + " -name " + "'" + java_file_name + "'" + " > cfl.txt")
        os.system("find " + class_buggy_pwd + " -name " + "'" + java_file_name + "'" + " > cbl.txt")
        with open("cfl.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
            found_paths = f.readlines()
            if len(found_paths) == 0:
                return 0

            substring = class_name.replace('.', '/')
            class_fixed_location = ''
            for path in found_paths:
                if substring in path:
                    class_fixed_location = path
                    break

            class_fixed_location = class_fixed_location.strip()
            class_fixed_location = class_fixed_location.replace("$", "\$")

        with open("cbl.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
            found_paths = f.readlines()
            if len(found_paths) == 0:
                continue

            substring = class_name.replace('.', '/')
            class_buggy_location = ''
            for path in found_paths:
                if substring in path:
                    class_buggy_location = path
                    break

            class_buggy_location = class_buggy_location.strip() 
            class_buggy_location = class_buggy_location.replace("$", "\$")

        os.system("rm cfl.txt cbl.txt")
        class_name = java_file_name.split(".")[0]
        output_file_location = "./projects/" + project + "/" + bug_id + "/output/modified_classes/'" + class_name + "'/"
        os.system("mkdir " + output_file_location)
        os.system("python3 javaClassMethodExtractor.py " + class_fixed_location + " " +  class_buggy_location + " " + output_file_location  + "> ./currAmount.txt")

        with open("./currAmount.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
            number = f.readlines()
            if len(number) == 0:
                number = 0
            else:
                number = int(list(map(lambda x: x.strip(), number))[0])
        
        export_tuples(project, bug_id, number, tests, class_name)

        os.system('rm currAmount.txt')


def export_tuples(project, bug_id, number, tests, class_name):
    counter = 0
    tuples = {}

    for test in set(tests['relevant_tests'] + tests['failed_BC'] + tests['failed_FC']):
        method_name = test.split("::")[1]
        test_file_location = ""

        if test in tests['relevant_tests']:     
            test_file_location = "./projects/" + project + "/" + bug_id + "/output/relevant_tests/" + method_name + ".txt"
        elif test in tests['failed_BC']:
            test_file_location = "./projects/" + project + "/" + bug_id + "/output/failed_BC/" + method_name + ".txt"
        else:
            test_file_location = "./projects/" + project + "/" + bug_id + "/output/failed_FC/" + method_name + ".txt"

        with open(test_file_location, "r", encoding="ISO-8859-1", errors='ignore') as f:
            test_method = f.readlines()
            test_method = "".join(test_method)

        for num in range(number):
            fixed_code_location = "./projects/" + project + "/" + bug_id + "/output/modified_classes/" + class_name + "/" + str(num) + str(num) + ".txt"
            buggy_code_location = "./projects/" + project + "/" + bug_id + "/output/modified_classes/" + class_name + "/" + str(num) + ".txt"

            with open(fixed_code_location, "r", encoding="ISO-8859-1", errors='ignore') as f:
                fixed_code = f.readlines()
                fixed_code = "".join(fixed_code)

            with open(buggy_code_location, "r", encoding="ISO-8859-1", errors='ignore') as f:
                buggy_code = f.readlines()
                buggy_code = "".join(buggy_code)

            is_duplicate = False
            if test in tests['failed_BC']:
                tuples[counter] = {"project": project, "bug_id": bug_id, "code": buggy_code, "test_name": method_name, "test_code": test_method, "label": "F", "type": "BC"}
                counter += 1
                is_duplicate = True

            elif test in tests['failed_FC']:
                tuples[counter] = {"project": project, "bug_id": bug_id, "code": fixed_code, "test_name": method_name, "test_code": test_method, "label": "F", "type": "FC"}
                counter += 1
                continue    # if it fails on FC, then there is no passing test

            tuples[counter] = {"project": project, "bug_id": bug_id, "code": fixed_code, "test_name": method_name, "test_code": test_method, "label": "P", "type": "FC"}
            counter += 1

            if not is_duplicate:
                tuples[counter] = {"project": project, "bug_id": bug_id, "code": buggy_code, "test_name": method_name, "test_code": test_method, "label": "P", "type": "BC"}
                counter += 1

    bug_tuples = json.dumps(tuples, indent = 4)

    with open("./projects/" + project + "/" + str(bug_id) + "/output/" + class_name +  "_tuples.json", "w") as out_f:
        out_f.write(bug_tuples)


def remove_dirs(project, bug_id):
    rm_location = "./projects/" + project + "/" + bug_id + "/compile"
    shutil.rmtree(rm_location)


def parse_args():
    parser = argparse.ArgumentParser(prog='generating data tuples')
    parser.add_argument('--project_name', type=str, default='all', help='project you want to produce the tuples for')
    parser.add_argument('--randoop_tests', type = bool, default = False, help = 'you want to run randoop tests?' )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    generate_tuples(args)
