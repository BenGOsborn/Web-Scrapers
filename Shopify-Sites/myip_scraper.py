from seleniumwire import webdriver
import multiprocessing
import os
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests

def run_tor():
    os.system('tor.lnk')

def scrape_table(table_element):
    table_soup = BeautifulSoup(table_element.get_attribute('innerHTML'), features='html.parser')

    total_data = []

    rows = table_soup.find('tbody').find_all('tr')
    for i in range(0, len(rows), 2):
        try:
            url = rows[i].find_all('a')[1].text

            try:
                visitors_raw = rows[i + 1].find_all('div', {'class': 'sval'})[0].text
                visitors = float(visitors_raw.split(' ')[0].replace(',', ''))
            
            except:
                visitors = None

            try:
                raise Exception("Break me") # Remove this

                page_html = requests.get(f"http://{url}").text
                page_soup = BeautifulSoup(page_html, features='html.parser')
                title = page_soup.find('title').text

            except:
                title = None

            data = (title, url, visitors)
            total_data.append(data)

        except:
            pass

    return total_data

def main():
    p = multiprocessing.Process(target=run_tor)
    p.start()

    options = {'proxy': {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}}
    driver = webdriver.Chrome(seleniumwire_options=options)

    driver.get("https://myip.ms/browse/sites/1/ipID/23.227.38.32/ipIDii/23.227.38.32")

    carousel_html = driver.find_element_by_xpath('//*[@id="tabs-1"]/table[2]/tbody/tr/td/span/span[1]/table[1]/tbody/tr/td/div[1]/div')
    last_page = int(BeautifulSoup(carousel_html.get_attribute('innerHTML'), features='html.parser').find_all('a')[-1]['href'][1:])

    final_data = []

    csv_name = f"myip_leads_{time.time()}.csv"

    for i in range(20, last_page):
        try:
            element = driver.find_element_by_xpath(f'//a[@href="#{i + 1}"]').click()

            time.sleep(10)

            try:
                captcha = driver.find_element_by_xpath('//*[@id="captcha_submit"]')
                captcha.click()
                time.sleep(10)

            except:
                pass

            table = driver.find_element_by_xpath('//*[@id="sites_tbl"]')
            data = scrape_table(table)

            final_data += data

            df = pd.DataFrame(final_data, columns=['title', 'url', 'visitors'])
            df.to_csv(csv_name, index=False)

        except:
            pass
    
    driver.close()

    p.join()
    
if __name__ == '__main__':
    main()