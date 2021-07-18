from sklearn.metrics import roc_auc_score, f1_score, mean_squared_error, log_loss
from itertools import combinations
import numpy as np
import pandas as pd

FUNCTIONS = {"roc_auc_score": roc_auc_score, "f1_score": f1_score,
             "mean_squared_error": mean_squared_error, "log_loss": log_loss}


class BinaryValidator:

    @staticmethod
    def validate(test: pd.Series, pred: pd.Series) -> dict:
        metrics = {}
        for name in FUNCTIONS:
            metrics.update({name: FUNCTIONS[name](test, pred)})
        return metrics







