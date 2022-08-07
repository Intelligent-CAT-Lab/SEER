# Installation Instructions
In this guide, we will go through how to set up and use SEER. Please read on for step-by-step installation instructions.

## 1. Clone SEER from GitHub
In order to download our code repository, please use git and execute the following in order to clone our repository in your local machine.

`git clone https://github.com/Intelligent-CAT-Lab/SEER.git`

After cloning has been completed, please change the directory by executing the following:

`cd SEER`

## 2. Install Dependencies
As mentioned in [REQUIREMENTS.md](REQUIREMENTS.md), SEER has some software dependencies. Please execute the following in order to install all dependencies. It is important to note that we have developed SEER on Ubuntu 18.04 LTS and Python 3.6.9.

`pip3 install -r requirements.txt`

## 3. Taking SEER for a Ride
We provide a small demo from the learning module of SEER in order to make sure it has been set up properly, and all components are functional. The learning module is one of the core and most important component of SEER. In particular, we will show a sample output, or what a user expects to see when he/she wants to train phase-1 of SEER.

In order to download all necessary files from Zenodo, please execute the following in order:

* `cd learning`
* `sudo apt install curl`
* `sudo apt install unzip`
* `curl https://zenodo.org/record/6970062/files/phase1_dataset_final.zip?download=1 --output phase1_dataset_final.zip`
* `unzip phase1_dataset_final.zip`

At this point, we are ready to start phase-1 of model training. To do that, please execute the following:

* `python3 train_phase1.py --data_path phase1_dataset_final/ --model JointEmbedder --dataset TestOracleInferencePhase1 --fold 1 --gpu_id 0`

If everything is sound and correct, you should be able to see the following output on your console:

```
loading data...
18736 entries
loading data...
986 entries
Constructing Model ...
```

After seeing this, the training phase has been started and the model is consistently fetching a batch from the training dataset, and use it for learning purposes. It could take some time until you see the evaluation results after the first epoch.

If you do not see the output above, it indicates that something is not right. Please get in touch with the authors in order to resolve your problem.
