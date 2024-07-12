import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


class ImdbMovieScrapper:
    def __init__(self) -> None:
        self.base_url = "https://www.imdb.com/search/title/"
        option = Options()
        option.profile = '/home/mate/snap/firefox/common/.mozilla/firefox/fb0aec67.default'
        service = Service('/snap/bin/geckodriver')
        self.driver = webdriver.Firefox(service=service, options=option)
    
    
    def get_url(self, title="feature", release_date="2010-01-01"):
        _sort_query_string = "sort=release_date,asc"
        return f"{self.base_url}?title_type={title}&release_date={release_date}&{_sort_query_string}"


    def load_all_movies(self):
        time.sleep(5)
        load_more_data_css_selector = 'button.ipc-btn.ipc-btn--single-padding.ipc-btn--center-align-content.ipc-btn--default-height.ipc-btn--core-base.ipc-btn--theme-base.ipc-btn--on-accent2.ipc-btn--rounded.ipc-text-button.ipc-see-more__button'
        while True:
            elements = self.driver.find_elements(By.CSS_SELECTOR, load_more_data_css_selector)
            print(elements)
            if not elements:
                break
            wait = WebDriverWait(self.driver, 10)
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_data_css_selector)))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(2)
            button.click()

    def run(self):
        self.driver.get(self.get_url())
        self.load_all_movies()
        data = self.get_movies_data()
        cleaned_data = self.validate_data(data)
        # augmented_data = self.augment_data(cleaned_data)
        self.save_data()

    @staticmethod
    def scape_url(url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.content  # Returns the raw HTML content
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return None

    def get_movies_data(self):
        page_source = self.driver.page_source
        page_source = BeautifulSoup(page_source, 'html.parser')
        ul_css_selector = 'ipc-metadata-list ipc-metadata-list--dividers-between sc-748571c8-0 jmWPOZ detailed-list-view ipc-metadata-list--base'
        ul_element = page_source.find('ul', class_=ul_css_selector)
        links = ul_element.find_all('a')
        hrefs = [link.get('href') for link in links]
        for href in hrefs:
            full_url = requests.compat.urljoin(self.base_url, href)
            page_source = self.scape_url(full_url)
            if page_source:
                page_source = BeautifulSoup(page_source, 'html.parser')
                print(page_source.title.get_text())
        print("List of links:", hrefs)


if "__main__" == __name__:
    ImdbMovieScrapper().run()




