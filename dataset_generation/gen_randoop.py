import sys
sys.path.append('../')

import os
import argparse
from configs import configs


def generate_mutants(args):
    config = configs()
    generate_randoop_tests(config['projects'], args)


def generate_randoop_tests(projects, args):
    for project in projects:
        bug_ids = get_bug_ids(project)
        for bug_id in bug_ids:
            os.system('{}/{}/gen_tests.pl -g randoop -p {} -v {}f -n {} -b 100 -o {}_randoop'.format(args.defects4j_path, 'defects4j/framework/bin', project, bug_id, bug_id, project))

    os.system('rm temp.txt')


def get_bug_ids(project_name):
    command = 'defects4j query -p ' + project_name + ' -q bug.id > temp.txt'
    os.system(command)

    bug_ids = []
    with open('temp.txt') as fr:
        for line in fr.readlines():
            bug_ids.append(line.strip())

    return bug_ids


def parse_args():
    parser = argparse.ArgumentParser(prog='generating randoop tests')
    parser.add_argument('--defects4j_path', type=str, default='/home/$USER', help='path to defects4j. default path is /home/$USER')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    generate_mutants(args)
