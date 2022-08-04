def configs():
    configurations = {
        'projects': ["Chart", "Cli", "Closure", "Codec", "Collections", "Compress", "Csv", 
                    "Gson", "JacksonCore", "JacksonDatabind", "JacksonXml", "Jsoup", "JxPath", 
                    "Lang", "Math", "Mockito", "Time"],

        # data_params
        'dataset_name': 'TestOracleDatasetPhase1', # name of dataset to specify a data loader
            #training data
            'codepos_train_dataset': 'codepos_train.h5',
            'codeneg_train_dataset': 'codeneg_train.h5',
            'codepos_diff_train': 'codeposdiff_train.h5',
            'codeneg_diff_train': 'codenegdiff_train.h5',
            'codepos_valid_dataset': 'codepos_valid.h5',
            'codeneg_valid_dataset': 'codeneg_valid.h5',
            'codepos_diff_valid': 'codeposdiff_valid.h5',
            'codeneg_diff_valid': 'codenegdiff_valid.h5',

            'code_train_dataset': 'code_train.h5',
            'test_train_dataset': 'test_train.h5',
            'label_train_dataset': 'label_train.h5',
            'code_valid_dataset': 'code_valid.h5',
            'test_valid_dataset': 'test_valid.h5',
            'label_valid_dataset': 'label_valid.h5',
                   
            #parameters
            'code_len': 723,
            'test_len': 1625,
            'n_words': 155535,
            'code_n_words': 21335,
            'test_n_words': 233263,
            #vocabulary info
            'vocab_code': 'vocab_code.json',
            'vocab_test': 'vocab_test.json',

        #training_params
            'n_folds': 10,
            'batch_size': 16,
            'nb_epoch': 150,
            'learning_rate': 1.34e-6,
            'adam_epsilon':1e-8,
            'warmup_steps':5000,
            'emb_size': 200,
            'n_hidden': 1024,
            'n_head': 2,
            'n_layers': 1,
            'dropout':0.25,
            'margin':0.4,
            'filter_size': 2,
            'stride': 2,
            'patience': 5
    }

    return configurations
