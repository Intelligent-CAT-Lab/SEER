## Hardware Requirements
The data archive of SEER which is publicly available on Zenodo requires roughly 3 GBs of disk space. Moreover, all neural models have been trained on a Virtual Machine with a GPU on Google Cloud Platform. Using a GPU will significantly improve the performance of model. The details of our GPU is given in `RQ4` of the paper.

## Software Requirements
We have developed and tested SEER using Ubuntu 18.04 LTS (Bionic Beaver), Python 3.6.9, and Java 8. SEER has some software dependencies listed below:

* matplotlib
* numpy
* pandas
* scikit learn
* tables
* torch
* tqdm

Please install all dependencies by executing the following:

`pip3 install -r requirements.txt`
