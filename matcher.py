import sys
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from entities import CompareByLanguageFuzzyTitle, CompareByLanguageNaiveTitle,\
    CompareJustFuzzyTitle,  CompareJustNaiveTitle,  FirstMatcher, FullMatcher
from multiprocessing import Pool, cpu_count
from yamlparams.utils import Hparam


TitleEnity =  CompareJustFuzzyTitle
MatcherEntity = FullMatcher


def match_mangas(source_df: pd.DataFrame,
                 target_df: pd.DataFrame,
                 target_df_name_columns: list,
                 target_df_name: str,
                 source_df_name_columns: list):
    # create manga titles
    source_manga_names = list(
        source_df[source_df_name_columns].to_records(index=False))
    ids = source_df.index.tolist()

    gtitles = [TitleEnity(list(source_manga_names[i]),
                          meta={'index': ids[i]})
               for i in range(len(source_manga_names))]

    target_manga_names = list(
        target_df[target_df_name_columns].to_records(index=False))

    ids = target_df.index.tolist()
    mtitles = [TitleEnity(list(target_manga_names[i]),
                          meta={'index': ids[i]})
               for i in range(len(target_manga_names))]

    print('source titles n:', len(gtitles))
    print('target titles n:', len(mtitles))

    q_matches = []
    source_df.loc[:, f'{target_df_name}_id'] = None

    k = -1
    with Pool(cpu_count()-1) as pool:
        matcher = MatcherEntity(mtitles)
        match_res = list(tqdm(pool.imap(matcher.find_matches,
                                        gtitles[:k]), total=len(gtitles)))

    for gtitle, matched in tqdm(zip(gtitles[:k],
                                    match_res), total=len(gtitles)):
        i = gtitle.get_index()

        if len(matched) == 1:
            # if and only one2one corresponding found
            source_df.loc[i, f'{target_df_name}_id'] = matched[0].get_index()

        elif len(matched) > 1:
            for item in matched:
                source_df.loc[i, f'{target_df_name}_id'] = item.get_index()

        q_matches.append(len(matched))

    return {'q_matches': q_matches,
            'source_df': source_df,
            'matched': matched}


if __name__ == '__main__':
    print('run with config', sys.argv[1])
    config = Hparam(sys.argv[1])
    try:
        sep = config.target_df.separator
    except KeyError:
        sep = ','
    target_df = pd.read_csv(config.target_df.path, sep=sep)
    source_df = pd.read_csv(config.source_df.path, sep=';')

    res_soure_target = match_mangas(source_df,
                                    target_df,
                                    config.target_df.name_cols,
                                    config.target_df.name,
                                    config.source_df.name_cols)
    res_df = res_soure_target['source_df']
    res_df.to_csv(config.result.path, sep=';')

    plt.hist(res_soure_target['q_matches'], bins=100)
    plt.savefig(config.result.hist_path)
