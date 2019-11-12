# PseudoClone

This is the code for PseudoClone.


pre-process includes the trainsformation on source code so it can be fit into models for training and testing.
See `pre-process/process/generate-xxxx` for detail usage.

train includes the train code for BiLSTM+Attention.

test includes the test code for our approach.

In order to directly run test code to see experiment result on BCB, please download [dataset.tar.gz](https://drive.google.com/open?id=1JWsHOE5ZF5QgFyTW2sj-d9hNW8kfXXIY)
and unzip it into `test/LSTMCCloneTest`. Our trained model and configuration are in it. Run `test/LSTMCCloneTest/driver/TestBLSTM.py` with parameter:
```
--config_file dataset/blstm/tpe/config.cfg 
--thread 1 
--gpu -1 if cpu
--input (anywhere you like) 
--output (anywhere you like) 
```

To detect other datasets, please refer to the scripts in `pre-process/process`. 
Please download [dataset.zip](https://drive.google.com/open?id=1DXvz-giFprwGBU3rG9iZzyasQujUycUz)
and unzip it into `pre-process` folder, same level as data. It includes some dicts like keywords and operators.

All the links are google drive, and shared along with this github account's email. It is under the rules of double-blind.\

Questions are welcomed, please contact [correspond author](mailto:selva.george95@gmail.com)
