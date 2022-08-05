# Mutant Generation
In this section, we aim to generate the syntactic faults dataset by creating higher order mutants. In order to run the scripts properly, you need to install Defects4J and its dependencies. You can follow the steps from the official Defects4J installation guide [here](https://github.com/rjust/defects4j). Please make sure that you add Defects4J's executables to your PATH.

## How to check if Defects4J has been installed correctly?
After following the steps from the official Defects4J installation guide, please execute the following in your terminal:

`defects4j info -p Lang`

If the output is like the following, it means Defects4J is functional and ready to be used in our work. Please note that instead of `/home/ali/` you will see your own directory names.

```
Summary of configuration for Project: Lang
--------------------------------------------------------------------------------
    Script dir: /home/ali/defects4j/framework
      Base dir: /home/ali/defects4j
    Major root: /home/ali/defects4j/major
      Repo dir: /home/ali/defects4j/project_repos
--------------------------------------------------------------------------------
    Project ID: Lang
       Program: commons-lang
    Build file: /home/ali/defects4j/framework/projects/Lang/Lang.build.xml
--------------------------------------------------------------------------------
           Vcs: Vcs::Git
    Repository: /home/ali/defects4j/project_repos/commons-lang.git
     Commit db: /home/ali/defects4j/framework/projects/Lang/active-bugs.csv
Number of bugs: 64
--------------------------------------------------------------------------------
```

In all other cases, there is something wrong, please create an issue so we could assist you.

## How to Generate Higher Order Mutants?

In order to generate higher order mutants, please locate defects4j at `/home/$USER` and locate the repository (SEER) under `/home/$USER/defects4j`. Before running `mutation_operators.py` and `generateMutants.py` scripts, please run the following command in your terminal which allows exporting the source code of generated mutants:

`export MAJOR_OPT="-J-Dmajor.export.mutants=true"`

Moreover, please find the file `/home/$USER/defects4j/framework/projects/defects4j.build.xml` and change the line `haltonfailure="true"` to `haltonfailure="false"`.

Change your directory `cd mutant_generation`, and then run the following scripts in the given order:

- `mutation_operators.py`: The script which determines applicable mutation operators for each modified method in the dataset. Running the script creates a file `{project_name}-mutators.txt` which is used for the next step. Please locate the `projects` directory inside `mutant_generation` before executing this script. The `projects` directory is created as a result of executing `tuple_gen.py` inside `dataset_generation`.
- `generateMutants.py`: The script for generating higher order mutants for each mutable project. Before running the script, please make sure `mutation_operators` directory and `{project_name}-mutator.txt` file -created in the previous step- are available inside `mutant_generation` directory.
- `mutant_stats.py`: The script for creating statistics for syntatic faults dataset.

## Generations are Slow?

We understand generations take a significant amount of time. In fact, we were only able to finish it in a few days. Therefore, we highly recommend everyone to use the final, cleaned, preprocessed dataset available on Zenodo.
