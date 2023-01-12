# Perfect Is the Enemy of Test Oracle

[<img padding="10" align="right" src="https://www.acm.org/binaries/content/gallery/acm/publications/artifact-review-v1_1-badges/artifacts_evaluated_functional_v1_1.png" alt="ACM Artifacts Evaluated - Functional v1.1" width="114" height="113"/>][paper]
[<img padding="10" align="right" src="https://www.acm.org/binaries/content/gallery/acm/publications/artifact-review-v1_1-badges/artifacts_available_v1_1.png" alt="ACM Artifacts Available v1.1" width="114" height="113"/>][paper]

[![Install](https://img.shields.io/badge/install-instructions-blue)](INSTALL.md)
[![Dependencies](https://img.shields.io/badge/install-dependencies-blue)](REQUIREMENTS.md)
[![GitHub](https://img.shields.io/github/license/Intelligent-CAT-Lab/SEER?color=blue)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6970062.svg)](https://doi.org/10.5281/zenodo.6970062)

Artifact repository for the paper [_Perfect Is the Enemy of Test Oracle_](https://doi.org/10.1145/3540250.3549086), accepted at _ESEC/FSE 2022_.
Authors are [Ali Reza Ibrahimzada][ali], [Yiğit Varlı][yigit], [Dilara Tekinoğlu][dilara], and [Reyhaneh Jabbarvand][reyhaneh].

The artifact mainly consists of Python scripts which were used for automating dataset generation, mutation testing, and deep learning model implementation. We have split each distinct component of SEER into a separate directory in this repository. Please refer to each directory for a detailed explanation of the component.

**In order to reproduce the result of each Research Question (RQ) from the paper, please refer to [`scripts`](scripts)**

[ali]: https://alibrahimzada.github.io/
[yigit]: https://github.com/yigitv4rli
[dilara]: https://dtekinoglu.github.io/
[reyhaneh]: https://reyhaneh.cs.illinois.edu/index.htm

[paper]: https://doi.org/10.1145/3540250.3549086

## Data Archive
Please find the model checkpoints and final datasets for both phase-1 and phase-2 of model training on [Zenodo](https://doi.org/10.5281/zenodo.6970062). Below is a description for each file of our data archive on Zenodo.
* `attention_analysis.zip`: This zip contains the necessary files for attention analysis. Please refer to [attention_analysis](attention_analysis) for further explanations.
* `defects4j_randoop_tests.zip`: This zip contains the generated randoop tests for all 17 projects available in Defects4J. We use the content of this file in [dataset_generation](dataset_generation)
* `epoch_21_fold_1.h5`: This file is a checkpoint of the best performing model from phase-1. The model has been saved after epoch 21 in fold 1.
* `epoch_29_fold_1.h5`: This file is a checkpoint of the best performing model model from phase-2. The model has been saved after epoch 29 in fold 1.
* `phase1_dataset_final.zip`: This zip contains the cleaned and preprocessed dataset for phase-1 of model training.
* `phase2_dataset_final_unseen.zip`: This zip contains the cleaned and preprocessed dataset for phase-2 of model training. The keyword "unseen" in the file name represents that minor projects are not included in model training.
* `phase2_dataset_final_whole.zip`: This zip contains the cleaned and preprocessed dataset for phase-2 of model training. The keyword "whole" in the file name represents that all projects are included in model training, testing, and validation.
* `data.zip`: This zip contains all necessary files for reproducing the result of each RQ from the paper. We use this file in [scripts](scripts)

## SEER Overview
Automation of test oracles is one of the most challenging facets of software testing, but remains comparatively less addressed compared to automated test input generation. Test oracles rely on a ground-truth that can distinguish between the correct and buggy behavior to determine whether a test fails (detects a bug) or passes. What makes the oracle problem challenging and undecidable is the assumption that the ground-truth should know the exact expected, correct or buggy behavior. However, we argue that one can still build an accurate oracle without knowing the exact correct or buggy behavior, but how these two might differ. This paper presents SEER, a Deep Learning-based approach that in the absence of test assertions or other types of oracle, can automatically determine whether a unit test passes or fails on a given method under test (MUT). To build the ground-truth, SEER jointly embeds unit tests and the implementation of MUTs into a unified vector space, in such a way that the neural representation of tests are similar to that of MUTs they pass on them, but dissimilar to MUTs they fail on them. The classifier built on top of this vector representation serves as the oracle to generate “fail” labels, when test inputs detect a bug in MUT or “pass” labels, otherwise. Our extensive experiments on applying SEER to more than 5K unit tests from a diverse set of opensource Java projects show that the produced oracle is (1) effective in predicting the fail or pass labels, achieving an overall accuracy, precision, recall, and F1 measure of 93%, 86%, 94%, and 90%, (2) generalizable, predicting the labels for the unit test of projects that were not in training or validation set with negligible performance drop, and (3) efficient, detecting the existence of bugs in only 6.5 milliseconds on average. Moreover, by interpreting the proposed neural model and looking at it beyond a closed-box solution, we confirm that the oracle is valid, i.e., it predicts the labels through learning relevant features.

## Implementation Details
Please check the following descriptions related to each .py file in this directory:
* `configs.py`: This file is used as a configuration when training deep learning models. We control hyperparameters, dataset, etc. from this file.
* `utils.py`: This file contains independent functions which are used throughout the project.
  * For creating the vocabulary for both phase-1 and phase-2, please execute the following:  
  `python3 utils.py create_vocabulary all`
  * For creating the .h5 files from JSONs, please execute the following if JSON type is train, fold is 1, and model type is JointEmbedder:  
  `python3 utils.py json_to_h5 train 1 JointEmbedder`
  * For extracting the length of the longest sequence (Code, Test) in phase-1 dataset, please execute the following:  
  `python3 utils.py get_max_len phase1_dataset_final`
  * For splitting the raw dataset in phase-1 into train (90%), valid (5%), and test sets (5%), please execute the following:  
  `python3 utils.py train_valid_test_split phase1_dataset_final 0.05 0.05`
  * For filtering the assert statements in the dataset, please execute the following:  
  `python3 utils.py filter_asserts`

The directory structure of SEER is as follows. Please read the corresponding README file inside each directory, if necessary.

     SEER
       |
       |--- attention_analysis:       The Multi-Head Attention Analysis related to model interpretation
       |
       |--- embedding_analysis:       The Embedding Analysis related to model interpretation
       |
       |--- dataset_generation:       The module which contains all scripts related to dataset generation
       |
       |--- models:                   The module which contains the deep learning models implemented in PyTorch
       |
       |--- learning:                 The module which contains everything related to model training and evaluation
       |
       |--- scripts:                  The module which reproduces RQs from the paper
       |
       |--- mutant_generation:        The module which contains all scripts related to mutant generation
           |
           |--- mutation_operators:   A directory which contains all mutation operators used in Major

## Please Cite as
```
@inproceedings{10.1145/3540250.3549086,
    author = {Ibrahimzada, Ali Reza and Varli, Yigit and Tekinoglu, Dilara and Jabbarvand, Reyhaneh},
    title = {Perfect is the Enemy of Test Oracle},
    year = {2022},
    isbn = {9781450394130},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/3540250.3549086},
    doi = {10.1145/3540250.3549086},
    abstract = {Automation of test oracles is one of the most challenging facets of software testing, but remains comparatively less addressed compared to automated test input generation. Test oracles rely on a ground-truth that can distinguish between the correct and buggy behavior to determine whether a test fails (detects a bug) or passes. What makes the oracle problem challenging and undecidable is the assumption that the ground-truth should know the exact expected, correct, or buggy behavior. However, we argue that one can still build an accurate oracle without knowing the exact correct or buggy behavior, but how these two might differ. This paper presents , a learning-based approach that in the absence of test assertions or other types of oracle, can determine whether a unit test passes or fails on a given method under test (MUT). To build the ground-truth, jointly embeds unit tests and the implementation of MUTs into a unified vector space, in such a way that the neural representation of tests are similar to that of MUTs they pass on them, but dissimilar to MUTs they fail on them. The classifier built on top of this vector representation serves as the oracle to generate “fail” labels, when test inputs detect a bug in MUT or “pass” labels, otherwise. Our extensive experiments on applying to more than 5K unit tests from a diverse set of open-source Java projects show that the produced oracle is (1) effective in predicting the fail or pass labels, achieving an overall accuracy, precision, recall, and F1 measure of 93%, 86%, 94%, and 90%, (2) generalizable, predicting the labels for the unit test of projects that were not in training or validation set with negligible performance drop, and (3) efficient, detecting the existence of bugs in only 6.5 milliseconds on average. Moreover, by interpreting the neural model and looking at it beyond a closed-box solution, we confirm that the oracle is valid, i.e., it predicts the labels through learning relevant features.},
    booktitle = {Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
    pages = {70–81},
    numpages = {12},
    keywords = {Test Oracle, Software Testing, Test Automation, Deep Learning},
    location = {Singapore, Singapore},
    series = {ESEC/FSE 2022}
}
```
## Contact

Please don't hesitate to open issues or pull-requests, or to contact us directly (alirezai@illinois.edu). We are thankful for any questions, constructive criticism, or interest. :blush:
