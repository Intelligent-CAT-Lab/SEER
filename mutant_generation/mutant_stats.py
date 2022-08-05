import json
import pathlib
import os
from csv import DictWriter
import pandas as pd

# This function extracts and returns the method name from code field of a tuple.
def get_method_name(code):
    position = code.index("(") -1 
    method_name = []
    while position >= 0:
        if code[position] != " " and code[position] != "\t":
            method_name.insert(0,code[position])
            position -=1
        else:
            break
    result = ""
    for elem in method_name:
        result+=elem
    return result

# This function pops P-labeled tuples which do not contain triggering test.
def remove_non_triggering(tuples,new_tuples):
    for _id in tuples:
        code = tuples[_id]['code']
        test = tuples[_id]['test_code']
        label =  tuples[_id]['label']
        method = get_method_name(code)

        if method+"(" not in test:
            print(tuples[_id]['project'], tuples[_id]['bug_id'], "was not triggering.")
            try:
                new_tuples.pop(_id)
            except:
                pass

# This function returns true if tuple's test field contains a randoop test.
def isRandoop(test_name):
    if "test" not in test_name:
        return False
    
    start = test_name.index("test")+4
    for i in range(start, len(test_name)):
        if test_name[i] >"9" or test_name[i] < "0":
            return False
            
    return True

def get_wrong_fc(project):

    if project == "Codec":
        return ["6","9"]

    if project == "Chart":
        return ["2","5","9","11","18","14","22"]

    if project == "Compress":
        return ["30"]
    
    if project == "JacksonDatabind":
        return ["57"]
    
    if project == "Gson":
        return ["2","9","15"]
    
    if project == "Csv":
        return ["13"]
    
    if project == "JacksonCore":
        return ["17","18"]
    
    if project == "Math":
        return ["8","37","41","63","75","83"]
    
    if project == "Lang":
        return ["11","61","63"]
    
    if project == "Time":
        return ["13","14","15","18"]
    
    if project == "JxPath":
        return ["1","9","12","16","22"]
    
    if project == "Jsoup":
        return ["1","8","46","47","49","67","68","75"]
    
    return []

def remove_wrong_fc(tuples,new_tuples):
    for _id in tuples:
        wrong_list = get_wrong_fc(tuples[_id]['project'])
        if tuples[_id]['bug_id'] in wrong_list:
            print(tuples[_id]['project'], tuples[_id]['bug_id'], "was wrong fc.")
            try:
                new_tuples.pop(_id)
            except:
                pass


# This function gets PT, FT, PRT, FRT, F and P numbers for each mutant.
def get_stats(tuples):
    stat_id = 0
    stats = {}
    processed_bugs = []
    for _id in tuples:
        bug = tuples[_id]['bug_id']
        if bug not in processed_bugs:
            processed_mutants = []
            processed_bugs.append(bug)
        
            mutant_id = 1

        mutant_code = tuples[_id]['code']
        if mutant_code not in processed_mutants:
            stat_id+=1

            print("New object for", bug, mutant_id)
            stats[stat_id] = {'project':tuples[_id]['project'],
                                'bug_id':tuples[_id]['bug_id'],
                                'Passing Dev Tests': 0,
                                'Failing Dev Tests': 0,
                                'Failing Randoop Tests': 0,
                                'Passing Randoop Tests': 0,
                                'Label F': 0,
                                'Label P': 0,
                                'mutant_id': mutant_id}
            processed_mutants.append(mutant_code)
            mutant_id+=1

        
        if  tuples[_id]['label'] == 'P' and isRandoop(tuples[_id]['test_name']):
            stats[stat_id]['Passing Randoop Tests'] +=1
            stats[stat_id]['Label P'] += 1

        elif  tuples[_id]['label'] == 'P' and isRandoop(tuples[_id]['test_name']) == False:
            stats[stat_id]['Passing Dev Tests'] +=1
            stats[stat_id]['Label P'] += 1

        elif  tuples[_id]['label'] == 'F' and isRandoop(tuples[_id]['test_name']):
            stats[stat_id]['Failing Randoop Tests'] +=1
            stats[stat_id]['Label F'] += 1

        elif  tuples[_id]['label'] == 'F' and isRandoop(tuples[_id]['test_name']) == False:
            stats[stat_id]['Failing Dev Tests'] +=1
            stats[stat_id]['Label F'] += 1

    with open(tuples[_id]['project']+"_stats.json","w") as m:
        m.write(json.dumps(stats, indent = 4))


def write_to_csv(projects):
    for project in projects:
        filename = project+"_stats.json"
        with open(filename) as tuples_file:
            tuples = json.load(tuples_file)
        for id in tuples:
            result = {'project':tuples[id]['project'],
                            'bug_id':tuples[id]['bug_id'],
                            'mutant_id': tuples[id]['mutant_id'],
                            'Passing Dev Tests': tuples[id]['Passing Dev Tests'],
                            'Failing Dev Tests': tuples[id]['Failing Dev Tests'],
                            'Failing Randoop Tests': tuples[id]['Failing Randoop Tests'],
                            'Passing Randoop Tests': tuples[id]['Passing Randoop Tests'],
                            'Label F': tuples[id]['Label F'],
                            'Label P': tuples[id]['Label P']
                            }


    
            field_names = ['project','bug_id', 'mutant_id','Passing Dev Tests',
                                'Failing Dev Tests',
                                'Failing Randoop Tests',
                                'Passing Randoop Tests',
                                'Label F',
                                'Label P'
                                ]
    
            with open("Mutants Stats.csv","a") as mutant_stats:
                dictwriter_object = DictWriter(mutant_stats,fieldnames=field_names)
                dictwriter_object.writerow(result)



""" main program starts here """

projects = ["JxPath","Cli","Codec","Compress","Csv","Gson","JacksonCore","JacksonXml",
"Time","Math","Lang","Jsoup","JacksonDatabind","Closure","Chart"]
toi_path = str(pathlib.Path.home()/"defects4j/SEER/mutant_generation")
os.chdir(toi_path+"/preprocessed_tuples_stats")

write_to_csv(projects)
