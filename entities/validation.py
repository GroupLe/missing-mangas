from sklearn.metrics import roc_auc_score, f1_score, mean_squared_error, log_loss
from itertools import combinations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

FUNCTIONS = {"roc_auc_score": roc_auc_score, "f1_score": f1_score,
             "mean_squared_error": mean_squared_error, "log_loss": log_loss}


class BinaryValidator:

    @staticmethod
    def validate(test: pd.Series, pred: pd.Series) -> dict:
        metrics = {}
        for name in FUNCTIONS:
            metrics.update({name: FUNCTIONS[name](test, pred)})
        return metrics


class ReprezentData:

    @staticmethod
    def create_csv(metrics: dict, path: str) -> None:
        pd.DataFrame(metrics, index=[0]).to_csv(path, index=False)

    @staticmethod
    def plot(path: str) -> None:
        df = pd.read_csv(path)
        for index, name in enumerate(df):
            plt.xlabel('number_of_dimention')
            plt.ylabel("score")
            plt.title("Histogram for " + name + ":")
            plt.plot(np.arange(len(df[name])), df[name])
            plt.show()

    @staticmethod
    def add_metrics_to_csv(metrics: dict, path: str) -> pd.DataFrame:
        df = pd.DataFrame(metrics, index=[0])
        old_df = pd.read_csv(path)
        result_df = pd.concat([old_df, df], ignore_index=True)
        result_df.to_csv(path, index=False)

    @staticmethod
    def view_df(path: str) -> None:
        display(pd.read_csv(path))

