import time
import requests
from decouple import config

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


class GetDataFromSourceMixin:
    main_div_css_selector = ".sc-978e9339-1"

    @staticmethod
    def get_rating_votes(page_source):
        rating_votes_css_selector = "sc-eb51e184-3 gUihYJ"
        rating_el = page_source.find("div", rating_votes_css_selector)
        rating_votes = rating_el.get_text(separator=" ", strip=True)
        if rating_votes[-1] == "K":
            rating_votes = float(rating_votes[:-1]) * 1000
        elif rating_votes[-1] == "M":
            rating_votes = float(rating_votes[:-1]) * 1000000
        return int(rating_votes)

    @staticmethod
    def get_title(page_source: BeautifulSoup):
        title_css_selector = ".hero__primary-text"
        title_span = page_source.select_one(title_css_selector)
        return title_span.get_text()

    def get_rating(self, page_source):
        rating_css_selector = "div.sc-3a4309f8-0:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > span:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > span:nth-child(1)"
        rating_div = page_source.select_one(rating_css_selector)
        return float(rating_div.get_text(separator=" ", strip=True))

    @staticmethod
    def get_top_cast(page_source):
        top_cast_section = page_source.find(attrs={
            "cel_widget_id": "StaticFeature_Cast"
        })
        if not top_cast_section:
            return []
        name_links = top_cast_section.find_all("a", class_="sc-bfec09a1-1 gCQkeh")
        names = [
            name_link.get_text(separator=" ", strip=True)
            for name_link in name_links
        ]
        return names

    @staticmethod
    def get_countries(page_source: BeautifulSoup):
        country_section = page_source.find(attrs={
            "data-testid": "title-details-origin"
        })
        if not country_section:
            return []
        countries_links = country_section.find_all("a")
        countries = [
            country_link.get_text(separator=" ", strip=True)
            for country_link in countries_links
        ]
        return countries

    @staticmethod
    def get_languages(page_source: BeautifulSoup):
        language_section = page_source.find(attrs={
            "data-testid": "title-details-languages"
        })
        if not language_section:
            return []
        languages_links = language_section.find_all("a")
        languages = [
            language_link.get_text(separator=" ", strip=True)
            for language_link in languages_links
        ]
        return languages

    @staticmethod
    def get_similar(page_source: BeautifulSoup):
        similar_section = page_source.find(attrs={
            "cel_widget_id": "StaticFeature_MoreLikeThis"
        })
        if not similar_section:
            return []
        similar_parent_div = similar_section.find("div", class_="ipc-sub-grid ipc-sub-grid--page-span-2 ipc-sub-grid--nowrap ipc-shoveler__grid")
        similar_child_divs = similar_parent_div.find_all("div", recursive=False)
        similar_spans = [
            similar_div.select_one("a:nth-child(3) > span:nth-child(1)")
            for similar_div in similar_child_divs
        ]
        similars = [
            similar_span.get_text(separator=" ", strip=True)
            for similar_span in similar_spans
        ]
        return similars


class ImdbMovieScrapper(GetDataFromSourceMixin):
    def __init__(self, title_type="feature", release_data="2010-01-01") -> None:
        option = Options()
        option.profile = config("PROFILE_PATH")
        service = Service(config("DRIVER_PATH"))
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




