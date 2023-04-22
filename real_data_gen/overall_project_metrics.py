import csv
import os
import sys

projects = sys.argv[1].split(sep='*')
print(projects)

path = './real_data_gen/fold0'

open(f"{path}/test_stats.csv", 'w').close()

with open(f"{path}/test_stats.csv", "ab") as fout:
    # First file:
    with open(f"{path}/{projects[0]}/test_stats.csv", "rb") as f:
        fout.writelines(f)

    # Now the rest:
    for project in projects[1:]:
        with open(f"{path}/{project}/test_stats.csv", "rb") as f:
            next(f) # Skip the header, portably
            fout.writelines(f)