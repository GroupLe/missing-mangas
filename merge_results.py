import os
import pandas as pd
from collections import defaultdict

result = defaultdict(list)
result["name"] = []
directory = "missing-mangas/data/models_results/"

for root, dirs, files in os.walk(directory):
    for file in files:
        df = pd.read_csv(directory + file)
        columns = list(df.columns)
        for string in df.to_records(index=False):
            result["name"].append(file.replace(".csv", ""))
            for index, elem in enumerate(string):
                result[columns[index]].append(elem)
                
            

pd.DataFrame(result).to_csv("data/models_results/merged.csv", index = False)