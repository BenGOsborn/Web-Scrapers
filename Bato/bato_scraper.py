from selenium.webdriver import Chrome
import os
from time import sleep
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self):
        driver_path = os.path.join(os.getcwd(), "chromedriver")
        self.__driver = Chrome(executable_path=driver_path)
        self.__ROOT_URL = "https://bato.to"

        self.__items = []

    def collect_items(self):
        for i in range(1426): # Number of pages to scrape
            url = f"https://bato.to/browse?page={i+1}"
            self.__driver.get(url)

            soup = BeautifulSoup(self.__driver.page_source, features="html.parser")

            items = soup.find_all('div', {'class': 'col item line-b is-hot no-flag'})
            for i, item in enumerate(items):
                element = item.find('a', {'class': 'item-title'})
                title = element.text
                link = element['href']
                print(f"Manga {i + 1}: {title} | {self.__ROOT_URL}{link}")

            break

    def close(self):
        self.__driver.close()

if __name__ == "__main__":
    bot = Scraper()
    bot.collect_items()
    bot.close()