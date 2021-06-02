import requests
import os
import time
import multiprocessing
from bs4 import BeautifulSoup
import pandas as pd

import requests_html

def run_tor():
    os.system('tor.lnk')

def get_page_html(url, headers=None, data=None):
    proxies = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}

    p = multiprocessing.Process(target=run_tor)
    p.start()

    session = requests_html.HTMLSession()
    res = session.post(url=url, proxies=proxies, headers=headers, data=data)

    # I want this to only occur if there is an instance of it though
    captcha_btn = res.html.find('#captcha_submit', first=True)

    res.html.render(sleep=2)
    raw_html = res.html.raw_html
    session.close()

    os.system("taskkill /F /IM tor.exe")
    p.join()

    return raw_html

def scrape_page(page_num):
    url = f"https://myip.ms/ajax_table/sites/{page_num}/ipID/23.227.38.32/ipIDii/23.227.38.32"
    headers = {'Host': 'myip.ms', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0', 'Accept': 'text/html, */*; q=0.01', 'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br', 'Referer': 'https://myip.ms/browse/sites/1/ipID/23.227.38.32/ipIDii/23.227.38.32', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest', 'Content-Length': '19', 'Origin': 'https://myip.ms', 'Connection': 'close', # keep-alive
                'Cookie': 's2_csrf_cookie_name=d8bdfff3be5f0fe1893db49274674d0a; sw=68.3; sh=88.3; _ga=GA1.2.1134855039.1617256442; _gid=GA1.2.631515582.1617256442; PHPSESSID=1uiqdecpf9hpkftji99pj3lbci; GoogleAdServingTest=Good; __gads=ID=2a8dfc9de7c33462-22c54dd542a7000d:T=1617256448:RT=1617256448:S=ALNI_MZIq0EuZ2QQhfAhBW8H0C_NcM0YvA; s2_uGoo=182c623db8733c3cffa5d1861647db87ced798c1; s2_csrf_cookie_name=d8bdfff3be5f0fe1893db49274674d0a; s2_uLang=en; s2_theme_ui=red'}
    data = {'getpage': 'yes', 'lang': 'en'}

    raw_html = get_page_html(url, headers=headers, data=data)

    soup = BeautifulSoup(raw_html, features='html.parser')

    print(soup.prettify())

    data = []

    rows = soup.find_all('tr')
    for i in range(0, len(rows), 2):
        try:
            url = rows[i].find_all('a')[0].text

            visitors_raw = rows[i + 1].find_all('div', {'class': 'sval'})[0].text
            visitors = float(visitors_raw.split(' ')[0].replace(',', ''))

            data.append((url, visitors))
            
        except:
            pass

    return data

def main():
    total_data = []

    csv_name = f"myip_leads_{time.time()}.csv"

    i = int(input("Please enter the page number you wish to start scraping from (Set 1 for first page): "))
    threshold = 0

    while True:
        try:
            print(f"Scraping page {i}...")

            data = scrape_page(i)

            if len(data) == 0:
                threshold += 1

                if threshold == 3:
                    break
                
                continue

            total_data += data

            df = pd.DataFrame(total_data, columns=['url', 'visitors'])
            df.to_csv(csv_name, index=False)

            time.sleep(2)
        
        except Exception as e:
            print(f"Encountered exception '{e}'.")


        i += 1

if __name__ == '__main__':
    main()