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
    DataRepresenter
)

from multiprocessing import Pool, cpu_count
from yamlparams.utils import Hparam

TITLES = [CompareByLanguageCatBoostTitle,
          CompareByLanguageFuzzyTitle,
          CompareByLanguageNaiveTitle,
          CompareJustFuzzyTitle,
          CompareJustNaiveTitle
          ]

MATCHERS = [CatboostFullMatcher,
            FirstMatcher,
            FullMatcher
            ]


def match_mangas(source_df: pd.DataFrame, target_df: pd.DataFrame,
                 target_df_name_columns: list, source_df_name_columns: list,
                 title: Callable, matcher: Callable):

    # create manga TITLES
    source_manga_names = list(
        source_df[source_df_name_columns].to_records(index=False))
    ids = source_df.index.tolist()

    gtitles = [title(list(source_manga_names[i]), meta={'index': ids[i]})
               for i in range(len(source_manga_names))]

    target_manga_names = list(
        target_df[target_df_name_columns].to_records(index=False))

    ids = target_df.index.tolist()
    mtitles = [title(list(target_manga_names[i]), meta={'index': ids[i]})
               for i in range(len(target_manga_names))]

    with Pool(cpu_count() - 1) as pool:
        match_res = list(pool.imap(matcher(mtitles).find_matches, gtitles[:-1]))
    match_res = list(map(title.validate_titles, gtitles, match_res))
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
    labels = list(map(lambda x: x[0],
                      pd.read_csv(config.validate_df.path,
                      sep=';').to_records(index=False)))

    for title in tqdm(TITLES):
        for matcher in MATCHERS:
            titles_name = title.__name__
            matchers_name = matcher.__name__
            
            predict_model = match_mangas(source_df, target_df,
                                         config.target_df.name_cols,
                                         config.source_df.name_cols,
                                         title, matcher)

            metrics = BinaryValidator.validate(labels[:len(predict_model)],
                                               predict_model)

            """Uncomment this if you still don't have this csv"""
            # DataRepresenter.create_csv(metrics,
            #                            'data/models_results/' + titles_name + matchers_name + ".csv")
            DataRepresenter.add_metrics_to_csv(metrics,
                                               'data/models_results/' + titles_name + matchers_name + ".csv")

            if titles_name == "CompareByLanguageCatBoostTitle":
                MATCHERS.remove(CatboostFullMatcher)
                break
