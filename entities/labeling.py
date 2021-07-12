import pandas as pd
import os


class DataMatcher:
    def __init__(self, df: pd.DataFrame):
        self.data = df
        self.last_matched = 0
        self.user_verdict = []

    def match_labels_by_hands(self, iterations=100):
        count_iterations = 0
        columns = list(self.data.columns)
        for index, line in enumerate(
                self.data.iloc[self.last_matched:].to_records(index=False)):
            if index == iterations:
                self.last_matched += iterations
                break
            for pair in list(zip(columns, list(line))):
                print(" : ".join(str(elem) for elem in pair))
            print(f"{index + 1}/{iterations}")
            while True:
                try:
                    user_opinion = int(input())
                    if user_opinion != 1 and user_opinion != 0:
                        raise ValueError
                    else:
                        break
                except ValueError:
                    print("Incorrect input, you should enter 1 or 0")
            self.user_verdict.append(user_opinion)

    def save_user_verdict(self, name_of_new_column: str, path: str):
        new_data = self.data.iloc[:self.last_matched]
        new_data.loc[:self.last_matched, name_of_new_column] = self.user_verdict
        new_data.to_csv(path)
