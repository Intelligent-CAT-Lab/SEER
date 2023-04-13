# Issue when executing test classifier on new data
[/scripts](https://github.com/Intelligent-CAT-Lab/SEER/tree/main/scripts) includes scripts to reproduce the research questions on existing results, but does not run the classifier on the data, e.g. `phase2.json`. I seek to run the classifier on a new dataset (described below) and then calculate the summary results as done in `/scripts`.

## New Dataset
The new dataset matches the schema for `phase2.json` from `phase2_dataset_final_whole.zip` in [Zenodo](https://zenodo.org/record/6970062).
```json
{
  "0": {
    "dataset": "...",
    "project": "...",
    "C": "...",
    "T": "...",
    "label": "...",
  },
  "1": {"..."}
}
```

## Steps taken
1. Downloaded pre-trained weights from [Zenodo](https://zenodo.org/record/6970062).
2. Generated `new_data.json` matching the schema above. 
3. Execute `python3 test.py --data_path ./new_data.json --model JointEmbedder --dataset TestOracleInferencePhase2 --timestamp 202203201945 --gpu_id 0 --fold 1 --reload_from 29`. See the error below.
  ```
  Traceback (most recent call last):
    File "test.py", line 75, in <module>
      test(args)
    File "test.py", line 19, in test
      test_set = TestOracleDatasetPhase2(args.model, args.data_path, 'code_test.h5', 1075, 'test_test.h5', 1625, 'label_test.h5')
    File ".../SEER/learning/data_loader_phase2.py", line 20, in __init__
      table_code = tb.open_file(data_dir + f_code)
    File ".../.conda/envs/seer/lib/python3.6/site-packages/tables/file.py", line 300, in open_file
      return File(filename, mode, title, root_uep, filters, **kwargs)
    File ".../.conda/envs/seer/lib/python3.6/site-packages/tables/file.py", line 750, in __init__
      self._g_new(filename, mode, **params)
    File "tables/hdf5extension.pyx", line 368, in tables.hdf5extension.File._g_new
    File ".../.conda/envs/seer/lib/python3.6/site-packages/tables/utils.py", line 143, in check_file_access
      raise OSError(f"``{path}`` does not exist")
  OSError: ``.../SEER/datasets/phase3_dataset/code_test.h5`` does not exist
  ```

`code_test.h5`, `test_test.h5`, and `label_test.h5` are not generated by any methods in `utils.py`. Thus, I am unable to use the pre-trained model to classify other datasets.

> Please describe how to effectively run `test.py` on new data if there is a better way.