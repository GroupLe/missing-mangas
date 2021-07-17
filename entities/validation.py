from sklearn.metrics import roc_auc_score, f1_score, mean_squared_error, log_loss
from itertools import combinations
import numpy as np
from collections import defaultdict
import pandas as pd

FUNCTIONS = {"roc_auc_score": roc_auc_score, "f1_score": f1_score,
             "mean_squared_error": mean_squared_error, "log_loss": log_loss}


class BinaryValidator:

    @staticmethod
    def validate(test: pd.Series, pred: pd.Series) -> defaultdict:
        metrics = defaultdict(list)
        for name in FUNCTIONS:
            metrics[name] = FUNCTIONS[name](test, pred)

        return metrics







