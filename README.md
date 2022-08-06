# Perfect Is the Enemy of Test Oracle

Artifact repository for the paper _Perfect Is the Enemy of Test Oracle_, accepted at _ESEC/FSE 2022_.
Authors are [Ali Reza Ibrahimzada][ali], [Yiğit Varlı][yigit], [Dilara Tekinoğlu][dilara], and [Reyhaneh Jabbarvand][reyhaneh].

[ali]: https://alibrahimzada.github.io/
[yigit]: https://github.com/yigitv4rli
[dilara]: https://dtekinoglu.github.io/
[reyhaneh]: https://reyhaneh.cs.illinois.edu/index.htm

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
       |--- mutant_generation:        The module which contains all scripts related to mutant generation
           |
           |--- mutation_operators:   A directory which contains all mutation operators used in Major

## Contact

Please don't hesitate to open issues or pull-requests, or to contact us directly (alirezai@illinois.edu). We are thankful for any questions, constructive criticism, or interest. :blush:
