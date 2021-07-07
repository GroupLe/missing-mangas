import pickle
from time import sleep
from selenium import webdriver
import pandas as pd
from tqdm import tqdm


def get_chapter_label(link):
    browser.get(f'https://remanga.org/manga/{link}?subpath=content')
    chapter_label = browser.find_elements_by_xpath(
        "//div[contains(@class, 'MuiTabs-flexContainer')]/button")[1].text
    return chapter_label


if __name__ == '__main__':
    options = webdriver.FirefoxOptions()
    options.binary_location = '/usr/bin/firefox'
    browser = webdriver.Firefox(executable_path='./geckodriver',
                                options=options)

    browser.get('https://remanga.org')
    sleep(1.0)
    btn = browser.find_element_by_xpath(
        "//button[@class='MuiButtonBase-root c26']")
    btn.click()

    login, psw = open('secret.txt').splitlines()
    browser.find_element_by_id("login").send_keys(login)
    browser.find_element_by_id("password").send_keys(psw)

    btn = browser.find_element_by_xpath(
        "//button[@class='MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-containedSizeLarge MuiButton-sizeLarge MuiButton-fullWidth']")
    btn.click()

    sleep(0.5)

    df = pd.read_csv('./data/remanga_catalog_mangas.csv')
    links = df[df.n_chapters.isna()].dir.tolist()
    chapters = []

    bar = tqdm(links)
    for link in bar:
        try:
            chapters.append(get_chapter_label(link))
        except Exception as e:
            chapters.append(None)
            print(e, 'on', link)

        sleep(0.1)

    pickle.dump(chapters, open('data/remanga_raw_18+_chapters.pkl', 'wb'))

    df.loc[df.n_chapters.isna(), 'n_chapters'] = chapters
    df.to_csv('data/remanga_catalog_full.csv', index=False)
