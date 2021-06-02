from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep

def main():
    SEARCH = "site:myshopify.com fashion"
    URL = f"https://www.google.com/search?q={SEARCH.replace(' ', '+')}"

    NUM_PAGES = 500

    lead_urls = []
    leads = []

    driver = webdriver.Chrome()
    driver.get(URL)
    sleep(1.25)

    while True: 
        try:
            raw_html = driver.find_element_by_xpath('//*[@id="gsr"]').get_attribute('innerHTML')

        except:
            print("Captcha error, please complete the CAPTCHA before continuing")
            sleep(120)
            continue

        soup = BeautifulSoup(raw_html, 'html.parser')

        divs = soup.find_all('div', {'class': 'yuRUbf'})

        for div in divs:
            try:
                a = div.find('a')

                href = a['href']
                headline = a.find('h3').text

                if href not in lead_urls:
                    lead_urls.append(href)
                    leads.append((headline, href))

            except Exception as e:
                print(f"Encountered error '{e}' - DIV.")

        try:
            driver.find_element_by_xpath('//*[@id="pnnext"]').click()
        
        except:
            print("Finished scraping!")
            break

    driver.close()

    df = pd.DataFrame(leads, columns=['headline', 'url'])
    df.to_csv('google_leads.csv', index=False)

if __name__ == '__main__':
    main()