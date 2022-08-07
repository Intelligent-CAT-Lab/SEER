The artifacts for the paper _Perfect Is the Enemy of Test Oracle_ is a set of Python scripts which automates dataset generation, and it also contains scripts for model learning. We have added a component called [`scripts`](scripts) for reproducing every result from our evaluations/RQS in the paper. Our artifact has the following purposes:

* **Reusability**: Other researchers can use SEER as a benchmark and build more neural components on top of it. Moreover, they can also re-train SEER on a larger corpus of data, and integrate with some software for using it in practice. We documented all modules of SEER in detail and made the documentation available on Github as well.

* **Reproduced RQs**: Our artifact reproduces all evaluations from the paper to show that SEER is able to reproduce the results.

We claim the _Artifacts Available_ badge as we made our artifacts publicly available on Github and Zenodo.

We claim the _Artifacts Evaluated - Reusable_ as we implemented SEER as a reusable tool (see above).