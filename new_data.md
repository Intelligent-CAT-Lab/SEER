This execution used [this](https://drive.google.com/file/d/1Xp9q752zs0N0sVdFv5aW0lcQPtbY_a0Z/view?usp=share_link) file (placed in `./datasets/phase3_dataset`) that was generated using [this](https://github.com/anrath/SEER/blob/main/share-files/modify_data.ipynb) script.

## From [here](https://github.com/anrath/SEER/blob/main/README.md#implementation-details) generally:
Note that some of these do not work properly.

`python3 utils.py train_valid_test_split phase3_dataset 0 1.0`

`python3 utils.py create_vocabulary all`

`python3 utils.py json_to_h5 test 1 JointEmbedder`

## Error [here](https://github.com/anrath/SEER/blob/main/learning/phase3.err.)
Based on execution of [rlurm.slurm](https://github.com/anrath/SEER/blob/main/learning/rlurm.slurm).
