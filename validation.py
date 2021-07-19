import sys
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from typing import Callable

from entities.titles import (
    CompareByLanguageFuzzyTitle,
    CompareByLanguageNaiveTitle,
    CompareJustFuzzyTitle,
    CompareJustNaiveTitle,
    CompareByLanguageCatBoostTitle
)
from entities.matchers import (
    FirstMatcher,
    FullMatcher,
    CatboostFullMatcher
)

from entities.metrics import (
    BinaryValidator,
    ReprezentData
)

from multiprocessing import Pool, cpu_count
from yamlparams.utils import Hparam

TitleEntitys = {"CompareByLanguageCatBoostTitle": CompareByLanguageCatBoostTitle,
                "CompareByLanguageFuzzyTitle": CompareByLanguageFuzzyTitle,
               "CompareJustFuzzyTitle": CompareJustFuzzyTitle,
               "CompareByLanguageNaiveTitle": CompareByLanguageNaiveTitle,
               "CompareJustFuzzyTitle": CompareJustFuzzyTitle
               }

MatcherEntitys = {"CatboostFullMatcher": CatboostFullMatcher,
                  "FirstMatcher": FirstMatcher,
                  "FullMatcher": FullMatcher
                  }



def match_mangas(source_df: pd.DataFrame,
                 target_df: pd.DataFrame,
                 target_df_name_columns: list,
                 target_df_name: str,
                 source_df_name_columns: list,
                 labels: list,
                 TitleEntity: Callable,
                 MatcherEntity: Callable):

    # create manga titles
    source_manga_names = list(
        source_df[source_df_name_columns].to_records(index=False))
    ids = source_df.index.tolist()

    gtitles = [TitleEntity(list(source_manga_names[i]),
                          meta={'index': ids[i]})
               for i in range(len(source_manga_names))]

    target_manga_names = list(
        target_df[target_df_name_columns].to_records(index=False))

    ids = target_df.index.tolist()
    mtitles = [TitleEntity(list(target_manga_names[i]),
                          meta={'index': ids[i]})
               for i in range(len(target_manga_names))]

    source_df.loc[:, f'{target_df_name}_id'] = None

    k = -1
    with Pool(cpu_count() - 1) as pool:
        matcher = MatcherEntity(mtitles)
        match_res = list(map(TitleEntity.check_names, gtitles,list(pool.imap(matcher.find_matches,
                                        gtitles[:k]))))
    return match_res



if __name__ == '__main__':
    print('run with config', sys.argv[1])
    config = Hparam(sys.argv[1])
    try:
        sep = config.target_df.separator
    except KeyError:
        sep = ','
    target_df = pd.read_csv(config.target_df.path, sep=sep)
    source_df = pd.read_csv(config.source_df.path, sep=';')
    labels = list(map(lambda x:x[0],
                        pd.read_csv(config.validate_df.path,
                                    sep=';').to_records(index = False)))

    for name_title in tqdm(TitleEntitys):
        for name_matcher in MatcherEntitys:

            predict_model = match_mangas(source_df,
                                            target_df,
                                            config.target_df.name_cols,
                                            config.target_df.name,
                                            config.source_df.name_cols,
                                            labels, TitleEntitys[name_title],
                                            MatcherEntitys[name_matcher])

            metrics = BinaryValidator.validate(labels[:len(predict_model)],
                                               predict_model)

            """Uncomment this if you still don't have this csv"""
            ReprezentData.create_csv(metrics,
                                     'data/models_results/' + name_title + name_matcher + ".csv")

            if name_title == "CompareByLanguageCatBoostTitle":
                MatcherEntitys.pop("CatboostFullMatcher")
                break


