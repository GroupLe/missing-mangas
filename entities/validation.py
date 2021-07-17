from sklearn.metrics import roc_auc_score, f1_score, mean_squared_error, log_loss
from itertools import combinations
import numpy as np
from collections import defaultdict

FUNCTIONS = {"roc_auc_score": roc_auc_score, "f1_score": f1_score,
             "mean_squared_error": mean_squared_error, "log_loss": log_loss}


class BinaryValidator:
    def __init__(self, test: pd.DataFrame, predict: pd.DataFrame):
        self.predict = predict
        self.test = test

    def validate(self, path_to_csv: str) -> None:
        metrics = defaultdict(list)
        for name in FUNCTIONS:
            metrics[name] = FUNCTIONS[name](self.test, self.predict)

        df = pd.DataFrame(metrics, index=[0])
        try:
            old_df = pd.read_csv(path_to_csv)
            result_df = pd.concat([old_df, df], ignore_index=True)
            result_df.to_csv(path_to_csv, index=False)
        except:
            df.to_csv(path_to_csv, index=False)




